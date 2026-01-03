"""
Regional economic network analysis.

This module provides tools for analyzing regional economic networks, including:
- Trade flows between regions
- Labor market connections
- Economic integration and spillovers
- Core-periphery structure
"""

from typing import Any, Dict, List, Literal, Optional, Set, Tuple

import networkx as nx
import numpy as np
import pandas as pd

from krl_network.core.base import NetworkConfig
from krl_network.core.exceptions import ComputationError, DataError, InvalidNetworkError
from krl_network.core.result import NetworkResult, add_metric
from krl_network.networks.base_economic import BaseEconomicNetwork


class RegionalNetwork(BaseEconomicNetwork):
    """Regional economic network for spatial analysis.

    This class models economic relationships between geographic regions and provides:
    - Multiple network types (trade, labor, migration, spillovers)
    - Economic integration measurement
    - Core-periphery analysis
    - Spatial weighting (distance, contiguity, gravity)
    - Regional clustering
    """

    # Network type constants
    NETWORK_TYPES = ["trade", "labor", "migration", "commuting", "spillover"]

    def __init__(
        self,
        network_type: str = "trade",
        config: Optional[NetworkConfig] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Initialize regional network.

        Args:
            network_type: Type of regional network (trade, labor, migration, commuting, spillover)
            config: Network configuration (defaults to directed, weighted)
            metadata: Regional metadata (regions, time period, data source, etc.)

        Raises:
            DataError: If network_type is invalid
        """
        if network_type not in self.NETWORK_TYPES:
            raise DataError(
                f"Invalid network_type: {network_type}. " f"Must be one of {self.NETWORK_TYPES}"
            )

        # Default to directed, weighted network
        if config is None:
            config = NetworkConfig(directed=True, weighted=True)

        super().__init__(config, metadata)

        self.network_type = network_type
        self.region_attributes: Dict[Any, Dict[str, Any]] = {}  # Region-level data
        self.spatial_weights: Dict[Tuple[Any, Any], float] = {}  # Distance/contiguity

    @classmethod
    def from_flow_data(
        cls,
        df: pd.DataFrame,
        origin_col: str = "origin",
        destination_col: str = "destination",
        flow_col: str = "flow",
        network_type: str = "trade",
        bidirectional: bool = False,
        **kwargs,
    ) -> "RegionalNetwork":
        """Create regional network from flow data.

        Args:
            df: DataFrame with flow records (origin, destination, flow)
            origin_col: Column name for origin region
            destination_col: Column name for destination region
            flow_col: Column name for flow value (trade, workers, migrants, etc.)
            network_type: Type of regional network
            bidirectional: If True, create undirected edges with total flow
            **kwargs: Additional arguments for RegionalNetwork

        Returns:
            RegionalNetwork instance

        Raises:
            DataError: If required columns are missing
        """
        network = cls(network_type=network_type, **kwargs)

        # Validate columns
        required = [origin_col, destination_col, flow_col]
        network.validate_economic_data(df, required)

        # Add edges
        for _, row in df.iterrows():
            origin = row[origin_col]
            destination = row[destination_col]
            flow = float(row[flow_col]) if pd.notna(row[flow_col]) else 0.0

            if bidirectional:
                # For bidirectional, aggregate both directions
                if network.graph.has_edge(origin, destination):
                    network.graph[origin][destination]["weight"] += flow
                elif network.graph.has_edge(destination, origin):
                    network.graph[destination][origin]["weight"] += flow
                else:
                    network.add_edge(origin, destination, weight=flow)
            else:
                # Directed flow
                if network.graph.has_edge(origin, destination):
                    network.graph[origin][destination]["weight"] += flow
                else:
                    network.add_edge(origin, destination, weight=flow)

        return network

    def from_dataframe(
        self,
        df: pd.DataFrame,
        source_col: str = "source",
        target_col: str = "target",
        weight_col: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Build regional network from DataFrame.

        Args:
            df: DataFrame with edge data
            source_col: Column name for source regions
            target_col: Column name for target regions
            weight_col: Optional column for edge weights
            **kwargs: Additional edge attributes
        """
        # Use from_flow_data for regional networks
        self.validate_economic_data(df, [source_col, target_col])

        for _, row in df.iterrows():
            source = row[source_col]
            target = row[target_col]
            weight = (
                float(row[weight_col])
                if weight_col and weight_col in df.columns and pd.notna(row[weight_col])
                else 1.0
            )

            # Add edge with attributes
            edge_attrs = {"weight": weight}
            for key, value in kwargs.items():
                if key in df.columns:
                    edge_attrs[key] = row[key]

            self.add_edge(source, target, **edge_attrs)

    def set_region_attributes(self, region: Any, attributes: Dict[str, Any]) -> None:
        """Set attributes for a region.

        Args:
            region: Region identifier
            attributes: Dictionary of region attributes (GDP, population, etc.)
        """
        if region not in self.graph:
            raise InvalidNetworkError(f"Region {region} not in network")

        self.region_attributes[region] = attributes
        # Also set as node attributes
        for key, value in attributes.items():
            self.graph.nodes[region][key] = value

    def set_spatial_weights(
        self,
        weights_df: pd.DataFrame,
        region1_col: str = "region1",
        region2_col: str = "region2",
        weight_col: str = "weight",
    ) -> None:
        """Set spatial weights (distance, contiguity, etc.).

        Args:
            weights_df: DataFrame with spatial weights
            region1_col: Column for first region
            region2_col: Column for second region
            weight_col: Column for weight value
        """
        for _, row in weights_df.iterrows():
            r1 = row[region1_col]
            r2 = row[region2_col]
            weight = float(row[weight_col]) if pd.notna(row[weight_col]) else 0.0
            self.spatial_weights[(r1, r2)] = weight
            # Symmetric for undirected spatial relationships
            self.spatial_weights[(r2, r1)] = weight

    def calculate_integration_index(
        self, method: Literal["trade", "flow", "connectivity"] = "trade"
    ) -> Dict[Any, float]:
        """Calculate economic integration index for each region.

        Integration measures how connected a region is to the broader economy.

        Args:
            method: Integration calculation method
                - trade: Trade intensity (exports + imports / GDP)
                - flow: Total flow relative to region size
                - connectivity: Network connectivity measures

        Returns:
            Dictionary mapping regions to integration scores (0-1)
        """
        integration = {}

        if method == "trade" and self.network_type == "trade":
            # Trade integration: (exports + imports) / GDP
            for region in self.graph.nodes():
                exports = sum(
                    self.graph[region][dest]["weight"] for dest in self.graph.successors(region)
                )
                imports = sum(
                    self.graph[src][region]["weight"] for src in self.graph.predecessors(region)
                )
                total_trade = exports + imports

                # Get GDP if available
                gdp = self.region_attributes.get(region, {}).get("gdp", 1.0)
                integration[region] = min(total_trade / gdp, 1.0) if gdp > 0 else 0.0

        elif method == "flow":
            # Flow integration: total flow strength
            for region in self.graph.nodes():
                out_flow = sum(
                    self.graph[region][dest]["weight"] for dest in self.graph.successors(region)
                )
                in_flow = sum(
                    self.graph[src][region]["weight"] for src in self.graph.predecessors(region)
                )
                total_flow = out_flow + in_flow

                # Normalize by max flow
                max_flow = (
                    max(
                        sum(self.graph[r][d]["weight"] for d in self.graph.successors(r))
                        + sum(self.graph[s][r]["weight"] for s in self.graph.predecessors(r))
                        for r in self.graph.nodes()
                    )
                    if self.graph.number_of_nodes() > 0
                    else 1.0
                )

                integration[region] = total_flow / max_flow if max_flow > 0 else 0.0

        elif method == "connectivity":
            # Connectivity integration: degree centrality
            from krl_network.metrics.centrality import degree_centrality

            integration = degree_centrality(self.graph, normalized=True)

        return integration

    def identify_core_periphery(
        self,
        method: Literal["degree", "flow", "eigenvector"] = "degree",
        core_threshold: float = 0.6,
    ) -> Dict[str, List[Any]]:
        """Identify core and periphery regions.

        Core regions are highly connected hubs; periphery regions are less connected.

        Args:
            method: Method for identifying core
                - degree: Based on degree centrality
                - flow: Based on total flow volume
                - eigenvector: Based on eigenvector centrality
            core_threshold: Threshold for classifying core (0-1)

        Returns:
            Dictionary with 'core' and 'periphery' lists of regions
        """
        from krl_network.metrics.centrality import degree_centrality, eigenvector_centrality

        # Calculate scores
        if method == "degree":
            scores = degree_centrality(self.graph, normalized=True)
        elif method == "flow":
            scores = {}
            for region in self.graph.nodes():
                out_flow = sum(
                    self.graph[region][dest]["weight"] for dest in self.graph.successors(region)
                )
                in_flow = sum(
                    self.graph[src][region]["weight"] for src in self.graph.predecessors(region)
                )
                scores[region] = out_flow + in_flow

            # Normalize
            max_score = max(scores.values()) if scores else 1.0
            scores = {r: s / max_score for r, s in scores.items()}

        elif method == "eigenvector":
            scores = eigenvector_centrality(self.graph)

        # Classify core/periphery
        core = [r for r, s in scores.items() if s >= core_threshold]
        periphery = [r for r, s in scores.items() if s < core_threshold]

        return {"core": core, "periphery": periphery, "scores": scores}

    def calculate_regional_spillovers(
        self,
        shock_region: Any,
        shock_magnitude: float = 1.0,
        spillover_decay: float = 0.5,
        max_hops: int = 3,
    ) -> Dict[Any, float]:
        """Calculate spillover effects from a regional shock.

        Models how economic shocks propagate through regional connections.

        Args:
            shock_region: Region experiencing initial shock
            shock_magnitude: Magnitude of initial shock
            spillover_decay: Decay rate for spillovers (0-1)
            max_hops: Maximum number of hops for spillover propagation

        Returns:
            Dictionary mapping regions to spillover magnitudes
        """
        if shock_region not in self.graph:
            raise InvalidNetworkError(f"Shock region {shock_region} not in network")

        spillovers = {shock_region: shock_magnitude}
        visited = {shock_region}
        current_wave = {shock_region: shock_magnitude}

        # Propagate spillovers
        for hop in range(max_hops):
            next_wave = {}

            for region, magnitude in current_wave.items():
                # Propagate to neighbors
                for neighbor in self.graph.successors(region):
                    if neighbor not in visited:
                        # Calculate spillover based on connection strength
                        edge_weight = self.graph[region][neighbor]["weight"]
                        total_weight = sum(
                            self.graph[region][n]["weight"] for n in self.graph.successors(region)
                        )

                        # Spillover proportional to connection strength and decays
                        spillover = magnitude * (edge_weight / total_weight) * spillover_decay

                        if neighbor in next_wave:
                            next_wave[neighbor] = max(next_wave[neighbor], spillover)
                        else:
                            next_wave[neighbor] = spillover

                        visited.add(neighbor)

            # Update spillovers
            spillovers.update(next_wave)
            current_wave = next_wave

            if not current_wave:
                break

        return spillovers

    def calculate_market_access(
        self, use_distance: bool = True, distance_decay: float = 1.0
    ) -> Dict[Any, float]:
        """Calculate market access for each region.

        Market access measures the potential for economic interaction,
        weighted by distance or network proximity.

        Args:
            use_distance: Whether to use spatial weights (distance)
            distance_decay: Decay parameter for distance (higher = more decay)

        Returns:
            Dictionary mapping regions to market access scores
        """
        market_access = {}

        for region in self.graph.nodes():
            access = 0.0

            for other_region in self.graph.nodes():
                if region == other_region:
                    continue

                # Get market size (GDP or population)
                market_size = self.region_attributes.get(other_region, {}).get("gdp", 1.0)

                if use_distance and (region, other_region) in self.spatial_weights:
                    # Distance-weighted access
                    distance = self.spatial_weights[(region, other_region)]
                    if distance > 0:
                        access += market_size / (distance**distance_decay)
                    else:
                        access += market_size  # No distance penalty
                else:
                    # Network distance (shortest path)
                    try:
                        path_length = nx.shortest_path_length(self.graph, region, other_region)
                        access += market_size / (path_length**distance_decay)
                    except nx.NetworkXNoPath:
                        pass  # No path, no access

            market_access[region] = access

        return market_access

    def identify_regional_clusters(
        self,
        method: Literal["modularity", "flow", "spatial"] = "modularity",
        n_clusters: Optional[int] = None,
    ) -> Dict[Any, int]:
        """Identify regional economic clusters.

        Args:
            method: Clustering method
                - modularity: Community detection (Louvain)
                - flow: Flow-based clustering
                - spatial: Spatial contiguity clustering
            n_clusters: Target number of clusters (optional)

        Returns:
            Dictionary mapping regions to cluster IDs
        """
        if method == "modularity":
            # Use Louvain community detection
            try:
                import networkx.algorithms.community as nx_comm

                # Convert to undirected for community detection
                G_undirected = self.graph.to_undirected()
                communities = nx_comm.louvain_communities(G_undirected, weight="weight")

                # Map regions to cluster IDs
                clusters = {}
                for cluster_id, community in enumerate(communities):
                    for region in community:
                        clusters[region] = cluster_id

                return clusters
            except ImportError:
                raise ComputationError("Community detection requires NetworkX >= 2.5")

        elif method == "flow":
            # Flow-based clustering using k-means on flow patterns
            flow_vectors = []
            regions = list(self.graph.nodes())

            for region in regions:
                # Create flow vector (out-flows to all regions)
                vector = np.zeros(len(regions))
                for i, target in enumerate(regions):
                    if self.graph.has_edge(region, target):
                        vector[i] = self.graph[region][target]["weight"]
                flow_vectors.append(vector)

            # Simple k-means (or use predefined if n_clusters not specified)
            if n_clusters is None:
                n_clusters = min(5, len(regions))

            # Use hierarchical clustering for simplicity
            from scipy.cluster.hierarchy import fcluster, linkage
            from scipy.spatial.distance import pdist

            if len(flow_vectors) > 1:
                distances = pdist(flow_vectors, metric="euclidean")
                linkage_matrix = linkage(distances, method="ward")
                cluster_labels = fcluster(linkage_matrix, n_clusters, criterion="maxclust")
                return {region: int(label) for region, label in zip(regions, cluster_labels)}
            else:
                return {regions[0]: 1} if regions else {}

        elif method == "spatial":
            # Spatial contiguity clustering
            if not self.spatial_weights:
                raise DataError("Spatial weights required for spatial clustering")

            # Build contiguity graph
            contiguity_graph = nx.Graph()
            for (r1, r2), weight in self.spatial_weights.items():
                if weight > 0:  # Contiguous
                    contiguity_graph.add_edge(r1, r2)

            # Find connected components (spatially contiguous clusters)
            components = nx.connected_components(contiguity_graph)
            clusters = {}
            for cluster_id, component in enumerate(components):
                for region in component:
                    clusters[region] = cluster_id

            return clusters

        return {}

    def calculate_trade_balance(self) -> Dict[Any, float]:
        """Calculate trade balance for each region.

        Trade balance = exports - imports

        Returns:
            Dictionary mapping regions to trade balance values
        """
        if self.network_type != "trade":
            raise InvalidNetworkError("Trade balance only applicable for trade networks")

        balance = {}
        for region in self.graph.nodes():
            exports = sum(
                self.graph[region][dest]["weight"] for dest in self.graph.successors(region)
            )
            imports = sum(
                self.graph[src][region]["weight"] for src in self.graph.predecessors(region)
            )
            balance[region] = exports - imports

        return balance

    def assess_regional_risk(
        self, include_integration: bool = True, include_clustering: bool = True
    ) -> NetworkResult:
        """Comprehensive regional economic risk assessment.

        Args:
            include_integration: Include integration analysis
            include_clustering: Include cluster identification

        Returns:
            NetworkResult with regional risk metrics
        """
        result = self.export_economic_metrics(include_nodes=True, include_edges=True)

        # Network-level metrics specific to regional networks
        add_metric(result, "network_type", self.network_type)
        add_metric(result, "num_regions", self.graph.number_of_nodes())

        # Integration analysis
        if include_integration:
            try:
                integration = self.calculate_integration_index()
                result.metadata["integration_scores"] = integration
                add_metric(result, "avg_integration", np.mean(list(integration.values())))
            except Exception:
                pass

        # Core-periphery structure
        try:
            core_periphery = self.identify_core_periphery()
            add_metric(result, "num_core_regions", len(core_periphery["core"]))
            add_metric(result, "num_periphery_regions", len(core_periphery["periphery"]))
            result.metadata["core_regions"] = core_periphery["core"]
            result.metadata["periphery_regions"] = core_periphery["periphery"]
        except Exception:
            pass

        # Regional clustering
        if include_clustering:
            try:
                clusters = self.identify_regional_clusters()
                add_metric(result, "num_clusters", len(set(clusters.values())))
                result.metadata["clusters"] = clusters
            except Exception:
                pass

        # Trade balance (if applicable)
        if self.network_type == "trade":
            try:
                balance = self.calculate_trade_balance()
                result.metadata["trade_balance"] = balance
            except Exception:
                pass

        # Market access
        try:
            market_access = self.calculate_market_access(use_distance=False)
            result.metadata["market_access"] = market_access
        except Exception:
            pass

        return result
