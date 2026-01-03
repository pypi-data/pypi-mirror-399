"""
International trade network analysis.

This module provides tools for analyzing international trade networks, including:
- Bilateral trade flows
- Trade structure (blocs, PTAs, regional integration)
- Comparative advantage (RCA, export similarity)
- Network evolution over time
- Trade diversification
"""

from typing import Any, Dict, List, Literal, Optional, Tuple

import networkx as nx
import numpy as np
import pandas as pd

from krl_network.core.base import NetworkConfig
from krl_network.core.exceptions import ComputationError, DataError, InvalidNetworkError
from krl_network.core.result import NetworkResult, add_metric
from krl_network.networks.base_economic import BaseEconomicNetwork


class TradeNetwork(BaseEconomicNetwork):
    """International trade network for trade analysis.

    This class models bilateral trade relationships and provides:
    - Trade flow construction (exports/imports)
    - Trade balance and openness
    - Comparative advantage (RCA)
    - Export similarity and product space
    - Trade bloc identification
    - Network evolution analysis
    """

    def __init__(
        self, config: Optional[NetworkConfig] = None, metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize trade network.

        Args:
            config: Network configuration (defaults to directed, weighted, self_loops=True)
            metadata: Trade metadata (year, products, data source, etc.)
        """
        # Default to directed, weighted network with self-loops for re-exports
        if config is None:
            config = NetworkConfig(directed=True, weighted=True, self_loops=True)

        super().__init__(config, metadata)

        # Trade-specific attributes
        self.product_classification: Optional[str] = None  # HS, SITC, etc.
        self.trade_year: Optional[int] = None

    @classmethod
    def from_trade_data(
        cls,
        df: pd.DataFrame,
        exporter_col: str = "exporter",
        importer_col: str = "importer",
        value_col: str = "value",
        product_col: Optional[str] = None,
        year_col: Optional[str] = None,
        aggregate_products: bool = True,
        **kwargs,
    ) -> "TradeNetwork":
        """Create trade network from bilateral trade data.

        Args:
            df: DataFrame with trade records
            exporter_col: Column name for exporting country
            importer_col: Column name for importing country
            value_col: Column name for trade value
            product_col: Optional column for product classification
            year_col: Optional column for year
            aggregate_products: If True, aggregate across products
            **kwargs: Additional arguments for TradeNetwork

        Returns:
            TradeNetwork instance

        Raises:
            DataError: If required columns are missing
        """
        network = cls(**kwargs)

        # Validate columns
        required = [exporter_col, importer_col, value_col]
        network.validate_economic_data(df, required)

        # Filter by product/year if specified
        df_filtered = df.copy()

        if year_col and year_col in df.columns:
            # Take most recent year if multiple
            latest_year = df_filtered[year_col].max()
            df_filtered = df_filtered[df_filtered[year_col] == latest_year]
            network.trade_year = latest_year

        # Add edges (exports from exporter to importer)
        if aggregate_products or product_col is None:
            # Aggregate all products
            trade_flows = (
                df_filtered.groupby([exporter_col, importer_col])[value_col].sum().reset_index()
            )

            for _, row in trade_flows.iterrows():
                exporter = row[exporter_col]
                importer = row[importer_col]
                value = float(row[value_col]) if pd.notna(row[value_col]) else 0.0

                if value > 0:
                    if network.graph.has_edge(exporter, importer):
                        network.graph[exporter][importer]["weight"] += value
                    else:
                        network.add_edge(exporter, importer, weight=value)
        else:
            # Keep products separate in metadata
            for _, row in df_filtered.iterrows():
                exporter = row[exporter_col]
                importer = row[importer_col]
                value = float(row[value_col]) if pd.notna(row[value_col]) else 0.0
                product = row[product_col] if product_col and product_col in df.columns else None

                if value > 0:
                    # Store product in edge data (add after edge creation)
                    if network.graph.has_edge(exporter, importer):
                        # Accumulate if edge exists
                        network.graph[exporter][importer]["weight"] += value
                        if "products" not in network.graph[exporter][importer]:
                            network.graph[exporter][importer]["products"] = []
                        if product:
                            network.graph[exporter][importer]["products"].append(product)
                    else:
                        # Add edge first, then add product attributes
                        network.add_edge(exporter, importer, weight=value)
                        if product:
                            network.graph[exporter][importer]["product"] = product
                            network.graph[exporter][importer]["products"] = [product]

        return network

    def from_dataframe(
        self,
        df: pd.DataFrame,
        source_col: str = "source",
        target_col: str = "target",
        weight_col: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Build trade network from DataFrame.

        Args:
            df: DataFrame with edge data
            source_col: Column name for exporting countries
            target_col: Column name for importing countries
            weight_col: Optional column for trade values
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

    def calculate_trade_balance(self) -> Dict[Any, float]:
        """Calculate trade balance for each country.

        Trade balance = exports - imports

        Returns:
            Dictionary mapping countries to trade balance
        """
        balance = {}

        for country in self.graph.nodes():
            exports = sum(
                self.graph[country][dest]["weight"]
                for dest in self.graph.successors(country)
                if country != dest  # Exclude self-loops
            )
            imports = sum(
                self.graph[src][country]["weight"]
                for src in self.graph.predecessors(country)
                if src != country  # Exclude self-loops
            )
            balance[country] = exports - imports

        return balance

    def calculate_trade_openness(self, gdp: Optional[pd.Series] = None) -> Dict[Any, float]:
        """Calculate trade openness for each country.

        Trade openness = (exports + imports) / GDP

        Args:
            gdp: GDP by country (if None, uses normalized trade volume)

        Returns:
            Dictionary mapping countries to openness ratio
        """
        openness = {}

        for country in self.graph.nodes():
            exports = sum(
                self.graph[country][dest]["weight"] for dest in self.graph.successors(country)
            )
            imports = sum(
                self.graph[src][country]["weight"] for src in self.graph.predecessors(country)
            )
            total_trade = exports + imports

            if gdp is not None and country in gdp.index:
                openness[country] = total_trade / gdp[country] if gdp[country] > 0 else 0.0
            else:
                # Normalize by max trade
                max_trade = max(
                    sum(self.graph[c][d]["weight"] for d in self.graph.successors(c))
                    + sum(self.graph[s][c]["weight"] for s in self.graph.predecessors(c))
                    for c in self.graph.nodes()
                )
                openness[country] = total_trade / max_trade if max_trade > 0 else 0.0

        return openness

    def calculate_revealed_comparative_advantage(
        self,
        product_data: pd.DataFrame,
        country_col: str = "country",
        product_col: str = "product",
        export_col: str = "exports",
    ) -> pd.DataFrame:
        """Calculate Revealed Comparative Advantage (RCA) indices.

        RCA_ij = (X_ij / X_i) / (X_j / X_world)
        where:
        - X_ij = exports of product j by country i
        - X_i = total exports by country i
        - X_j = world exports of product j
        - X_world = total world exports

        RCA > 1 indicates comparative advantage

        Args:
            product_data: DataFrame with country-product-exports
            country_col: Column for country
            product_col: Column for product
            export_col: Column for export values

        Returns:
            DataFrame with RCA indices (countries × products)
        """
        # Calculate totals
        country_exports = product_data.groupby(country_col)[export_col].sum()
        product_exports = product_data.groupby(product_col)[export_col].sum()
        world_exports = product_data[export_col].sum()

        # Calculate RCA for each country-product pair
        rca_data = []
        for _, row in product_data.iterrows():
            country = row[country_col]
            product = row[product_col]
            exports = row[export_col]

            # RCA = (X_ij / X_i) / (X_j / X_world)
            share_in_country = (
                exports / country_exports[country] if country_exports[country] > 0 else 0
            )
            share_in_world = product_exports[product] / world_exports if world_exports > 0 else 0

            rca = share_in_country / share_in_world if share_in_world > 0 else 0

            rca_data.append(
                {"country": country, "product": product, "rca": rca, "has_advantage": rca > 1}
            )

        return pd.DataFrame(rca_data)

    def calculate_export_similarity(
        self,
        product_data: pd.DataFrame,
        country_col: str = "country",
        product_col: str = "product",
        export_col: str = "exports",
        method: Literal["cosine", "correlation"] = "cosine",
    ) -> pd.DataFrame:
        """Calculate export similarity between countries.

        Measures how similar countries' export baskets are.

        Args:
            product_data: DataFrame with country-product-exports
            country_col: Column for country
            product_col: Column for product
            export_col: Column for export values
            method: Similarity method (cosine or correlation)

        Returns:
            DataFrame with pairwise export similarity (countries × countries)
        """
        # Create country-product matrix
        export_matrix = product_data.pivot_table(
            index=country_col, columns=product_col, values=export_col, fill_value=0
        )

        countries = export_matrix.index.tolist()
        n = len(countries)

        # Calculate similarity
        similarity = pd.DataFrame(0.0, index=countries, columns=countries)

        for i, country_i in enumerate(countries):
            for j, country_j in enumerate(countries):
                if i == j:
                    similarity.loc[country_i, country_j] = 1.0
                else:
                    vec_i = export_matrix.loc[country_i].values
                    vec_j = export_matrix.loc[country_j].values

                    if method == "cosine":
                        # Cosine similarity
                        dot_product = np.dot(vec_i, vec_j)
                        norm_i = np.linalg.norm(vec_i)
                        norm_j = np.linalg.norm(vec_j)
                        sim = dot_product / (norm_i * norm_j) if norm_i > 0 and norm_j > 0 else 0
                    else:  # correlation
                        # Pearson correlation
                        sim = np.corrcoef(vec_i, vec_j)[0, 1] if len(vec_i) > 1 else 0
                        sim = max(0, sim)  # Clip negative correlations

                    similarity.loc[country_i, country_j] = sim

        return similarity

    def identify_trade_blocs(
        self,
        method: Literal["modularity", "threshold"] = "modularity",
        threshold: Optional[float] = None,
    ) -> Dict[Any, int]:
        """Identify trade blocs (communities of highly interconnected traders).

        Args:
            method: Identification method
                - modularity: Community detection (Louvain)
                - threshold: Countries with trade > threshold
            threshold: Trade value threshold for threshold method

        Returns:
            Dictionary mapping countries to bloc IDs
        """
        if method == "modularity":
            try:
                import networkx.algorithms.community as nx_comm

                # Convert to undirected for community detection
                G_undirected = self.graph.to_undirected()
                communities = nx_comm.louvain_communities(G_undirected, weight="weight")

                blocs = {}
                for bloc_id, community in enumerate(communities):
                    for country in community:
                        blocs[country] = bloc_id

                return blocs
            except ImportError:
                raise ComputationError("Community detection requires NetworkX >= 2.5")

        elif method == "threshold":
            if threshold is None:
                # Use median trade value as threshold
                trade_values = [data["weight"] for _, _, data in self.graph.edges(data=True)]
                threshold = np.median(trade_values) if trade_values else 0

            # Create subgraph of high-value trade
            strong_trade = nx.DiGraph()
            for u, v, data in self.graph.edges(data=True):
                if data["weight"] >= threshold:
                    strong_trade.add_edge(u, v, **data)

            # Add isolated nodes to ensure all countries are included
            for node in self.graph.nodes():
                if node not in strong_trade:
                    strong_trade.add_node(node)

            # Find weakly connected components
            components = list(nx.weakly_connected_components(strong_trade))
            blocs = {}
            for bloc_id, component in enumerate(components):
                for country in component:
                    blocs[country] = bloc_id

            return blocs

        return {}

    def calculate_trade_diversification(
        self, measure: Literal["hhi", "entropy", "count"] = "hhi"
    ) -> Dict[Any, float]:
        """Calculate trade diversification for each country.

        Args:
            measure: Diversification measure
                - hhi: Herfindahl-Hirschman Index (lower = more diversified)
                - entropy: Shannon entropy (higher = more diversified)
                - count: Number of trading partners

        Returns:
            Dictionary mapping countries to diversification scores
        """
        diversification = {}

        for country in self.graph.nodes():
            # Get export destinations and values
            exports = {
                dest: self.graph[country][dest]["weight"] for dest in self.graph.successors(country)
            }

            if not exports:
                diversification[country] = 0.0
                continue

            total_exports = sum(exports.values())
            shares = {dest: val / total_exports for dest, val in exports.items()}

            if measure == "hhi":
                # HHI = sum of squared shares (0-1, lower is more diversified)
                hhi = sum(share**2 for share in shares.values())
                diversification[country] = hhi

            elif measure == "entropy":
                # Shannon entropy (higher is more diversified)
                entropy = -sum(
                    share * np.log(share) if share > 0 else 0 for share in shares.values()
                )
                diversification[country] = entropy

            elif measure == "count":
                # Number of trading partners
                diversification[country] = len(exports)

        return diversification

    def analyze_trade_evolution(
        self,
        previous_network: "TradeNetwork",
        metrics: List[str] = ["growth", "stability", "new_partners"],
    ) -> Dict[str, Any]:
        """Analyze trade network evolution over time.

        Args:
            previous_network: Trade network from earlier time period
            metrics: List of evolution metrics to calculate

        Returns:
            Dictionary with evolution metrics
        """
        evolution = {}

        if "growth" in metrics:
            # Calculate trade growth
            growth = {}
            for country in self.graph.nodes():
                current_exports = sum(
                    self.graph[country][dest]["weight"] for dest in self.graph.successors(country)
                )

                if country in previous_network.graph:
                    previous_exports = sum(
                        previous_network.graph[country][dest]["weight"]
                        for dest in previous_network.graph.successors(country)
                    )
                    growth[country] = (
                        (current_exports - previous_exports) / previous_exports
                        if previous_exports > 0
                        else 0
                    )
                else:
                    growth[country] = 1.0  # New trader

            evolution["growth"] = growth

        if "stability" in metrics:
            # Calculate partner stability (Jaccard similarity)
            stability = {}
            for country in self.graph.nodes():
                current_partners = set(self.graph.successors(country))

                if country in previous_network.graph:
                    previous_partners = set(previous_network.graph.successors(country))

                    if current_partners or previous_partners:
                        intersection = len(current_partners & previous_partners)
                        union = len(current_partners | previous_partners)
                        stability[country] = intersection / union if union > 0 else 0
                    else:
                        stability[country] = 1.0
                else:
                    stability[country] = 0.0  # New country

            evolution["stability"] = stability

        if "new_partners" in metrics:
            # Count new trading partners
            new_partners = {}
            for country in self.graph.nodes():
                current_partners = set(self.graph.successors(country))

                if country in previous_network.graph:
                    previous_partners = set(previous_network.graph.successors(country))
                    new_partners[country] = len(current_partners - previous_partners)
                else:
                    new_partners[country] = len(current_partners)

            evolution["new_partners"] = new_partners

        return evolution

    def assess_trade_structure(
        self,
        include_balance: bool = True,
        include_blocs: bool = True,
        include_diversification: bool = True,
    ) -> NetworkResult:
        """Comprehensive trade structure assessment.

        Args:
            include_balance: Include trade balance analysis
            include_blocs: Include trade bloc identification
            include_diversification: Include diversification metrics

        Returns:
            NetworkResult with trade metrics
        """
        result = self.export_economic_metrics(include_nodes=True, include_edges=True)

        # Network-level metrics
        add_metric(result, "num_countries", self.graph.number_of_nodes())
        add_metric(result, "num_trade_flows", self.graph.number_of_edges())

        if self.trade_year:
            add_metric(result, "trade_year", self.trade_year)

        # Trade balance
        if include_balance:
            try:
                balance = self.calculate_trade_balance()
                result.metadata["trade_balance"] = balance

                surplus_countries = sum(1 for b in balance.values() if b > 0)
                add_metric(result, "num_surplus_countries", surplus_countries)
            except Exception:
                pass

        # Trade openness
        try:
            openness = self.calculate_trade_openness()
            add_metric(result, "avg_trade_openness", np.mean(list(openness.values())))
            result.metadata["trade_openness"] = openness
        except Exception:
            pass

        # Trade blocs
        if include_blocs:
            try:
                blocs = self.identify_trade_blocs()
                add_metric(result, "num_trade_blocs", len(set(blocs.values())))
                result.metadata["trade_blocs"] = blocs
            except Exception:
                pass

        # Diversification
        if include_diversification:
            try:
                diversification = self.calculate_trade_diversification(measure="hhi")
                add_metric(result, "avg_hhi", np.mean(list(diversification.values())))
                result.metadata["trade_diversification"] = diversification
            except Exception:
                pass

        return result
