# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Format conversion utilities for networks.
"""

from typing import Optional

import networkx as nx
import numpy as np
import pandas as pd

from krl_network.core.exceptions import DataError


def networkx_to_igraph(graph: nx.Graph):
    """
    Convert NetworkX graph to igraph.

    Args:
        graph: NetworkX graph

    Returns:
        igraph.Graph object

    Raises:
        ImportError: If igraph is not installed
    """
    try:
        import igraph as ig
    except ImportError:
        raise ImportError(
            "igraph is required for this conversion. Install with: pip install igraph"
        )

    # Create igraph
    is_directed = isinstance(graph, nx.DiGraph)
    edges = list(graph.edges())

    # Map node names to indices
    nodes = list(graph.nodes())
    node_to_idx = {node: idx for idx, node in enumerate(nodes)}
    edges_idx = [(node_to_idx[s], node_to_idx[t]) for s, t in edges]

    # Create graph
    g = ig.Graph(n=len(nodes), edges=edges_idx, directed=is_directed)

    # Add node attributes
    g.vs["name"] = nodes
    for attr in list(graph.nodes[nodes[0]].keys()) if nodes else []:
        g.vs[attr] = [graph.nodes[node].get(attr) for node in nodes]

    # Add edge attributes
    for attr in list(graph.edges[edges[0]].keys()) if edges else []:
        g.es[attr] = [graph.edges[edge].get(attr) for edge in edges]

    return g


def igraph_to_networkx(graph) -> nx.Graph:
    """
    Convert igraph to NetworkX graph.

    Args:
        graph: igraph.Graph object

    Returns:
        NetworkX graph
    """
    # Determine if directed
    G = nx.DiGraph() if graph.is_directed() else nx.Graph()

    # Add nodes with attributes
    for v in graph.vs:
        attrs = {attr: v[attr] for attr in v.attributes()}
        node_id = attrs.pop("name", v.index)
        G.add_node(node_id, **attrs)

    # Add edges with attributes
    for e in graph.es:
        source = graph.vs[e.source]["name"] if "name" in graph.vs.attributes() else e.source
        target = graph.vs[e.target]["name"] if "name" in graph.vs.attributes() else e.target
        attrs = {attr: e[attr] for attr in e.attributes()}
        G.add_edge(source, target, **attrs)

    return G


def adjacency_to_edgelist(
    adjacency_matrix: np.ndarray,
    node_names: Optional[list] = None,
    threshold: float = 0.0,
) -> pd.DataFrame:
    """
    Convert adjacency matrix to edge list DataFrame.

    Args:
        adjacency_matrix: Square adjacency matrix
        node_names: Optional list of node names (uses indices if None)
        threshold: Minimum weight to include edge (default: 0.0)

    Returns:
        DataFrame with columns: source, target, weight

    Raises:
        DataError: If matrix is not square
    """
    if adjacency_matrix.shape[0] != adjacency_matrix.shape[1]:
        raise DataError("Adjacency matrix must be square")

    n = adjacency_matrix.shape[0]
    if node_names is None:
        node_names = list(range(n))
    elif len(node_names) != n:
        raise DataError(f"Number of node names ({len(node_names)}) must match matrix size ({n})")

    # Extract edges
    edges = []
    for i in range(n):
        for j in range(n):
            weight = adjacency_matrix[i, j]
            if abs(weight) > threshold:
                edges.append(
                    {
                        "source": node_names[i],
                        "target": node_names[j],
                        "weight": weight,
                    }
                )

    return pd.DataFrame(edges)


def edgelist_to_adjacency(
    edgelist: pd.DataFrame,
    source_col: str = "source",
    target_col: str = "target",
    weight_col: Optional[str] = "weight",
    node_order: Optional[list] = None,
) -> tuple[np.ndarray, list]:
    """
    Convert edge list DataFrame to adjacency matrix.

    Args:
        edgelist: DataFrame with edge data
        source_col: Column name for source nodes
        target_col: Column name for target nodes
        weight_col: Column name for weights (None for unweighted)
        node_order: Optional ordering for nodes (uses unique nodes if None)

    Returns:
        Tuple of (adjacency_matrix, node_names)

    Raises:
        DataError: If required columns are missing
    """
    if source_col not in edgelist.columns:
        raise DataError(f"Source column '{source_col}' not found in edgelist")
    if target_col not in edgelist.columns:
        raise DataError(f"Target column '{target_col}' not found in edgelist")

    # Get unique nodes
    if node_order is None:
        nodes = sorted(set(edgelist[source_col].unique()) | set(edgelist[target_col].unique()))
    else:
        nodes = node_order

    n = len(nodes)
    node_to_idx = {node: idx for idx, node in enumerate(nodes)}

    # Create adjacency matrix
    adj_matrix = np.zeros((n, n))

    for _, row in edgelist.iterrows():
        i = node_to_idx[row[source_col]]
        j = node_to_idx[row[target_col]]

        if weight_col and weight_col in edgelist.columns:
            weight = row[weight_col]
        else:
            weight = 1.0

        adj_matrix[i, j] = weight

    return adj_matrix, nodes
