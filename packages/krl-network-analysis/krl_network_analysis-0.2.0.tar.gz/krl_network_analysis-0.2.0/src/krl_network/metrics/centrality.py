# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Centrality measures for network analysis.
"""

from typing import Dict, Optional, Union

import networkx as nx
import pandas as pd

from krl_network.core.exceptions import ComputationError


def degree_centrality(
    graph: nx.Graph,
    normalized: bool = True,
) -> Dict[Union[str, int], float]:
    """
    Calculate degree centrality for all nodes.

    Degree centrality is the fraction of nodes a node is connected to.

    Args:
        graph: NetworkX graph
        normalized: If True, normalize by dividing by n-1

    Returns:
        Dictionary mapping nodes to degree centrality values
    """
    try:
        return nx.degree_centrality(graph) if normalized else dict(graph.degree())
    except Exception as e:
        raise ComputationError(f"Failed to compute degree centrality: {e}")


def betweenness_centrality(
    graph: nx.Graph,
    normalized: bool = True,
    weight: Optional[str] = None,
    endpoints: bool = False,
) -> Dict[Union[str, int], float]:
    """
    Calculate betweenness centrality for all nodes.

    Betweenness centrality measures the extent to which a node lies on
    paths between other nodes (acts as a bridge).

    Args:
        graph: NetworkX graph
        normalized: If True, normalize by dividing by (n-1)(n-2)/2
        weight: Edge weight attribute name (None for unweighted)
        endpoints: If True, include endpoints in path counts

    Returns:
        Dictionary mapping nodes to betweenness centrality values
    """
    try:
        return nx.betweenness_centrality(
            graph,
            normalized=normalized,
            weight=weight,
            endpoints=endpoints,
        )
    except Exception as e:
        raise ComputationError(f"Failed to compute betweenness centrality: {e}")


def closeness_centrality(
    graph: nx.Graph,
    distance: Optional[str] = None,
    wf_improved: bool = True,
) -> Dict[Union[str, int], float]:
    """
    Calculate closeness centrality for all nodes.

    Closeness centrality measures how close a node is to all other nodes
    (inverse of average shortest path length).

    Args:
        graph: NetworkX graph
        distance: Edge distance attribute name (None for unweighted)
        wf_improved: If True, use Wasserman-Faust improved formula

    Returns:
        Dictionary mapping nodes to closeness centrality values
    """
    try:
        return nx.closeness_centrality(
            graph,
            distance=distance,
            wf_improved=wf_improved,
        )
    except Exception as e:
        raise ComputationError(f"Failed to compute closeness centrality: {e}")


def eigenvector_centrality(
    graph: nx.Graph,
    max_iter: int = 100,
    tol: float = 1e-6,
    weight: Optional[str] = "weight",
) -> Dict[Union[str, int], float]:
    """
    Calculate eigenvector centrality for all nodes.

    Eigenvector centrality measures node importance based on the
    importance of its neighbors (recursive definition).

    Args:
        graph: NetworkX graph
        max_iter: Maximum number of iterations
        tol: Convergence tolerance
        weight: Edge weight attribute name (None for unweighted)

    Returns:
        Dictionary mapping nodes to eigenvector centrality values
    """
    try:
        return nx.eigenvector_centrality(
            graph,
            max_iter=max_iter,
            tol=tol,
            weight=weight,
        )
    except nx.PowerIterationFailedConvergence:
        # Fall back to eigenvector centrality with numpy
        try:
            return nx.eigenvector_centrality_numpy(graph, weight=weight)
        except Exception as e2:
            raise ComputationError(f"Eigenvector centrality failed to converge: {e2}")
    except Exception as e:
        raise ComputationError(f"Failed to compute eigenvector centrality: {e}")


def pagerank(
    graph: nx.Graph,
    alpha: float = 0.85,
    max_iter: int = 100,
    tol: float = 1e-6,
    weight: Optional[str] = "weight",
) -> Dict[Union[str, int], float]:
    """
    Calculate PageRank for all nodes.

    PageRank measures node importance using the Google PageRank algorithm.
    It's similar to eigenvector centrality but includes damping.

    Args:
        graph: NetworkX graph
        alpha: Damping parameter (probability of continuing)
        max_iter: Maximum number of iterations
        tol: Convergence tolerance
        weight: Edge weight attribute name (None for unweighted)

    Returns:
        Dictionary mapping nodes to PageRank values
    """
    try:
        return nx.pagerank(
            graph,
            alpha=alpha,
            max_iter=max_iter,
            tol=tol,
            weight=weight,
        )
    except Exception as e:
        raise ComputationError(f"Failed to compute PageRank: {e}")


def katz_centrality(
    graph: nx.Graph,
    alpha: float = 0.1,
    beta: float = 1.0,
    max_iter: int = 1000,
    tol: float = 1e-6,
    weight: Optional[str] = None,
) -> Dict[Union[str, int], float]:
    """
    Calculate Katz centrality for all nodes.

    Katz centrality measures influence by considering all paths
    between nodes with exponentially decaying weights.

    Args:
        graph: NetworkX graph
        alpha: Attenuation factor (must be smaller than 1/λ_max)
        beta: Weight attributed to immediate neighborhood
        max_iter: Maximum number of iterations
        tol: Convergence tolerance
        weight: Edge weight attribute name (None for unweighted)

    Returns:
        Dictionary mapping nodes to Katz centrality values
    """
    try:
        return nx.katz_centrality(
            graph,
            alpha=alpha,
            beta=beta,
            max_iter=max_iter,
            tol=tol,
            weight=weight,
        )
    except nx.PowerIterationFailedConvergence:
        # Try with numpy method
        try:
            return nx.katz_centrality_numpy(graph, alpha=alpha, beta=beta, weight=weight)
        except Exception as e2:
            raise ComputationError(f"Katz centrality failed to converge: {e2}")
    except Exception as e:
        raise ComputationError(f"Failed to compute Katz centrality: {e}")


def centrality_to_dataframe(
    centrality_dict: Dict[Union[str, int], float],
    column_name: str = "centrality",
) -> pd.DataFrame:
    """
    Convert centrality dictionary to DataFrame.

    Args:
        centrality_dict: Dictionary mapping nodes to centrality values
        column_name: Name for the centrality column

    Returns:
        DataFrame with node and centrality columns
    """
    return pd.DataFrame(
        [(node, value) for node, value in centrality_dict.items()],
        columns=["node", column_name],
    ).sort_values(by=column_name, ascending=False)


def top_k_central_nodes(
    centrality_dict: Dict[Union[str, int], float],
    k: int = 10,
) -> pd.DataFrame:
    """
    Get top k nodes by centrality.

    Args:
        centrality_dict: Dictionary mapping nodes to centrality values
        k: Number of top nodes to return

    Returns:
        DataFrame of top k nodes sorted by centrality
    """
    df = centrality_to_dataframe(centrality_dict)
    return df.head(k)
