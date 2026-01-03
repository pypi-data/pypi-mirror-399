"""
Supply chain network analysis.

This module provides tools for analyzing supply chain networks, including:
- Critical supplier identification
- Bottleneck detection
- Shock propagation simulation
- Risk assessment
"""

from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np
import pandas as pd

from krl_network.core.base import NetworkConfig
from krl_network.core.exceptions import ComputationError, DataError, InvalidNetworkError
from krl_network.core.result import NetworkResult, add_metric
from krl_network.networks.base_economic import BaseEconomicNetwork


class SupplyChainNetwork(BaseEconomicNetwork):
    """Supply chain network for risk and resilience analysis.

    This class models supply chain relationships and provides methods for:
    - Building networks from shipment data or bills of materials
    - Identifying critical suppliers and bottlenecks
    - Analyzing redundancy and alternative paths
    - Simulating supply shocks and cascading failures
    """

    def __init__(
        self, config: Optional[NetworkConfig] = None, metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize supply chain network.

        Args:
            config: Network configuration (defaults to directed, weighted)
            metadata: Supply chain metadata (industry, time period, etc.)
        """
        # Default to directed, weighted network
        if config is None:
            config = NetworkConfig(directed=True, weighted=True)

        super().__init__(config, metadata)

        # Supply chain specific attributes
        self.tiers: Dict[Any, int] = {}  # Node tier levels
        self.lead_times: Dict[Tuple[Any, Any], float] = {}  # Edge lead times

    @classmethod
    def from_shipment_data(
        cls,
        df: pd.DataFrame,
        supplier_col: str = "supplier",
        buyer_col: str = "buyer",
        volume_col: Optional[str] = None,
        lead_time_col: Optional[str] = None,
        **kwargs,
    ) -> "SupplyChainNetwork":
        """Create supply chain network from shipment data.

        Args:
            df: DataFrame with shipment records
            supplier_col: Column name for supplier
            buyer_col: Column name for buyer
            volume_col: Optional column for shipment volume (used as weight)
            lead_time_col: Optional column for lead time
            **kwargs: Additional arguments for SupplyChainNetwork

        Returns:
            SupplyChainNetwork instance

        Raises:
            DataError: If required columns are missing
        """
        network = cls(**kwargs)

        # Validate columns
        required = [supplier_col, buyer_col]
        network.validate_economic_data(df, required)

        # Add edges
        for _, row in df.iterrows():
            supplier = row[supplier_col]
            buyer = row[buyer_col]

            # Calculate weight (volume or count)
            if volume_col and volume_col in df.columns and pd.notna(row[volume_col]):
                weight = float(row[volume_col])
            else:
                weight = 1.0

            # Add edge
            if network.graph.has_edge(supplier, buyer):
                # Aggregate weights for multiple shipments
                network.graph[supplier][buyer]["weight"] += weight
            else:
                network.add_edge(supplier, buyer, weight=weight)

            # Store lead time if provided
            if lead_time_col and lead_time_col in df.columns:
                lead_time = row[lead_time_col]
                network.lead_times[(supplier, buyer)] = lead_time

        return network

    @classmethod
    def from_bom(
        cls,
        df: pd.DataFrame,
        parent_col: str = "parent",
        component_col: str = "component",
        quantity_col: Optional[str] = None,
        **kwargs,
    ) -> "SupplyChainNetwork":
        """Create supply chain network from bill of materials (BOM).

        Args:
            df: DataFrame with BOM records
            parent_col: Column name for parent item
            component_col: Column name for component item
            quantity_col: Optional column for component quantity
            **kwargs: Additional arguments for SupplyChainNetwork

        Returns:
            SupplyChainNetwork instance

        Raises:
            DataError: If required columns are missing
        """
        network = cls(**kwargs)

        # Validate columns
        required = [parent_col, component_col]
        network.validate_economic_data(df, required)

        # Add edges (component -> parent)
        for _, row in df.iterrows():
            parent = row[parent_col]
            component = row[component_col]

            # Use quantity as weight
            if quantity_col and quantity_col in df.columns and pd.notna(row[quantity_col]):
                weight = float(row[quantity_col])
            else:
                weight = 1.0

            network.add_edge(component, parent, weight=weight)

        return network

    def from_dataframe(
        self,
        df: pd.DataFrame,
        source_col: str = "source",
        target_col: str = "target",
        weight_col: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Build supply chain network from DataFrame.

        Args:
            df: DataFrame with edge data
            source_col: Column name for source nodes
            target_col: Column name for target nodes
            weight_col: Optional column for edge weights
            **kwargs: Additional edge attributes
        """
        # Use from_shipment_data for supply chain networks
        # This is a compatibility method for the BaseNetwork interface
        self.validate_economic_data(df, [source_col, target_col])

        for _, row in df.iterrows():
            source = row[source_col]
            target = row[target_col]
            weight = row[weight_col] if weight_col and weight_col in df.columns else 1.0

            # Add edge with attributes
            edge_attrs = {"weight": weight}
            for key, value in kwargs.items():
                if key in df.columns:
                    edge_attrs[key] = row[key]

            self.add_edge(source, target, **edge_attrs)

    def calculate_tiers(self, end_products: Optional[List[Any]] = None) -> Dict[Any, int]:
        """Calculate tier levels in supply chain.

        Tier 0: End products (final customers)
        Tier 1: Direct suppliers to end products
        Tier 2: Suppliers to tier 1, etc.

        Args:
            end_products: List of end product nodes (if None, uses nodes with no successors)

        Returns:
            Dictionary mapping nodes to tier levels

        Raises:
            InvalidNetworkError: If network is not directed
        """
        if not self.config.directed:
            raise InvalidNetworkError("Tier calculation requires directed network")

        # Identify end products
        if end_products is None:
            end_products = [n for n in self.graph.nodes() if self.graph.out_degree(n) == 0]

        if not end_products:
            raise ComputationError("No end products found (nodes with no outgoing edges)")

        # BFS backward from end products
        tiers = {}
        for product in end_products:
            if product not in self.graph:
                continue
            tiers[product] = 0

        # Process by tier
        current_tier = 0
        while True:
            current_nodes = [n for n, t in tiers.items() if t == current_tier]
            if not current_nodes:
                break

            # Find predecessors (suppliers)
            next_tier_nodes = set()
            for node in current_nodes:
                for supplier in self.graph.predecessors(node):
                    if supplier not in tiers:
                        next_tier_nodes.add(supplier)

            if not next_tier_nodes:
                break

            # Assign tier
            for node in next_tier_nodes:
                tiers[node] = current_tier + 1

            current_tier += 1

        self.tiers = tiers
        return tiers

    def identify_critical_suppliers(
        self, method: str = "betweenness", top_k: int = 10
    ) -> pd.DataFrame:
        """Identify critical suppliers in supply chain.

        Critical suppliers are those whose disruption would most impact the network.

        Args:
            method: Criticality method (betweenness, degree, pagerank, tier)
            top_k: Number of top suppliers to return

        Returns:
            DataFrame with supplier, criticality score, and tier
        """
        if method == "tier":
            # Tier-based criticality
            if not self.tiers:
                self.calculate_tiers()

            df = pd.DataFrame(
                [
                    {"node": node, "tier": tier, "criticality": 1.0 / (tier + 1)}
                    for node, tier in self.tiers.items()
                ]
            )
            df = df.sort_values("criticality", ascending=False)
            df["rank"] = range(1, len(df) + 1)
            return df.head(top_k).reset_index(drop=True)
        else:
            # Use centrality-based method
            return self.identify_critical_nodes(method=method, top_k=top_k)

    def detect_bottlenecks(
        self, capacity_attr: str = "weight", flow_fraction: float = 0.8
    ) -> pd.DataFrame:
        """Detect bottlenecks in supply chain.

        Bottlenecks are edges or nodes where capacity constraints could impede flow.

        Args:
            capacity_attr: Edge attribute representing capacity
            flow_fraction: Fraction of capacity considered "bottleneck" (0.8 = 80% capacity)

        Returns:
            DataFrame with bottleneck edges, capacity, and utilization
        """
        bottlenecks = []

        # Edge-based bottlenecks
        for u, v, data in self.graph.edges(data=True):
            capacity = data.get(capacity_attr, 1.0)

            # Calculate potential flow through edge
            # Simple heuristic: number of paths using this edge
            try:
                # Count shortest paths through edge
                num_paths = sum(
                    1
                    for s in self.graph.nodes()
                    for t in self.graph.nodes()
                    if s != t
                    and nx.has_path(self.graph, s, t)
                    and (u, v)
                    in zip(
                        nx.shortest_path(self.graph, s, t)[:-1],
                        nx.shortest_path(self.graph, s, t)[1:],
                    )
                )
            except:
                num_paths = 0

            # Estimate utilization (normalized by degree)
            out_degree = self.graph.out_degree(u) if self.config.directed else self.graph.degree(u)
            utilization = num_paths / (out_degree * len(self.graph)) if out_degree > 0 else 0

            if utilization >= flow_fraction:
                bottlenecks.append(
                    {
                        "source": u,
                        "target": v,
                        "capacity": capacity,
                        "utilization": round(utilization, 3),
                        "paths_through": num_paths,
                    }
                )

        if not bottlenecks:
            return pd.DataFrame(
                columns=["source", "target", "capacity", "utilization", "paths_through"]
            )

        df = pd.DataFrame(bottlenecks)
        return df.sort_values("utilization", ascending=False).reset_index(drop=True)

    def analyze_redundancy(self, source: Any, target: Any, max_paths: int = 5) -> Dict[str, Any]:
        """Analyze redundancy between source and target nodes.

        Identifies alternative paths and assesses supply chain resilience.

        Args:
            source: Source node
            target: Target node
            max_paths: Maximum number of paths to find

        Returns:
            Dictionary with paths, lengths, and redundancy score

        Raises:
            InvalidNetworkError: If source or target not in network
        """
        if source not in self.graph:
            raise InvalidNetworkError(f"Source node {source} not in network")
        if target not in self.graph:
            raise InvalidNetworkError(f"Target node {target} not in network")

        # Find all simple paths (up to max_paths)
        try:
            all_paths = list(
                nx.all_simple_paths(self.graph, source, target, cutoff=len(self.graph))
            )
            paths = all_paths[:max_paths]
        except nx.NetworkXNoPath:
            return {"num_paths": 0, "paths": [], "path_lengths": [], "redundancy_score": 0.0}

        # Calculate path lengths
        path_lengths = [len(p) - 1 for p in paths]

        # Redundancy score based on number and diversity of paths
        num_paths = len(paths)
        length_diversity = np.std(path_lengths) if len(path_lengths) > 1 else 0

        # Score: more paths and diverse lengths = higher redundancy
        redundancy_score = min(num_paths / 5.0, 1.0) * (1 + 0.1 * length_diversity)

        return {
            "num_paths": num_paths,
            "paths": [list(p) for p in paths],
            "path_lengths": path_lengths,
            "shortest_path_length": min(path_lengths) if path_lengths else None,
            "longest_path_length": max(path_lengths) if path_lengths else None,
            "redundancy_score": round(redundancy_score, 3),
        }

    def calculate_dependency_score(self, node: Any, include_indirect: bool = True) -> float:
        """Calculate dependency score for a node.

        Measures how many downstream nodes depend on this supplier.

        Args:
            node: Node to calculate dependency for
            include_indirect: Include indirect dependencies (default: True)

        Returns:
            Dependency score (0-1, higher = more nodes depend on this)
        """
        if node not in self.graph:
            return 0.0

        if not self.config.directed:
            # For undirected, use degree centrality
            return self.graph.degree(node) / (len(self.graph) - 1) if len(self.graph) > 1 else 0

        # Count reachable downstream nodes
        if include_indirect:
            # All nodes reachable from this node
            reachable = len(nx.descendants(self.graph, node))
        else:
            # Only direct successors
            reachable = self.graph.out_degree(node)

        # Normalize by total nodes
        max_reachable = len(self.graph) - 1
        dependency = reachable / max_reachable if max_reachable > 0 else 0

        return round(dependency, 3)

    def simulate_supply_shock(
        self,
        disrupted_nodes: List[Any],
        propagation_threshold: float = 0.5,
        max_iterations: int = 10,
    ) -> Dict[str, Any]:
        """Simulate supply shock propagation through network.

        Models cascading failures when suppliers are disrupted.

        Args:
            disrupted_nodes: Initially disrupted nodes
            propagation_threshold: Fraction of inputs needed to continue operation
            max_iterations: Maximum propagation iterations

        Returns:
            Dictionary with disrupted nodes by iteration and impact metrics
        """
        if not self.config.directed:
            raise InvalidNetworkError("Shock simulation requires directed network")

        # Initialize
        disrupted = set(disrupted_nodes)
        disruption_waves = {0: list(disrupted)}

        # Propagate shock
        for iteration in range(1, max_iterations + 1):
            new_disruptions = set()

            for node in self.graph.nodes():
                if node in disrupted:
                    continue

                # Check if node has sufficient inputs
                predecessors = list(self.graph.predecessors(node))
                if not predecessors:
                    continue

                # Count disrupted suppliers
                disrupted_suppliers = sum(1 for p in predecessors if p in disrupted)
                disruption_fraction = disrupted_suppliers / len(predecessors)

                # Node fails if too many suppliers disrupted
                if disruption_fraction >= propagation_threshold:
                    new_disruptions.add(node)

            if not new_disruptions:
                break

            disrupted.update(new_disruptions)
            disruption_waves[iteration] = list(new_disruptions)

        # Calculate impact metrics
        total_disrupted = len(disrupted)
        total_nodes = len(self.graph)
        impact_fraction = total_disrupted / total_nodes if total_nodes > 0 else 0

        return {
            "initial_disruptions": disrupted_nodes,
            "total_disrupted": total_disrupted,
            "impact_fraction": round(impact_fraction, 3),
            "num_waves": len(disruption_waves),
            "disruption_waves": disruption_waves,
            "final_disrupted": list(disrupted),
        }

    def assess_supply_chain_risk(self) -> NetworkResult:
        """Comprehensive supply chain risk assessment.

        Returns:
            NetworkResult with network-level and node-level risk metrics
        """
        result = self.export_economic_metrics(include_nodes=True, include_edges=True)

        # Network-level risk metrics
        add_metric(result, "avg_degree", np.mean(list(dict(self.graph.degree()).values())))

        # Calculate tiers if not already done
        if not self.tiers:
            try:
                self.calculate_tiers()
                add_metric(result, "max_tier", max(self.tiers.values()) if self.tiers else 0)
            except:
                add_metric(result, "max_tier", 0)

        # Identify critical suppliers
        critical = self.identify_critical_suppliers(method="betweenness", top_k=10)
        result.metadata["critical_suppliers"] = critical.to_dict("records")

        # Detect bottlenecks
        bottlenecks = self.detect_bottlenecks()
        add_metric(result, "num_bottlenecks", len(bottlenecks))
        result.metadata["bottlenecks"] = (
            bottlenecks.to_dict("records") if len(bottlenecks) > 0 else []
        )

        # Node-level risk scores
        if result.nodes is not None and len(result.nodes) > 0:
            result.nodes["dependency_score"] = result.nodes["node"].apply(
                lambda x: self.calculate_dependency_score(x)
            )

        return result
