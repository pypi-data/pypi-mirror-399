# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Clustering and transitivity measures for networks.
"""

from typing import Dict, Optional, Union

import networkx as nx

from krl_network.core.exceptions import ComputationError


def clustering_coefficient(
    graph: nx.Graph,
    nodes: Optional[list] = None,
    weight: Optional[str] = None,
) -> Union[float, Dict[Union[str, int], float]]:
    """
    Calculate clustering coefficient for node(s).

    The clustering coefficient measures the degree to which nodes
    tend to cluster together (fraction of possible triangles that exist).

    Args:
        graph: NetworkX graph
        nodes: Specific nodes to compute (None for all nodes)
        weight: Edge weight attribute name (None for unweighted)

    Returns:
        Clustering coefficient(s) - single value if one node, dict otherwise
    """
    try:
        return nx.clustering(graph, nodes=nodes, weight=weight)
    except Exception as e:
        raise ComputationError(f"Failed to compute clustering coefficient: {e}")


def average_clustering(
    graph: nx.Graph,
    weight: Optional[str] = None,
    count_zeros: bool = True,
) -> float:
    """
    Calculate average clustering coefficient for the network.

    Args:
        graph: NetworkX graph
        weight: Edge weight attribute name (None for unweighted)
        count_zeros: If False, exclude nodes with zero clustering

    Returns:
        Average clustering coefficient
    """
    try:
        return nx.average_clustering(graph, weight=weight, count_zeros=count_zeros)
    except Exception as e:
        raise ComputationError(f"Failed to compute average clustering: {e}")


def transitivity(graph: nx.Graph) -> float:
    """
    Calculate transitivity (global clustering coefficient).

    Transitivity is the fraction of all possible triangles present in the graph.
    It's related to clustering coefficient but gives a single value for the graph.

    Args:
        graph: NetworkX graph

    Returns:
        Transitivity value between 0 and 1
    """
    try:
        return nx.transitivity(graph)
    except Exception as e:
        raise ComputationError(f"Failed to compute transitivity: {e}")


def triangles(
    graph: nx.Graph,
    nodes: Optional[list] = None,
) -> Union[int, Dict[Union[str, int], int]]:
    """
    Count the number of triangles for node(s).

    A triangle is a set of three nodes where each node is connected
    to the other two.

    Args:
        graph: NetworkX graph
        nodes: Specific nodes to compute (None for all nodes)

    Returns:
        Triangle count(s) - single value if one node, dict otherwise
    """
    try:
        result = nx.triangles(graph, nodes=nodes)
        # If nodes is a single node, return the count directly
        if nodes is not None and not isinstance(nodes, list):
            return result
        return result
    except Exception as e:
        raise ComputationError(f"Failed to count triangles: {e}")


def local_clustering_distribution(graph: nx.Graph) -> Dict[float, int]:
    """
    Get the distribution of local clustering coefficients.

    Args:
        graph: NetworkX graph

    Returns:
        Dictionary mapping clustering coefficient values to their frequency
    """
    try:
        clustering_values = nx.clustering(graph).values()
        distribution = {}
        for value in clustering_values:
            distribution[value] = distribution.get(value, 0) + 1
        return distribution
    except Exception as e:
        raise ComputationError(f"Failed to compute clustering distribution: {e}")


def identify_highly_clustered_nodes(
    graph: nx.Graph,
    threshold: float = 0.5,
) -> list:
    """
    Identify nodes with high clustering coefficients.

    Args:
        graph: NetworkX graph
        threshold: Minimum clustering coefficient (0-1)

    Returns:
        List of nodes with clustering >= threshold
    """
    try:
        clustering = nx.clustering(graph)
        return [node for node, coef in clustering.items() if coef >= threshold]
    except Exception as e:
        raise ComputationError(f"Failed to identify clustered nodes: {e}")
