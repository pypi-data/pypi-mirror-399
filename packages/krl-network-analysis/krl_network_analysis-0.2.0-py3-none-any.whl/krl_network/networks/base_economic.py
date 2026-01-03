"""
Base class for economic networks.

This module provides shared functionality for all economic network types.
"""

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

from krl_network.core.base import BaseNetwork, NetworkConfig
from krl_network.core.exceptions import ComputationError, DataError
from krl_network.core.result import NetworkResult, add_metric


class BaseEconomicNetwork(BaseNetwork):
    """Base class for economic network analysis.

    Provides shared functionality for supply chain, regional, I-O, and trade networks.
    """

    def __init__(
        self, config: Optional[NetworkConfig] = None, metadata: Optional[Dict[str, Any]] = None
    ):
        """Initialize economic network.

        Args:
            config: Network configuration
            metadata: Additional metadata (time period, data source, etc.)
        """
        super().__init__(graph=None, config=config, name=None)
        self.metadata = metadata or {}

    def validate_economic_data(self, df: pd.DataFrame, required_cols: List[str]) -> None:
        """Validate economic data DataFrame.

        Args:
            df: DataFrame to validate
            required_cols: Required column names

        Raises:
            DataError: If validation fails
        """
        # Check required columns
        missing = set(required_cols) - set(df.columns)
        if missing:
            raise DataError(f"Missing required columns: {missing}")

        # Check for empty DataFrame
        if df.empty:
            raise DataError("DataFrame is empty")

        # Check for nulls in required columns
        null_cols = [col for col in required_cols if df[col].isnull().any()]
        if null_cols:
            raise DataError(f"Null values found in required columns: {null_cols}")

    def calculate_network_resilience(self) -> float:
        """Calculate network resilience score.

        Resilience is based on redundancy, connectivity, and clustering.

        Returns:
            Resilience score (0-1, higher is more resilient)
        """
        if self.graph.number_of_nodes() == 0:
            return 0.0

        # Component: connectivity (0-1)
        connectivity_score = 1.0 if self.is_connected() else 0.5

        # Component: average degree (normalized)
        avg_degree = sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes()
        degree_score = min(avg_degree / 10.0, 1.0)  # Cap at 10

        # Component: clustering (0-1)
        try:
            import networkx as nx

            clustering = nx.average_clustering(self.graph)
        except:
            clustering = 0.0

        # Weighted combination
        resilience = 0.4 * connectivity_score + 0.3 * degree_score + 0.3 * clustering

        return round(resilience, 3)

    def identify_critical_nodes(self, method: str = "betweenness", top_k: int = 10) -> pd.DataFrame:
        """Identify critical nodes using various centrality measures.

        Args:
            method: Centrality method (betweenness, degree, eigenvector, pagerank)
            top_k: Number of top nodes to return

        Returns:
            DataFrame with node, centrality score, and rank

        Raises:
            ComputationError: If method is invalid
        """
        import networkx as nx

        from krl_network.metrics.centrality import (
            betweenness_centrality,
            degree_centrality,
            eigenvector_centrality,
            pagerank,
        )

        # Calculate centrality
        if method == "betweenness":
            centrality = betweenness_centrality(self.graph)
        elif method == "degree":
            centrality = degree_centrality(self.graph)
        elif method == "eigenvector":
            centrality = eigenvector_centrality(self.graph)
        elif method == "pagerank":
            centrality = pagerank(self.graph)
        else:
            raise ComputationError(f"Invalid centrality method: {method}")

        # Convert to DataFrame and rank
        df = pd.DataFrame(list(centrality.items()), columns=["node", "centrality"])
        df = df.sort_values("centrality", ascending=False)
        df["rank"] = range(1, len(df) + 1)

        return df.head(top_k).reset_index(drop=True)

    def calculate_node_risk_score(
        self, node: Any, weights: Optional[Dict[str, float]] = None
    ) -> float:
        """Calculate risk score for a node.

        Risk is based on centrality (dependency) and local structure.

        Args:
            node: Node identifier
            weights: Weights for risk components (centrality, degree, clustering)

        Returns:
            Risk score (0-1, higher is riskier)
        """
        if node not in self.graph:
            return 0.0

        # Default weights
        if weights is None:
            weights = {"centrality": 0.5, "degree": 0.3, "clustering": 0.2}

        # Centrality component (betweenness)
        import networkx as nx

        try:
            betweenness = nx.betweenness_centrality(self.graph)
            centrality_score = betweenness.get(node, 0)
        except:
            centrality_score = 0.0

        # Degree component (normalized)
        degree = self.graph.degree(node)
        max_degree = (
            max(dict(self.graph.degree()).values()) if self.graph.number_of_nodes() > 0 else 1
        )
        degree_score = degree / max_degree if max_degree > 0 else 0

        # Clustering component (inverted - low clustering = high risk)
        try:
            clustering = nx.clustering(self.graph, node)
            clustering_score = 1 - clustering  # Invert
        except:
            clustering_score = 0.5

        # Weighted combination
        risk = (
            weights["centrality"] * centrality_score
            + weights["degree"] * degree_score
            + weights["clustering"] * clustering_score
        )

        return round(risk, 3)

    def export_economic_metrics(
        self, include_nodes: bool = True, include_edges: bool = True
    ) -> NetworkResult:
        """Export economic network metrics.

        Args:
            include_nodes: Include node-level metrics
            include_edges: Include edge-level metrics

        Returns:
            NetworkResult with network and node/edge metrics
        """
        result = NetworkResult(metadata=self.metadata)

        # Network-level metrics
        add_metric(result, "num_nodes", self.graph.number_of_nodes())
        add_metric(result, "num_edges", self.graph.number_of_edges())
        add_metric(result, "density", self.density())

        # Only calculate connectivity for non-empty networks
        if self.graph.number_of_nodes() > 0:
            add_metric(result, "is_connected", self.is_connected())
        else:
            add_metric(result, "is_connected", False)

        add_metric(result, "resilience", self.calculate_network_resilience())

        # Node-level metrics
        if include_nodes and self.graph.number_of_nodes() > 0:
            nodes_data = []
            for node in self.graph.nodes():
                nodes_data.append(
                    {
                        "node": node,
                        "degree": self.graph.degree(node),
                        "risk_score": self.calculate_node_risk_score(node),
                    }
                )
            result.nodes = pd.DataFrame(nodes_data)

        # Edge-level metrics
        if include_edges and self.graph.number_of_edges() > 0:
            edges_data = []
            for u, v, data in self.graph.edges(data=True):
                edges_data.append({"source": u, "target": v, "weight": data.get("weight", 1.0)})
            result.edges = pd.DataFrame(edges_data)

        return result
