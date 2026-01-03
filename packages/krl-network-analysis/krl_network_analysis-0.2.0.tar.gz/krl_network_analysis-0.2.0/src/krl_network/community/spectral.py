"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Spectral clustering methods for community detection.
"""

import warnings
from typing import Any, Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np
from scipy.cluster import vq
from scipy.sparse import csgraph
from sklearn.cluster import KMeans

from krl_network.community.modularity import calculate_modularity
from krl_network.core.exceptions import ComputationError
from krl_network.core.result import NetworkResult


def spectral_clustering(
    graph: nx.Graph,
    n_communities: int,
    method: str = "normalized",
    weight: str = "weight",
    random_state: Optional[int] = None,
) -> List[Set[Any]]:
    """Spectral clustering using graph Laplacian eigendecomposition.

    Projects nodes into low-dimensional space defined by eigenvectors
    of the Laplacian matrix, then applies k-means clustering.

    Args:
        graph: Input graph
        n_communities: Number of communities to find
        method: Laplacian type ('unnormalized', 'normalized', 'random_walk')
        weight: Edge weight attribute
        random_state: Random seed for k-means

    Returns:
        List of community sets

    Reference:
        Von Luxburg (2007). A tutorial on spectral clustering.
    """
    if graph.number_of_nodes() == 0:
        return []

    if n_communities <= 0:
        raise ValueError("n_communities must be positive")

    nodes = list(graph.nodes())
    n = len(nodes)

    if n_communities > n:
        return [{node} for node in nodes]

    if n_communities == 1:
        return [set(nodes)]

    # Build adjacency matrix
    node_idx = {node: i for i, node in enumerate(nodes)}
    A = np.zeros((n, n))

    for u, v, data in graph.edges(data=True):
        w = data.get(weight, 1.0)
        i, j = node_idx[u], node_idx[v]
        A[i, j] = w
        A[j, i] = w  # Symmetric

    # Compute Laplacian
    if method == "unnormalized":
        L = _unnormalized_laplacian(A)
    elif method == "normalized":
        L = _normalized_laplacian(A)
    elif method == "random_walk":
        L = _random_walk_laplacian(A)
    else:
        raise ValueError(f"Unknown method: {method}")

    # Eigendecomposition
    try:
        # For Laplacian, we want smallest eigenvalues
        eigenvalues, eigenvectors = np.linalg.eigh(L)

        # Take first k eigenvectors (corresponding to k smallest eigenvalues)
        k = n_communities
        X = eigenvectors[:, :k]

        # Normalize rows for normalized spectral clustering
        if method in ["normalized", "random_walk"]:
            row_norms = np.linalg.norm(X, axis=1, keepdims=True)
            row_norms[row_norms == 0] = 1  # Avoid division by zero
            X = X / row_norms

    except np.linalg.LinAlgError as e:
        raise ComputationError(f"Eigendecomposition failed: {e}")

    # K-means clustering on embedded space
    if random_state is not None:
        np.random.seed(random_state)

    kmeans = KMeans(n_clusters=k, random_state=random_state, n_init=10)
    labels = kmeans.fit_predict(X)

    # Convert to community sets
    communities = [set() for _ in range(k)]
    for i, node in enumerate(nodes):
        communities[labels[i]].add(node)

    # Remove empty communities
    communities = [c for c in communities if c]

    return communities


def _unnormalized_laplacian(A: np.ndarray) -> np.ndarray:
    """Compute unnormalized Laplacian L = D - A."""
    D = np.diag(A.sum(axis=1))
    return D - A


def _normalized_laplacian(A: np.ndarray) -> np.ndarray:
    """Compute normalized Laplacian L_norm = D^(-1/2) L D^(-1/2)."""
    d = A.sum(axis=1)
    d[d == 0] = 1  # Avoid division by zero
    D_inv_sqrt = np.diag(1.0 / np.sqrt(d))

    L = np.diag(d) - A
    L_norm = D_inv_sqrt @ L @ D_inv_sqrt

    return L_norm


def _random_walk_laplacian(A: np.ndarray) -> np.ndarray:
    """Compute random walk Laplacian L_rw = D^(-1) L."""
    d = A.sum(axis=1)
    d[d == 0] = 1  # Avoid division by zero
    D_inv = np.diag(1.0 / d)

    L = np.diag(d) - A
    L_rw = D_inv @ L

    return L_rw


def spectral_bisection(graph: nx.Graph, weight: str = "weight") -> Tuple[Set[Any], Set[Any]]:
    """Spectral bisection: split graph into two communities.

    Uses the Fiedler vector (eigenvector of second smallest eigenvalue)
    to partition the graph.

    Args:
        graph: Input graph
        weight: Edge weight attribute

    Returns:
        Tuple of two community sets

    Reference:
        Fiedler (1973). Algebraic connectivity of graphs.
    """
    if graph.number_of_nodes() <= 1:
        return (set(graph.nodes()), set())

    nodes = list(graph.nodes())
    n = len(nodes)

    # Build Laplacian
    node_idx = {node: i for i, node in enumerate(nodes)}
    A = np.zeros((n, n))

    for u, v, data in graph.edges(data=True):
        w = data.get(weight, 1.0)
        i, j = node_idx[u], node_idx[v]
        A[i, j] = w
        A[j, i] = w

    L = _unnormalized_laplacian(A)

    # Find Fiedler vector (second smallest eigenvalue)
    try:
        eigenvalues, eigenvectors = np.linalg.eigh(L)
        fiedler_vector = eigenvectors[:, 1]  # Second eigenvector
    except np.linalg.LinAlgError as e:
        raise ComputationError(f"Eigendecomposition failed: {e}")

    # Partition based on sign of Fiedler vector
    comm1 = set()
    comm2 = set()

    for i, node in enumerate(nodes):
        if fiedler_vector[i] >= 0:
            comm1.add(node)
        else:
            comm2.add(node)

    return (comm1, comm2)


def recursive_spectral_bisection(
    graph: nx.Graph, n_communities: int, weight: str = "weight"
) -> List[Set[Any]]:
    """Recursively bisect graph using spectral method.

    Args:
        graph: Input graph
        n_communities: Target number of communities
        weight: Edge weight attribute

    Returns:
        List of community sets
    """
    if graph.number_of_nodes() == 0:
        return []

    if n_communities <= 0:
        raise ValueError("n_communities must be positive")

    if n_communities == 1:
        return [set(graph.nodes())]

    # Start with whole graph as one community
    communities = [set(graph.nodes())]

    # Iteratively bisect largest community
    while len(communities) < n_communities:
        # Find largest community
        largest_idx = max(range(len(communities)), key=lambda i: len(communities[i]))
        largest = communities[largest_idx]

        if len(largest) <= 1:
            break

        # Extract subgraph
        subgraph = graph.subgraph(largest)

        # Bisect
        try:
            comm1, comm2 = spectral_bisection(subgraph, weight)
        except:
            break

        # Replace largest with two new communities
        communities.pop(largest_idx)
        if comm1:
            communities.append(comm1)
        if comm2:
            communities.append(comm2)

    return communities


def assess_spectral_structure(
    graph: nx.Graph, max_k: int = 10, method: str = "normalized", weight: str = "weight"
) -> NetworkResult:
    """Assess community structure using spectral methods.

    Tries different numbers of communities and evaluates quality.

    Args:
        graph: Input graph
        max_k: Maximum number of communities to try
        method: Laplacian type
        weight: Edge weight attribute

    Returns:
        NetworkResult with spectral analysis
    """
    if graph.number_of_nodes() == 0:
        return NetworkResult(
            metrics={"optimal_k": 0, "max_modularity": 0.0},
            nodes={},
            metadata={"method": "spectral"},
        )

    n = graph.number_of_nodes()
    max_k = min(max_k, n)

    # Try different k values
    best_Q = -1
    best_k = 1
    best_comms = [set(graph.nodes())]
    modularity_scores = []

    for k in range(2, max_k + 1):
        try:
            comms = spectral_clustering(graph, k, method, weight, random_state=42)
            Q = calculate_modularity(graph, comms, weight=weight)
            modularity_scores.append(Q)

            if Q > best_Q:
                best_Q = Q
                best_k = k
                best_comms = comms
        except:
            break

    # Compute spectral gap (indicator of cluster quality)
    try:
        nodes = list(graph.nodes())
        node_idx = {node: i for i, node in enumerate(nodes)}
        A = np.zeros((len(nodes), len(nodes)))

        for u, v, data in graph.edges(data=True):
            w = data.get(weight, 1.0)
            i, j = node_idx[u], node_idx[v]
            A[i, j] = w
            A[j, i] = w

        L = _normalized_laplacian(A)
        eigenvalues = np.linalg.eigvalsh(L)
        eigenvalues = np.sort(eigenvalues)

        # Spectral gap = difference between k-th and (k+1)-th eigenvalue
        if best_k < len(eigenvalues):
            spectral_gap = eigenvalues[best_k] - eigenvalues[best_k - 1]
        else:
            spectral_gap = 0.0
    except:
        spectral_gap = 0.0

    sizes = [len(c) for c in best_comms]

    return NetworkResult(
        metrics={
            "optimal_k": best_k,
            "max_modularity": best_Q,
            "spectral_gap": spectral_gap,
            "avg_community_size": np.mean(sizes) if sizes else 0,
        },
        nodes={
            node: {"community": comm_id} for comm_id, comm in enumerate(best_comms) for node in comm
        },
        metadata={
            "communities": best_comms,
            "modularity_by_k": modularity_scores,
            "method": "spectral",
            "laplacian_type": method,
        },
    )
