"""
Input-output network analysis.

This module provides tools for analyzing input-output (I-O) networks, including:
- Leontief inverse calculation
- Economic multipliers (output, employment, income, value-added)
- Sectoral linkages (backward/forward)
- Key sector identification
- Value chain analysis
"""

from typing import Any, Dict, List, Literal, Optional, Tuple

import networkx as nx
import numpy as np
import pandas as pd

from krl_network.core.base import NetworkConfig
from krl_network.core.exceptions import ComputationError, DataError, InvalidNetworkError
from krl_network.core.result import NetworkResult, add_metric
from krl_network.networks.base_economic import BaseEconomicNetwork


class InputOutputNetwork(BaseEconomicNetwork):
    """Input-output network for sectoral analysis.

    This class models input-output relationships between economic sectors and provides:
    - I-O table processing (NAICS, commodity flows, MR IO)
    - Leontief inverse calculation
    - Economic multipliers (output, employment, income, value-added)
    - Sectoral linkages (backward/forward)
    - Key sector identification
    - Value chain analysis
    """

    def __init__(
        self, config: Optional[NetworkConfig] = None, metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize input-output network.

        Args:
            config: Network configuration (defaults to directed, weighted, self_loops=True)
            metadata: I-O metadata (classification, year, region, etc.)
        """
        # Default to directed, weighted network with self-loops allowed
        if config is None:
            config = NetworkConfig(directed=True, weighted=True, self_loops=True)

        super().__init__(config, metadata)

        # I-O specific attributes
        self.technical_coefficients: Optional[pd.DataFrame] = None  # A matrix
        self.leontief_inverse: Optional[pd.DataFrame] = None  # (I-A)^-1
        self.final_demand: Optional[pd.Series] = None
        self.total_output: Optional[pd.Series] = None
        self.value_added: Optional[pd.Series] = None

    @classmethod
    def from_io_table(
        cls,
        io_table: pd.DataFrame,
        sector_row: str,
        sector_col: List[str],
        total_output: Optional[pd.Series] = None,
        final_demand: Optional[pd.Series] = None,
        value_added: Optional[pd.Series] = None,
        **kwargs,
    ) -> "InputOutputNetwork":
        """Create I-O network from input-output table.

        Args:
            io_table: DataFrame with I-O transactions (sectors as rows)
            sector_row: Column name containing sector names
            sector_col: List of column names for sector transactions
            total_output: Optional total output by sector
            final_demand: Optional final demand by sector
            value_added: Optional value added by sector
            **kwargs: Additional arguments for InputOutputNetwork

        Returns:
            InputOutputNetwork instance

        Raises:
            DataError: If required columns are missing
        """
        network = cls(**kwargs)

        # Validate required columns (but allow empty DataFrame)
        required_cols = [sector_row] + sector_col
        if not io_table.empty:
            network.validate_economic_data(io_table, required_cols)

        # Store economic data
        if total_output is not None:
            network.total_output = total_output
        if final_demand is not None:
            network.final_demand = final_demand
        if value_added is not None:
            network.value_added = value_added

        # Add nodes first (all sectors)
        sectors = io_table[sector_row].tolist()
        for sector in sectors:
            if sector not in network.graph:
                network.graph.add_node(sector)

        # Add edges for non-zero flows
        for _, row in io_table.iterrows():
            from_sector = row[sector_row]

            for to_sector in sector_col:
                value = float(row[to_sector]) if pd.notna(row[to_sector]) else 0.0

                if value > 0:
                    network.add_edge(from_sector, to_sector, weight=value)

        return network

    def from_dataframe(
        self,
        df: pd.DataFrame,
        source_col: str = "source",
        target_col: str = "target",
        weight_col: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Build I-O network from DataFrame.

        Args:
            df: DataFrame with edge data
            source_col: Column name for source sectors
            target_col: Column name for target sectors
            weight_col: Optional column for transaction values
            **kwargs: Additional edge attributes
        """
        self.validate_economic_data(df, [source_col, target_col])

        for _, row in df.iterrows():
            source = row[source_col]
            target = row[target_col]
            weight = (
                float(row[weight_col])
                if weight_col and weight_col in df.columns and pd.notna(row[weight_col])
                else 1.0
            )

            edge_attrs = {"weight": weight}
            for key, value in kwargs.items():
                if key in df.columns:
                    edge_attrs[key] = row[key]

            self.add_edge(source, target, **edge_attrs)

    def calculate_technical_coefficients(
        self, total_output: Optional[pd.Series] = None
    ) -> pd.DataFrame:
        """Calculate technical coefficients matrix (A matrix).

        A_ij = intermediate input from i to j / total output of j

        Args:
            total_output: Total output by sector (if None, calculated from network)

        Returns:
            DataFrame with technical coefficients (A matrix)
        """
        sectors = list(self.graph.nodes())
        n = len(sectors)

        # Initialize A matrix
        A = pd.DataFrame(0.0, index=sectors, columns=sectors)

        # Use provided total output or calculate
        if total_output is None:
            total_output = pd.Series(0.0, index=sectors)
            for sector in sectors:
                # Total output = sum of all sales (outgoing edges)
                total_output[sector] = sum(
                    self.graph[sector][dest]["weight"] for dest in self.graph.successors(sector)
                )

        self.total_output = total_output

        # Calculate technical coefficients
        for from_sector in sectors:
            # Check successors including self-loops
            successors = list(self.graph.successors(from_sector))

            for to_sector in successors:
                intermediate_input = self.graph[from_sector][to_sector]["weight"]
                output = total_output[to_sector] if to_sector in total_output.index else 0

                if output > 0:
                    A.loc[from_sector, to_sector] = intermediate_input / output

        self.technical_coefficients = A
        return A

    def calculate_leontief_inverse(
        self, technical_coefficients: Optional[pd.DataFrame] = None
    ) -> pd.DataFrame:
        """Calculate Leontief inverse matrix: (I-A)^-1.

        Args:
            technical_coefficients: A matrix (if None, uses stored)

        Returns:
            Leontief inverse matrix

        Raises:
            ComputationError: If matrix is singular
        """
        if technical_coefficients is None:
            technical_coefficients = self.technical_coefficients

        if technical_coefficients is None or technical_coefficients.empty:
            raise ComputationError("Technical coefficients not calculated")

        # Calculate I - A
        I = np.eye(len(technical_coefficients))
        I_minus_A = I - technical_coefficients.values

        # Calculate inverse
        try:
            leontief_inv = np.linalg.inv(I_minus_A)
        except np.linalg.LinAlgError:
            raise ComputationError("Singular matrix: cannot compute Leontief inverse")

        # Convert to DataFrame
        L = pd.DataFrame(
            leontief_inv, index=technical_coefficients.index, columns=technical_coefficients.columns
        )

        self.leontief_inverse = L
        return L

    def calculate_output_multipliers(
        self, leontief_inverse: Optional[pd.DataFrame] = None
    ) -> Dict[Any, float]:
        """Calculate output multipliers.

        Output multiplier = sum of column in Leontief inverse
        Shows total output generated per unit of final demand

        Args:
            leontief_inverse: Leontief inverse (if None, uses stored)

        Returns:
            Dictionary of output multipliers by sector
        """
        if leontief_inverse is None:
            leontief_inverse = self.leontief_inverse

        if leontief_inverse is None:
            raise ComputationError("Leontief inverse not calculated")

        # Column sums
        multipliers = leontief_inverse.sum(axis=0)
        return multipliers.to_dict()

    def calculate_backward_linkages(self) -> Dict[Any, float]:
        """Calculate backward linkages (input intensity).

        Backward linkage = sum of column in A matrix (normalized)
        High value indicates sector purchases many inputs

        Returns:
            Dictionary of backward linkage indices by sector

        Raises:
            ComputationError: If technical coefficients not calculated
        """
        if self.technical_coefficients is None or self.technical_coefficients.empty:
            raise ComputationError("Technical coefficients must be calculated first")

        # Sum of each column (inputs purchased)
        linkages = self.technical_coefficients.sum(axis=0)

        # Normalize by mean (Hirschman-Rasmussen index)
        mean_linkage = linkages.mean()
        if mean_linkage > 0:
            linkages = linkages / mean_linkage

        return linkages.to_dict()

    def calculate_forward_linkages(self) -> Dict[Any, float]:
        """Calculate forward linkages (output distribution).

        Forward linkage = sum of row in A matrix (normalized)
        High value indicates sector sells to many sectors

        Returns:
            Dictionary of forward linkage indices by sector

        Raises:
            ComputationError: If technical coefficients not calculated
        """
        if self.technical_coefficients is None or self.technical_coefficients.empty:
            raise ComputationError("Technical coefficients must be calculated first")

        # Sum of each row (outputs sold)
        linkages = self.technical_coefficients.sum(axis=1)

        # Normalize by mean
        mean_linkage = linkages.mean()
        if mean_linkage > 0:
            linkages = linkages / mean_linkage

        return linkages.to_dict()

    def identify_key_sectors(self, threshold: float = 1.0) -> Dict[str, Any]:
        """Identify key sectors based on linkages.

        Classifies sectors into 4 categories:
        - key_sectors: High backward AND forward linkages
        - backward_oriented: High backward, low forward
        - forward_oriented: Low backward, high forward
        - weak_linkage: Low both

        Args:
            threshold: Threshold for "high" linkage (default 1.0 = average)

        Returns:
            Dictionary with sector classifications and linkage values
        """
        backward = self.calculate_backward_linkages()
        forward = self.calculate_forward_linkages()

        key_sectors = []
        backward_oriented = []
        forward_oriented = []
        weak_linkage = []

        for sector in backward.keys():
            b = backward[sector]
            f = forward[sector]

            if b >= threshold and f >= threshold:
                key_sectors.append(sector)
            elif b >= threshold:
                backward_oriented.append(sector)
            elif f >= threshold:
                forward_oriented.append(sector)
            else:
                weak_linkage.append(sector)

        return {
            "key_sectors": key_sectors,
            "backward_oriented": backward_oriented,
            "forward_oriented": forward_oriented,
            "weak_linkage": weak_linkage,
            "backward_linkages": backward,
            "forward_linkages": forward,
        }

    def calculate_employment_multipliers(
        self, employment_coefficients: pd.Series, leontief_inverse: pd.DataFrame
    ) -> Dict[Any, float]:
        """Calculate employment multipliers.

        Employment multiplier_j = sum_i(e_i × L_ij)
        where e = employment per unit output, L = Leontief inverse

        Shows total employment generated by one unit of final demand in sector j

        Args:
            employment_coefficients: Employment per unit output by sector
            leontief_inverse: Leontief inverse matrix

        Returns:
            Dictionary of employment multipliers (total employment per unit final demand)
        """
        # Ensure all sectors are included
        sectors = leontief_inverse.columns
        employment_vec = pd.Series(0.0, index=sectors)
        for sector in employment_coefficients.index:
            if sector in sectors:
                employment_vec[sector] = employment_coefficients[sector]

        # Calculate multipliers: L @ e (each row of L dotted with e)
        # For sector j: sum_i(L_ij * e_i) = total employment from 1 unit final demand in j
        employment_mult = leontief_inverse.values @ employment_vec.values

        return dict(zip(sectors, employment_mult))

    def calculate_value_added_multipliers(
        self, value_added_coefficients: pd.Series, leontief_inverse: pd.DataFrame
    ) -> Dict[Any, float]:
        """Calculate value-added multipliers.

        Value-added multiplier_j = sum_i(v_i × L_ij)
        where v = value added per unit output, L = Leontief inverse

        Shows total value added generated by one unit of final demand in sector j

        Args:
            value_added_coefficients: Value added per unit output by sector
            leontief_inverse: Leontief inverse matrix

        Returns:
            Dictionary of value-added multipliers (total VA per unit final demand)
        """
        # Ensure all sectors are included
        sectors = leontief_inverse.columns
        va_vec = pd.Series(0.0, index=sectors)
        for sector in value_added_coefficients.index:
            if sector in sectors:
                va_vec[sector] = value_added_coefficients[sector]

        # Calculate multipliers: L @ v
        va_mult = leontief_inverse.values @ va_vec.values

        return dict(zip(sectors, va_mult))

    def trace_production_chain(
        self, sector: Any, max_hops: int = 5, min_share: float = 0.01
    ) -> Dict[int, List[Tuple[Any, float]]]:
        """Trace production chain (suppliers by tier).

        Args:
            sector: Target sector
            max_hops: Maximum supply chain tiers to trace
            min_share: Minimum technical coefficient to include

        Returns:
            Dictionary mapping tier number to list of (supplier, share) tuples
        """
        if self.technical_coefficients is None or self.technical_coefficients.empty:
            return {}

        chain = {}
        visited = set()
        current_tier = [sector]

        for tier in range(1, max_hops + 1):
            next_tier = []
            tier_suppliers = []

            for s in current_tier:
                if s not in self.technical_coefficients.columns:
                    continue

                # Find suppliers (rows with positive coefficients in column s)
                suppliers = self.technical_coefficients[s]
                suppliers = suppliers[suppliers > min_share]

                for supplier, coef in suppliers.items():
                    if supplier not in visited and supplier != sector:
                        tier_suppliers.append((supplier, float(coef)))
                        next_tier.append(supplier)
                        visited.add(supplier)

            if tier_suppliers:
                chain[tier] = sorted(tier_suppliers, key=lambda x: x[1], reverse=True)

            if not next_tier:
                break

            current_tier = next_tier

        return chain

    def calculate_import_dependency(
        self, import_shares: pd.Series, leontief_inverse: Optional[pd.DataFrame] = None
    ) -> Dict[Any, float]:
        """Calculate total import dependency (direct + indirect).

        Import dependency_j = sum_i(L_ji × m_i)
        where m = import share vector (imports/total supply by sector)

        Shows total import content in sector j's output

        Args:
            import_shares: Direct import share by sector
            leontief_inverse: Optional Leontief inverse (uses stored if None)

        Returns:
            Dictionary of total import dependency by sector
        """
        if leontief_inverse is None:
            leontief_inverse = self.leontief_inverse

        if leontief_inverse is None:
            raise ComputationError("Leontief inverse not calculated")

        # Ensure all sectors included
        sectors = leontief_inverse.columns
        import_vec = pd.Series(0.0, index=sectors)
        for sector in import_shares.index:
            if sector in sectors:
                import_vec[sector] = import_shares[sector]

        # Calculate total import content: L @ m (matrix times column vector)
        # For sector j: sum_i(L_ji * m_i) = row j dotted with m
        import_dep = leontief_inverse.values @ import_vec.values

        return dict(zip(sectors, import_dep))

    def assess_io_structure(
        self, include_multipliers: bool = True, include_linkages: bool = True
    ) -> NetworkResult:
        """Comprehensive I-O structure assessment.

        Args:
            include_multipliers: Include multiplier calculations
            include_linkages: Include linkage analysis and key sectors

        Returns:
            NetworkResult with I-O metrics
        """
        result = self.export_economic_metrics(include_nodes=True, include_edges=True)

        # Network-level metrics
        add_metric(result, "num_sectors", self.graph.number_of_nodes())
        add_metric(result, "num_transactions", self.graph.number_of_edges())

        # Output multipliers
        if include_multipliers and self.leontief_inverse is not None:
            try:
                multipliers = self.calculate_output_multipliers()
                add_metric(result, "avg_output_multiplier", np.mean(list(multipliers.values())))
                add_metric(result, "max_output_multiplier", np.max(list(multipliers.values())))
                result.metadata["output_multipliers"] = multipliers
            except Exception:
                pass

        # Linkages and key sectors
        if include_linkages and self.technical_coefficients is not None:
            try:
                sectors = self.identify_key_sectors()
                add_metric(result, "num_key_sectors", len(sectors["key_sectors"]))
                result.metadata["key_sectors"] = sectors["key_sectors"]
                result.metadata["backward_oriented"] = sectors["backward_oriented"]
                result.metadata["forward_oriented"] = sectors["forward_oriented"]
            except Exception:
                pass

        return result
