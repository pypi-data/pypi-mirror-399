# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Network statistics and structural measures.
"""

from typing import Optional, Union

import networkx as nx

from krl_network.core.exceptions import ComputationError


def density(graph: nx.Graph) -> float:
    """
    Calculate network density.

    Density is the ratio of actual edges to possible edges.

    Args:
        graph: NetworkX graph

    Returns:
        Density value between 0 and 1
    """
    try:
        return nx.density(graph)
    except Exception as e:
        raise ComputationError(f"Failed to compute density: {e}")


def reciprocity(graph: nx.Graph) -> float:
    """
    Calculate reciprocity for directed networks.

    Reciprocity is the fraction of edges that have a reciprocal edge.
    Only applicable to directed graphs.

    Args:
        graph: NetworkX directed graph

    Returns:
        Reciprocity value between 0 and 1

    Raises:
        ComputationError: If graph is not directed
    """
    if not isinstance(graph, nx.DiGraph):
        raise ComputationError("Reciprocity is only defined for directed graphs")

    try:
        return nx.reciprocity(graph)
    except Exception as e:
        raise ComputationError(f"Failed to compute reciprocity: {e}")


def degree_assortativity(graph: nx.Graph, weight: Optional[str] = None) -> float:
    """
    Calculate degree assortativity coefficient.

    Assortativity measures the tendency of nodes to connect to others
    with similar degree. Positive values indicate assortative mixing
    (high-degree nodes connect to high-degree nodes).

    Args:
        graph: NetworkX graph
        weight: Edge weight attribute (None for unweighted)

    Returns:
        Assortativity coefficient between -1 and 1
    """
    try:
        return nx.degree_assortativity_coefficient(graph, weight=weight)
    except Exception as e:
        raise ComputationError(f"Failed to compute degree assortativity: {e}")


def assortativity(
    graph: nx.Graph,
    attribute: str,
    weight: Optional[str] = None,
) -> float:
    """
    Calculate attribute assortativity coefficient.

    Measures the tendency of nodes to connect to others with similar
    attribute values.

    Args:
        graph: NetworkX graph
        attribute: Node attribute name
        weight: Edge weight attribute (None for unweighted)

    Returns:
        Assortativity coefficient between -1 and 1
    """
    try:
        # Check if attribute is numeric
        sample_value = next(iter(graph.nodes(data=attribute)))[1]
        if isinstance(sample_value, (int, float)):
            return nx.numeric_assortativity_coefficient(graph, attribute, weight=weight)
        else:
            return nx.attribute_assortativity_coefficient(graph, attribute)
    except Exception as e:
        raise ComputationError(f"Failed to compute attribute assortativity: {e}")


def number_of_nodes(graph: nx.Graph) -> int:
    """Get number of nodes in the graph."""
    return graph.number_of_nodes()


def number_of_edges(graph: nx.Graph) -> int:
    """Get number of edges in the graph."""
    return graph.number_of_edges()


def average_degree(graph: nx.Graph) -> float:
    """
    Calculate average degree.

    Args:
        graph: NetworkX graph

    Returns:
        Average degree across all nodes
    """
    try:
        degrees = [d for _, d in graph.degree()]
        return sum(degrees) / len(degrees) if degrees else 0.0
    except Exception as e:
        raise ComputationError(f"Failed to compute average degree: {e}")


def degree_distribution(graph: nx.Graph) -> dict:
    """
    Get the degree distribution.

    Args:
        graph: NetworkX graph

    Returns:
        Dictionary mapping degree values to their frequency
    """
    try:
        degrees = [d for _, d in graph.degree()]
        distribution = {}
        for degree in degrees:
            distribution[degree] = distribution.get(degree, 0) + 1
        return distribution
    except Exception as e:
        raise ComputationError(f"Failed to compute degree distribution: {e}")


def connectivity(graph: nx.Graph) -> Union[int, float]:
    """
    Calculate node connectivity.

    Node connectivity is the minimum number of nodes that must be removed
    to disconnect the graph.

    Args:
        graph: NetworkX graph

    Returns:
        Node connectivity value
    """
    try:
        return nx.node_connectivity(graph)
    except Exception as e:
        raise ComputationError(f"Failed to compute connectivity: {e}")


def edge_connectivity(graph: nx.Graph) -> Union[int, float]:
    """
    Calculate edge connectivity.

    Edge connectivity is the minimum number of edges that must be removed
    to disconnect the graph.

    Args:
        graph: NetworkX graph

    Returns:
        Edge connectivity value
    """
    try:
        return nx.edge_connectivity(graph)
    except Exception as e:
        raise ComputationError(f"Failed to compute edge connectivity: {e}")
