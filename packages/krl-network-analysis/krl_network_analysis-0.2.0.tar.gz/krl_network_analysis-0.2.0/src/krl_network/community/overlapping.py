"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Overlapping community detection algorithms.
"""

import itertools
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np

from krl_network.core.exceptions import ComputationError
from krl_network.core.result import NetworkResult


def clique_percolation(graph: nx.Graph, k: int = 3) -> List[Set[Any]]:
    """Clique percolation method for overlapping communities.

    Communities are unions of k-cliques that share k-1 nodes.

    Args:
        graph: Input graph
        k: Clique size

    Returns:
        List of overlapping community sets

    Reference:
        Palla et al. (2005). Uncovering the overlapping community structure.
    """
    if graph.number_of_nodes() == 0:
        return []

    if k < 2:
        raise ValueError("k must be at least 2")

    # Find all k-cliques
    try:
        if k == 2:
            # For k=2, cliques are edges
            cliques = [set(edge) for edge in graph.edges()]
        else:
            cliques = list(nx.find_cliques(graph))
            cliques = [set(c) for c in cliques if len(c) >= k]
    except:
        return []

    if not cliques:
        return []

    # Build clique adjacency graph
    # Two cliques are adjacent if they share k-1 nodes
    clique_graph = nx.Graph()
    clique_graph.add_nodes_from(range(len(cliques)))

    for i in range(len(cliques)):
        for j in range(i + 1, len(cliques)):
            overlap = len(cliques[i] & cliques[j])
            if overlap >= k - 1:
                clique_graph.add_edge(i, j)

    # Find connected components in clique graph
    components = nx.connected_components(clique_graph)

    # Each component is a community (union of cliques)
    communities = []
    for component in components:
        community = set()
        for clique_idx in component:
            community.update(cliques[clique_idx])
        communities.append(community)

    return communities


def link_communities(graph: nx.Graph, threshold: Optional[float] = None) -> Dict[Any, Set[int]]:
    """Link communities: assign edges (not nodes) to communities.

    Nodes belong to multiple communities through their edges.

    Args:
        graph: Input graph
        threshold: Similarity threshold for edge clustering

    Returns:
        Dict mapping nodes to sets of community IDs

    Reference:
        Ahn et al. (2010). Link communities reveal multiscale complexity.
    """
    if graph.number_of_edges() == 0:
        return {node: {0} for node in graph.nodes()}

    # Calculate edge similarity (number of common neighbors)
    edges = list(graph.edges())
    edge_similarity = {}

    for i, (u1, v1) in enumerate(edges):
        for j, (u2, v2) in enumerate(edges):
            if i >= j:
                continue

            # Edges share a node
            if u1 == u2 or u1 == v2 or v1 == u2 or v1 == v2:
                # Count common neighbors
                neighbors1 = set(graph.neighbors(u1)) | set(graph.neighbors(v1))
                neighbors2 = set(graph.neighbors(u2)) | set(graph.neighbors(v2))

                common = len(neighbors1 & neighbors2)
                total = len(neighbors1 | neighbors2)

                if total > 0:
                    edge_similarity[(i, j)] = common / total

    # Hierarchical clustering of edges
    if threshold is None:
        threshold = 0.5

    # Simple threshold-based clustering
    edge_labels = {}
    next_label = 0

    for i, edge in enumerate(edges):
        edge_labels[i] = next_label
        next_label += 1

    # Merge similar edges
    changed = True
    while changed:
        changed = False
        for (i, j), sim in edge_similarity.items():
            if sim >= threshold:
                label_i = edge_labels[i]
                label_j = edge_labels[j]

                if label_i != label_j:
                    # Merge j into i
                    for k in edge_labels:
                        if edge_labels[k] == label_j:
                            edge_labels[k] = label_i
                    changed = True

    # Map nodes to communities (based on their edges)
    node_communities = defaultdict(set)

    for i, (u, v) in enumerate(edges):
        comm = edge_labels[i]
        node_communities[u].add(comm)
        node_communities[v].add(comm)

    # Add isolated nodes
    for node in graph.nodes():
        if node not in node_communities:
            node_communities[node] = {next_label}
            next_label += 1

    return dict(node_communities)


def ego_network_splitting(graph: nx.Graph, min_community_size: int = 3) -> Dict[Any, Set[int]]:
    """Ego-network splitting for overlapping communities.

    Each node's ego network (node + neighbors) may split into communities.

    Args:
        graph: Input graph
        min_community_size: Minimum community size

    Returns:
        Dict mapping nodes to sets of community IDs
    """
    if graph.number_of_nodes() == 0:
        return {}

    node_communities = defaultdict(set)
    community_id = 0

    for node in graph.nodes():
        # Get ego network
        neighbors = list(graph.neighbors(node))

        if len(neighbors) < min_community_size - 1:
            # Too small to split
            node_communities[node].add(community_id)
            for neighbor in neighbors:
                node_communities[neighbor].add(community_id)
            community_id += 1
            continue

        # Extract ego network
        ego_nodes = [node] + neighbors
        ego_graph = graph.subgraph(ego_nodes)

        # Find communities in ego network (simple connected components)
        components = list(nx.connected_components(ego_graph))

        for component in components:
            if len(component) >= min_community_size:
                for n in component:
                    node_communities[n].add(community_id)
                community_id += 1

    return dict(node_communities)


def fuzzy_community_membership(
    graph: nx.Graph,
    n_communities: int,
    max_iterations: int = 100,
    fuzziness: float = 2.0,
    random_state: Optional[int] = None,
) -> Dict[Any, Dict[int, float]]:
    """Fuzzy c-means clustering for soft community membership.

    Each node has membership degrees to all communities.

    Args:
        graph: Input graph
        n_communities: Number of communities
        max_iterations: Maximum iterations
        fuzziness: Fuzziness parameter (>1, typically 2)
        random_state: Random seed

    Returns:
        Dict mapping nodes to dict of {community_id: membership_degree}
    """
    if graph.number_of_nodes() == 0:
        return {}

    if random_state is not None:
        np.random.seed(random_state)

    nodes = list(graph.nodes())
    n = len(nodes)

    if n_communities > n:
        n_communities = n

    # Build adjacency matrix
    node_idx = {node: i for i, node in enumerate(nodes)}
    A = np.zeros((n, n))

    for u, v in graph.edges():
        i, j = node_idx[u], node_idx[v]
        A[i, j] = 1.0
        A[j, i] = 1.0

    # Initialize membership matrix randomly
    U = np.random.rand(n, n_communities)
    U = U / U.sum(axis=1, keepdims=True)  # Normalize rows

    # Iterative optimization
    for iteration in range(max_iterations):
        # Update cluster centers (weighted node representations)
        U_m = U**fuzziness
        # centers shape: (n_communities, n)
        centers = (U_m.T @ A) / (U_m.sum(axis=0, keepdims=True).T + 1e-10)

        # Update membership
        U_new = np.zeros((n, n_communities))

        for i in range(n):
            for k in range(n_communities):
                # Distance from node i to center k
                dist_k = np.sum((A[i] - centers[k]) ** 2)

                if dist_k == 0:
                    U_new[i, k] = 1.0
                    continue

                # Fuzzy membership
                sum_val = 0.0
                for j in range(n_communities):
                    dist_j = np.sum((A[i] - centers[j]) ** 2)
                    if dist_j > 0:
                        sum_val += (dist_k / dist_j) ** (2 / (fuzziness - 1))

                U_new[i, k] = 1.0 / sum_val if sum_val > 0 else 0.0

        # Normalize
        U_new = U_new / (U_new.sum(axis=1, keepdims=True) + 1e-10)

        # Check convergence
        if np.allclose(U, U_new, atol=1e-4):
            break

        U = U_new

    # Convert to dict
    result = {}
    for i, node in enumerate(nodes):
        result[node] = {k: float(U[i, k]) for k in range(n_communities)}

    return result


def assess_overlapping_communities(
    graph: nx.Graph, method: str = "clique_percolation", k: int = 3
) -> NetworkResult:
    """Assess overlapping community structure.

    Args:
        graph: Input graph
        method: Detection method
        k: Parameter (k for clique percolation, etc.)

    Returns:
        NetworkResult with overlapping communities
    """
    if graph.number_of_nodes() == 0:
        return NetworkResult(metrics={"num_communities": 0}, nodes={}, metadata={"method": method})

    if method == "clique_percolation":
        communities = clique_percolation(graph, k)

        # Convert to node membership dict
        node_communities = defaultdict(set)
        for comm_id, comm in enumerate(communities):
            for node in comm:
                node_communities[node].add(comm_id)

    elif method == "link_communities":
        node_communities = link_communities(graph)

    elif method == "ego_splitting":
        node_communities = ego_network_splitting(graph)

    else:
        raise ValueError(f"Unknown method: {method}")

    # Calculate metrics
    num_communities = (
        max(max(comms) for comms in node_communities.values()) + 1 if node_communities else 0
    )

    # Overlap statistics
    overlaps = [len(comms) for comms in node_communities.values()]
    avg_overlap = np.mean(overlaps) if overlaps else 0
    max_overlap = max(overlaps) if overlaps else 0

    return NetworkResult(
        metrics={
            "num_communities": num_communities,
            "avg_memberships_per_node": avg_overlap,
            "max_memberships": max_overlap,
        },
        nodes={node: {"communities": list(comms)} for node, comms in node_communities.items()},
        metadata={
            "method": method,
            "k": k if method == "clique_percolation" else None,
        },
    )
