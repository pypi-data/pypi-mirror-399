# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Path analysis and distance metrics for networks.
"""

from typing import Dict, List, Optional, Union

import networkx as nx

from krl_network.core.exceptions import ComputationError, InvalidNetworkError


def shortest_path(
    graph: nx.Graph,
    source: Union[str, int],
    target: Optional[Union[str, int]] = None,
    weight: Optional[str] = None,
    method: str = "dijkstra",
) -> Union[List, Dict]:
    """
    Find shortest path(s) from source node.

    Args:
        graph: NetworkX graph
        source: Source node
        target: Target node (None for paths to all nodes)
        weight: Edge weight attribute (None for unweighted)
        method: Algorithm ('dijkstra', 'bellman-ford', or 'unweighted')

    Returns:
        Shortest path (list) if target specified, or dict of paths to all nodes
    """
    if source not in graph:
        raise InvalidNetworkError(f"Source node {source} not in graph")

    if target is not None and target not in graph:
        raise InvalidNetworkError(f"Target node {target} not in graph")

    try:
        if method == "unweighted" or weight is None:
            if target is not None:
                return nx.shortest_path(graph, source=source, target=target)
            return nx.shortest_path(graph, source=source)
        elif method == "dijkstra":
            if target is not None:
                return nx.dijkstra_path(graph, source=source, target=target, weight=weight)
            return nx.single_source_dijkstra_path(graph, source=source, weight=weight)
        elif method == "bellman-ford":
            if target is not None:
                return nx.bellman_ford_path(graph, source=source, target=target, weight=weight)
            return nx.single_source_bellman_ford_path(graph, source=source, weight=weight)
        else:
            raise ValueError(f"Unknown method: {method}")
    except nx.NetworkXNoPath:
        raise ComputationError(f"No path exists from {source} to {target}")
    except Exception as e:
        raise ComputationError(f"Failed to compute shortest path: {e}")


def all_pairs_shortest_path(
    graph: nx.Graph,
    weight: Optional[str] = None,
) -> Dict[Union[str, int], Dict[Union[str, int], List]]:
    """
    Find shortest paths between all pairs of nodes.

    Args:
        graph: NetworkX graph
        weight: Edge weight attribute (None for unweighted)

    Returns:
        Dictionary mapping source->target->path
    """
    try:
        if weight is None:
            return dict(nx.all_pairs_shortest_path(graph))
        else:
            return dict(nx.all_pairs_dijkstra_path(graph, weight=weight))
    except Exception as e:
        raise ComputationError(f"Failed to compute all pairs shortest paths: {e}")


def shortest_path_length(
    graph: nx.Graph,
    source: Union[str, int],
    target: Optional[Union[str, int]] = None,
    weight: Optional[str] = None,
) -> Union[float, Dict[Union[str, int], float]]:
    """
    Calculate shortest path length(s) from source node.

    Args:
        graph: NetworkX graph
        source: Source node
        target: Target node (None for lengths to all nodes)
        weight: Edge weight attribute (None for unweighted)

    Returns:
        Path length (float) if target specified, or dict of lengths to all nodes
    """
    if source not in graph:
        raise InvalidNetworkError(f"Source node {source} not in graph")

    try:
        if target is not None:
            return nx.shortest_path_length(graph, source=source, target=target, weight=weight)
        return dict(nx.shortest_path_length(graph, source=source, weight=weight))
    except nx.NetworkXNoPath:
        raise ComputationError(f"No path exists from {source} to {target}")
    except Exception as e:
        raise ComputationError(f"Failed to compute shortest path length: {e}")


def average_shortest_path_length(
    graph: nx.Graph,
    weight: Optional[str] = None,
) -> float:
    """
    Calculate average shortest path length for the network.

    The graph must be connected (or use largest connected component).

    Args:
        graph: NetworkX graph
        weight: Edge weight attribute (None for unweighted)

    Returns:
        Average shortest path length
    """
    # Check if graph is connected
    is_directed = isinstance(graph, nx.DiGraph)
    if is_directed:
        if not nx.is_weakly_connected(graph):
            raise InvalidNetworkError("Graph must be connected. Use largest connected component.")
    else:
        if not nx.is_connected(graph):
            raise InvalidNetworkError("Graph must be connected. Use largest connected component.")

    try:
        return nx.average_shortest_path_length(graph, weight=weight)
    except Exception as e:
        raise ComputationError(f"Failed to compute average shortest path length: {e}")


def diameter(
    graph: nx.Graph,
    weight: Optional[str] = None,
) -> float:
    """
    Calculate diameter of the network.

    The diameter is the maximum eccentricity (longest shortest path).

    Args:
        graph: NetworkX graph
        weight: Edge weight attribute (None for unweighted)

    Returns:
        Network diameter
    """
    # Check if graph is connected
    is_directed = isinstance(graph, nx.DiGraph)
    if is_directed:
        if not nx.is_weakly_connected(graph):
            raise InvalidNetworkError("Graph must be connected to compute diameter")
    else:
        if not nx.is_connected(graph):
            raise InvalidNetworkError("Graph must be connected to compute diameter")

    try:
        if weight is None:
            return nx.diameter(graph)
        else:
            # For weighted graphs, compute manually from eccentricities
            ecc = eccentricity(graph, weight=weight)
            return max(ecc.values())
    except Exception as e:
        raise ComputationError(f"Failed to compute diameter: {e}")


def eccentricity(
    graph: nx.Graph,
    v: Optional[Union[str, int]] = None,
    weight: Optional[str] = None,
) -> Union[float, Dict[Union[str, int], float]]:
    """
    Calculate eccentricity for node(s).

    Eccentricity is the maximum distance from a node to all other nodes.

    Args:
        graph: NetworkX graph
        v: Specific node (None for all nodes)
        weight: Edge weight attribute (None for unweighted)

    Returns:
        Eccentricity value(s)
    """
    try:
        if weight is None:
            return nx.eccentricity(graph, v=v)
        else:
            # For weighted graphs, compute manually
            if v is not None:
                lengths = nx.single_source_dijkstra_path_length(graph, v, weight=weight)
                return max(lengths.values())
            else:
                result = {}
                for node in graph.nodes():
                    lengths = nx.single_source_dijkstra_path_length(graph, node, weight=weight)
                    result[node] = max(lengths.values())
                return result
    except Exception as e:
        raise ComputationError(f"Failed to compute eccentricity: {e}")


def radius(graph: nx.Graph) -> float:
    """
    Calculate radius of the network.

    The radius is the minimum eccentricity.

    Args:
        graph: NetworkX graph

    Returns:
        Network radius
    """
    try:
        return nx.radius(graph)
    except Exception as e:
        raise ComputationError(f"Failed to compute radius: {e}")


def periphery(graph: nx.Graph) -> List[Union[str, int]]:
    """
    Find peripheral nodes (nodes with eccentricity equal to diameter).

    Args:
        graph: NetworkX graph

    Returns:
        List of peripheral nodes
    """
    try:
        return nx.periphery(graph)
    except Exception as e:
        raise ComputationError(f"Failed to find periphery: {e}")


def center(graph: nx.Graph) -> List[Union[str, int]]:
    """
    Find central nodes (nodes with eccentricity equal to radius).

    Args:
        graph: NetworkX graph

    Returns:
        List of central nodes
    """
    try:
        return nx.center(graph)
    except Exception as e:
        raise ComputationError(f"Failed to find center: {e}")
