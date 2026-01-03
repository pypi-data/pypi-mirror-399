# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Base classes for network analysis.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import networkx as nx
import pandas as pd

from krl_network.core.exceptions import DataError, InvalidNetworkError
from krl_network.core.result import NetworkResult


@dataclass
class NetworkConfig:
    """
    Configuration for network analysis.

    Attributes:
        directed: Whether the network is directed
        weighted: Whether edges have weights
        multigraph: Whether to allow multiple edges between nodes
        default_weight: Default weight for unweighted edges
        self_loops: Whether to allow self-loops
        cache_results: Whether to cache computation results
        parallel: Whether to use parallel computation
        n_jobs: Number of parallel jobs (-1 for all cores)
    """

    directed: bool = False
    weighted: bool = True
    multigraph: bool = False
    default_weight: float = 1.0
    self_loops: bool = False
    cache_results: bool = True
    parallel: bool = False
    n_jobs: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseNetwork(ABC):
    """
    Abstract base class for all network types.

    This class provides the foundational interface and common functionality
    for constructing and analyzing economic networks.
    """

    def __init__(
        self,
        graph: Optional[nx.Graph] = None,
        config: Optional[NetworkConfig] = None,
        name: Optional[str] = None,
    ):
        """
        Initialize a network.

        Args:
            graph: NetworkX graph object (if None, creates empty graph)
            config: Network configuration
            name: Optional name for the network
        """
        self.config = config or NetworkConfig()
        self.name = name or self.__class__.__name__

        # Create appropriate graph type
        if graph is not None:
            self.graph = graph
        else:
            self.graph = self._create_empty_graph()

        # Cache for expensive computations
        self._cache: Dict[str, Any] = {}

    def _create_empty_graph(self) -> nx.Graph:
        """Create an empty graph based on configuration."""
        if self.config.directed:
            if self.config.multigraph:
                return nx.MultiDiGraph()
            return nx.DiGraph()
        else:
            if self.config.multigraph:
                return nx.MultiGraph()
            return nx.Graph()

    @abstractmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        source_col: str,
        target_col: str,
        weight_col: Optional[str] = None,
        **kwargs,
    ) -> "BaseNetwork":
        """
        Construct network from a pandas DataFrame.

        Args:
            df: DataFrame containing edge data
            source_col: Column name for source nodes
            target_col: Column name for target nodes
            weight_col: Column name for edge weights
            **kwargs: Additional arguments

        Returns:
            Constructed network instance
        """
        pass

    def add_node(self, node: Union[str, int], attributes: Optional[Dict[str, Any]] = None) -> None:
        """Add a node to the network."""
        self.graph.add_node(node, **(attributes or {}))
        self._invalidate_cache()

    def add_edge(
        self,
        source: Union[str, int],
        target: Union[str, int],
        weight: Optional[float] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add an edge to the network."""
        if not self.config.self_loops and source == target:
            return

        attrs = attributes or {}
        if self.config.weighted and weight is not None:
            attrs["weight"] = weight
        elif self.config.weighted:
            attrs["weight"] = self.config.default_weight

        self.graph.add_edge(source, target, **attrs)
        self._invalidate_cache()

    def remove_node(self, node: Union[str, int]) -> None:
        """Remove a node from the network."""
        if node in self.graph:
            self.graph.remove_node(node)
            self._invalidate_cache()

    def remove_edge(self, source: Union[str, int], target: Union[str, int]) -> None:
        """Remove an edge from the network."""
        if self.graph.has_edge(source, target):
            self.graph.remove_edge(source, target)
            self._invalidate_cache()

    def nodes(self) -> List[Union[str, int]]:
        """Get list of all nodes."""
        return list(self.graph.nodes())

    def edges(self) -> List[Tuple[Union[str, int], Union[str, int]]]:
        """Get list of all edges."""
        return list(self.graph.edges())

    def num_nodes(self) -> int:
        """Get number of nodes."""
        return self.graph.number_of_nodes()

    def num_edges(self) -> int:
        """Get number of edges."""
        return self.graph.number_of_edges()

    def has_node(self, node: Union[str, int]) -> bool:
        """Check if node exists in network."""
        return node in self.graph

    def has_edge(self, source: Union[str, int], target: Union[str, int]) -> bool:
        """Check if edge exists in network."""
        return self.graph.has_edge(source, target)

    def neighbors(self, node: Union[str, int]) -> List[Union[str, int]]:
        """Get neighbors of a node."""
        if node not in self.graph:
            raise InvalidNetworkError(f"Node {node} not in network")
        return list(self.graph.neighbors(node))

    def degree(self, node: Optional[Union[str, int]] = None) -> Union[int, Dict]:
        """
        Get degree of node(s).

        Args:
            node: Specific node (None for all nodes)

        Returns:
            Degree of node or dict of all degrees
        """
        if node is not None:
            return self.graph.degree(node)
        return dict(self.graph.degree())

    def get_node_attributes(self, node: Union[str, int]) -> Dict[str, Any]:
        """Get attributes of a node."""
        if node not in self.graph:
            raise InvalidNetworkError(f"Node {node} not in network")
        return dict(self.graph.nodes[node])

    def get_edge_attributes(
        self, source: Union[str, int], target: Union[str, int]
    ) -> Dict[str, Any]:
        """Get attributes of an edge."""
        if not self.graph.has_edge(source, target):
            raise InvalidNetworkError(f"Edge ({source}, {target}) not in network")
        return dict(self.graph.edges[source, target])

    def set_node_attributes(self, attributes: Dict[Union[str, int], Dict[str, Any]]) -> None:
        """Set attributes for multiple nodes."""
        nx.set_node_attributes(self.graph, attributes)
        self._invalidate_cache()

    def set_edge_attributes(
        self, attributes: Dict[Tuple[Union[str, int], Union[str, int]], Dict[str, Any]]
    ) -> None:
        """Set attributes for multiple edges."""
        nx.set_edge_attributes(self.graph, attributes)
        self._invalidate_cache()

    def subgraph(self, nodes: List[Union[str, int]]) -> "BaseNetwork":
        """Create a subgraph containing specified nodes."""
        subgraph = self.graph.subgraph(nodes).copy()
        return self.__class__(graph=subgraph, config=self.config, name=f"{self.name}_subgraph")

    def density(self) -> float:
        """Calculate network density."""
        return nx.density(self.graph)

    def is_connected(self) -> bool:
        """Check if network is connected."""
        if self.config.directed:
            return nx.is_weakly_connected(self.graph)
        return nx.is_connected(self.graph)

    def connected_components(self) -> List[Set[Union[str, int]]]:
        """Get connected components."""
        if self.config.directed:
            return list(nx.weakly_connected_components(self.graph))
        return list(nx.connected_components(self.graph))

    def to_dataframe(self) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Convert network to DataFrames.

        Returns:
            Tuple of (nodes_df, edges_df)
        """
        # Nodes DataFrame
        nodes_data = []
        for node in self.graph.nodes():
            node_dict = {"node": node}
            node_dict.update(self.graph.nodes[node])
            nodes_data.append(node_dict)
        nodes_df = pd.DataFrame(nodes_data)

        # Edges DataFrame
        edges_data = []
        for source, target in self.graph.edges():
            edge_dict = {"source": source, "target": target}
            edge_dict.update(self.graph.edges[source, target])
            edges_data.append(edge_dict)
        edges_df = pd.DataFrame(edges_data)

        return nodes_df, edges_df

    def validate(self) -> bool:
        """
        Validate network structure.

        Returns:
            True if network is valid

        Raises:
            InvalidNetworkError: If network structure is invalid
        """
        # Check for isolated nodes if required
        if self.num_nodes() > 0 and self.num_edges() == 0:
            raise InvalidNetworkError("Network has nodes but no edges")

        # Check for self-loops if not allowed
        if not self.config.self_loops:
            self_loops = list(nx.selfloop_edges(self.graph))
            if self_loops:
                raise InvalidNetworkError(
                    f"Network contains {len(self_loops)} self-loops but they are not allowed"
                )

        # Check for negative weights if weighted
        if self.config.weighted:
            for _, _, data in self.graph.edges(data=True):
                if "weight" in data and data["weight"] < 0:
                    raise InvalidNetworkError("Network contains negative weights")

        return True

    def summary(self) -> str:
        """Generate a text summary of the network."""
        lines = [
            f"Network: {self.name}",
            "=" * 40,
            f"Type: {'Directed' if self.config.directed else 'Undirected'}",
            f"Weighted: {self.config.weighted}",
            f"Nodes: {self.num_nodes()}",
            f"Edges: {self.num_edges()}",
            f"Density: {self.density():.4f}",
        ]

        if self.num_nodes() > 0:
            lines.append(f"Connected: {self.is_connected()}")
            if not self.is_connected():
                components = self.connected_components()
                lines.append(f"Components: {len(components)}")

        return "\n".join(lines)

    def _invalidate_cache(self) -> None:
        """Invalidate computation cache."""
        if self.config.cache_results:
            self._cache.clear()

    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached result."""
        if self.config.cache_results:
            return self._cache.get(key)
        return None

    def _set_cached(self, key: str, value: Any) -> None:
        """Set cached result."""
        if self.config.cache_results:
            self._cache[key] = value

    def __len__(self) -> int:
        """Return number of nodes."""
        return self.num_nodes()

    def __contains__(self, node: Union[str, int]) -> bool:
        """Check if node is in network."""
        return self.has_node(node)

    def __repr__(self) -> str:
        """String representation."""
        return f"{self.__class__.__name__}(name='{self.name}', nodes={self.num_nodes()}, edges={self.num_edges()})"
