"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Hierarchical community detection algorithms.
"""

import warnings
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import networkx as nx
import numpy as np
from scipy.cluster.hierarchy import cut_tree
from scipy.cluster.hierarchy import dendrogram as scipy_dendrogram

from krl_network.community.modularity import calculate_modularity
from krl_network.core.exceptions import ComputationError
from krl_network.core.result import NetworkResult


class HierarchicalCommunityDetector:
    """Hierarchical community detection using agglomerative or divisive methods."""

    def __init__(
        self, method: str = "agglomerative", linkage: str = "average", weight: str = "weight"
    ):
        """Initialize detector.

        Args:
            method: 'agglomerative' (bottom-up) or 'divisive' (top-down)
            linkage: Linkage criterion for agglomerative ('single', 'average', 'complete')
            weight: Edge weight attribute
        """
        if method not in ["agglomerative", "divisive"]:
            raise ValueError(f"Unknown method: {method}")

        if linkage not in ["single", "average", "complete"]:
            raise ValueError(f"Unknown linkage: {linkage}")

        self.method = method
        self.linkage = linkage
        self.weight = weight
        self.dendrogram_ = None

    def fit(self, graph: nx.Graph) -> "HierarchicalCommunityDetector":
        """Build hierarchical clustering.

        Args:
            graph: Input graph

        Returns:
            Self for chaining
        """
        if self.method == "agglomerative":
            self.dendrogram_ = self._agglomerative_clustering(graph)
        else:
            self.dendrogram_ = self._divisive_clustering(graph)

        return self

    def _agglomerative_clustering(self, graph: nx.Graph) -> List[Tuple]:
        """Bottom-up hierarchical clustering.

        Start with each node as a community, merge most similar pairs.

        Args:
            graph: Input graph

        Returns:
            List of merge steps (cluster_id1, cluster_id2, distance, size)
        """
        nodes = list(graph.nodes())
        n = len(nodes)

        if n == 0:
            return []

        if n == 1:
            return []

        # Create node index mapping
        node_to_idx = {node: i for i, node in enumerate(nodes)}

        # Initialize: each node is its own cluster
        # Use union-find to track cluster membership
        parent = list(range(n))
        cluster_members = {i: {i} for i in range(n)}

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        # Precompute pairwise distances
        distances = {}
        for i in range(n):
            for j in range(i + 1, n):
                u, v = nodes[i], nodes[j]
                if graph.has_edge(u, v):
                    w = graph[u][v].get(self.weight, 1.0)
                    distances[(i, j)] = 1.0 / (w + 1e-10)
                else:
                    # Use shortest path as distance if not directly connected
                    try:
                        path_len = nx.shortest_path_length(graph, u, v, weight=self.weight)
                        distances[(i, j)] = path_len
                    except nx.NetworkXNoPath:
                        distances[(i, j)] = float("inf")

        merges = []
        active_clusters = set(range(n))

        # Perform n-1 merges
        for merge_step in range(n - 1):
            # Find closest pair of clusters
            min_dist = float("inf")
            best_pair = None

            clusters = list(active_clusters)
            for idx_i, i in enumerate(clusters):
                for j in clusters[idx_i + 1 :]:
                    # Calculate inter-cluster distance based on linkage
                    members_i = cluster_members[i]
                    members_j = cluster_members[j]

                    if self.linkage == "single":
                        # Minimum distance between any pair
                        dist = min(
                            distances.get((min(a, b), max(a, b)), float("inf"))
                            for a in members_i
                            for b in members_j
                        )
                    elif self.linkage == "complete":
                        # Maximum distance between any pair
                        dist = max(
                            distances.get((min(a, b), max(a, b)), float("inf"))
                            for a in members_i
                            for b in members_j
                        )
                    else:  # average
                        # Average distance
                        dists = [
                            distances.get((min(a, b), max(a, b)), float("inf"))
                            for a in members_i
                            for b in members_j
                        ]
                        valid_dists = [d for d in dists if d != float("inf")]
                        dist = np.mean(valid_dists) if valid_dists else float("inf")

                    if dist < min_dist:
                        min_dist = dist
                        best_pair = (i, j)

            if best_pair is None or min_dist == float("inf"):
                # No more merges possible (disconnected graph)
                break

            # Merge the two clusters
            i, j = best_pair

            # Update union-find: merge j into i
            for member in cluster_members[j]:
                parent[member] = i

            # Update cluster members
            cluster_members[i] = cluster_members[i] | cluster_members[j]
            del cluster_members[j]

            # Record merge (using original node indices)
            merges.append((i, j, min_dist, len(cluster_members[i])))

            # Update active clusters
            active_clusters.remove(j)

        return merges

    def _divisive_clustering(self, graph: nx.Graph) -> List[Tuple]:
        """Top-down hierarchical clustering (similar to Girvan-Newman).

        Start with all nodes in one community, recursively split.

        Args:
            graph: Input graph

        Returns:
            List of split steps
        """
        if graph.number_of_nodes() == 0:
            return []

        # Use girvan_newman algorithm
        return self._girvan_newman_splits(graph)

    def _girvan_newman_splits(self, graph: nx.Graph) -> List[Tuple]:
        """Implement Girvan-Newman edge removal algorithm.

        Iteratively remove edges with highest betweenness.

        Args:
            graph: Input graph

        Returns:
            List of split information
        """
        G = graph.copy()
        splits = []

        # Track community evolution
        all_communities = [set(G.nodes())]

        # Iteratively remove edges
        while G.number_of_edges() > 0:
            # Calculate edge betweenness
            edge_betweenness = nx.edge_betweenness_centrality(G, weight=self.weight)

            if not edge_betweenness:
                break

            # Remove edge with highest betweenness
            max_edge = max(edge_betweenness, key=edge_betweenness.get)
            G.remove_edge(*max_edge)

            # Check if graph split into more components
            components = list(nx.connected_components(G))

            if len(components) > len(all_communities):
                # Graph split - record it
                splits.append(
                    (
                        len(all_communities),
                        len(components),
                        edge_betweenness[max_edge],
                        max(len(c) for c in components),
                    )
                )
                all_communities = components

        return splits

    def cut_at_level(self, n_communities: int, nodes: List[Any]) -> List[Set[Any]]:
        """Cut dendrogram to get specific number of communities.

        Args:
            n_communities: Desired number of communities
            nodes: Original node list

        Returns:
            List of community sets

        Raises:
            ComputationError: If fit() not called first
        """
        if self.dendrogram_ is None:
            raise ComputationError("Must call fit() before cut_at_level()")

        if not nodes:
            return []

        n_nodes = len(nodes)

        if n_communities <= 0:
            return [set(nodes)]

        if n_communities >= n_nodes:
            return [{node} for node in nodes]

        if not self.dendrogram_:
            # No merges recorded, all nodes separate
            return [{node} for node in nodes]

        # Build union-find structure by applying merges
        parent = list(range(n_nodes))

        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]

        def union(x, y):
            px, py = find(x), find(y)
            if px != py:
                parent[px] = py

        # Apply first (n_nodes - n_communities) merges
        # Each merge reduces the number of clusters by 1
        merges_to_apply = n_nodes - n_communities

        for merge_idx in range(min(merges_to_apply, len(self.dendrogram_))):
            cluster_i, cluster_j, dist, size = self.dendrogram_[merge_idx]

            # The merge represents: cluster_i absorbed cluster_j
            # We need to union all members of both clusters
            # In our implementation, cluster_i and cluster_j are root representatives
            # So we just union them directly
            if cluster_i < n_nodes and cluster_j < n_nodes:
                union(cluster_i, cluster_j)

        # Group nodes by their root
        communities = defaultdict(set)
        for i, node in enumerate(nodes):
            root = find(i)
            communities[root].add(node)

        result = list(communities.values())

        # Handle edge case where we have disconnected components
        # If we didn't get exactly n_communities, adjust
        if len(result) > n_communities:
            # Too many communities - merge smallest ones
            while len(result) > n_communities:
                smallest = min(result, key=len)
                result.remove(smallest)
                # Merge into largest
                if result:
                    largest = max(result, key=len)
                    largest.update(smallest)
        elif len(result) < n_communities:
            # Too few communities - split largest
            while len(result) < n_communities and any(len(c) > 1 for c in result):
                largest = max((c for c in result if len(c) > 1), key=len, default=None)
                if largest is None:
                    break
                result.remove(largest)
                items = list(largest)
                mid = len(items) // 2
                result.append(set(items[:mid]))
                result.append(set(items[mid:]))

        return result


def hierarchical_clustering(
    graph: nx.Graph,
    method: str = "agglomerative",
    linkage: str = "average",
    n_communities: Optional[int] = None,
    weight: str = "weight",
) -> List[Set[Any]]:
    """Perform hierarchical community detection.

    Args:
        graph: Input graph
        method: 'agglomerative' or 'divisive'
        linkage: Linkage criterion for agglomerative
        n_communities: Number of communities (if None, uses modularity)
        weight: Edge weight attribute

    Returns:
        List of community sets
    """
    if graph.number_of_nodes() == 0:
        return []

    nodes = list(graph.nodes())

    # Build hierarchical clustering
    detector = HierarchicalCommunityDetector(method, linkage, weight)
    detector.fit(graph)

    if n_communities is None:
        # Find optimal number using modularity
        best_Q = -1
        best_comms = None

        for k in range(1, min(graph.number_of_nodes() + 1, 20)):
            try:
                comms = detector.cut_at_level(k, nodes)
                if not comms:
                    break
                Q = calculate_modularity(graph, comms, weight=weight)
                if Q > best_Q:
                    best_Q = Q
                    best_comms = comms
            except Exception:
                break

        return best_comms if best_comms else [{node} for node in graph.nodes()]
    else:
        return detector.cut_at_level(n_communities, nodes)


def girvan_newman(
    graph: nx.Graph, k: Optional[int] = None, weight: str = "weight"
) -> List[Set[Any]]:
    """Girvan-Newman community detection via edge betweenness.

    Divisive method: iteratively remove edges with highest betweenness.

    Args:
        graph: Input graph
        k: Number of communities (if None, uses modularity)
        weight: Edge weight attribute

    Returns:
        List of community sets

    Reference:
        Girvan & Newman (2002). Community structure in social and biological networks.
    """
    if graph.number_of_nodes() == 0:
        return []

    G = graph.copy()

    # Track community evolution
    communities_evolution = []

    # Start with all nodes in one community
    communities_evolution.append([set(G.nodes())])

    # Iteratively remove edges
    while G.number_of_edges() > 0:
        # Calculate edge betweenness
        edge_betweenness = nx.edge_betweenness_centrality(G, weight=weight)

        if not edge_betweenness:
            break

        # Remove edge with highest betweenness
        max_edge = max(edge_betweenness, key=edge_betweenness.get)
        G.remove_edge(*max_edge)

        # Get current communities
        components = [set(c) for c in nx.connected_components(G)]
        communities_evolution.append(components)

        # Stop if reached desired number
        if k is not None and len(components) >= k:
            break

    # If k specified, return that level
    if k is not None:
        for comms in communities_evolution:
            if len(comms) >= k:
                return comms
        return communities_evolution[-1]

    # Otherwise, find best modularity
    best_Q = -1
    best_comms = communities_evolution[0]

    for comms in communities_evolution:
        Q = calculate_modularity(graph, comms, weight=weight)
        if Q > best_Q:
            best_Q = Q
            best_comms = comms

    return best_comms


def dendrogram_cut(
    dendrogram: List[Tuple], n_communities: int, n_nodes: Optional[int] = None
) -> Dict[Any, int]:
    """Cut dendrogram at level to get n communities.

    Args:
        dendrogram: Merge history from hierarchical clustering
        n_communities: Desired number of communities
        n_nodes: Number of original nodes (if None, inferred from dendrogram)

    Returns:
        Dictionary mapping nodes to community IDs
    """
    if not dendrogram or n_communities <= 0:
        return {}

    # Infer number of nodes from dendrogram if not provided
    if n_nodes is None:
        # Find maximum node index in dendrogram
        max_node = 0
        for node1, node2, dist, size in dendrogram:
            max_node = max(max_node, node1, node2)
        n_nodes = max_node + 1

    if n_communities >= n_nodes:
        return {i: i for i in range(n_nodes)}

    # Initialize: each node in its own community
    parent = list(range(n_nodes))

    def find(x):
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    # Apply first n_nodes - n_communities merges
    merges_to_apply = n_nodes - n_communities

    for i in range(min(merges_to_apply, len(dendrogram))):
        node1, node2, dist, size = dendrogram[i]
        if node1 < n_nodes and node2 < n_nodes:
            union(node1, node2)

    # Group nodes by root and renumber
    roots = {}
    next_id = 0
    communities = {}

    for i in range(n_nodes):
        root = find(i)
        if root not in roots:
            roots[root] = next_id
            next_id += 1
        communities[i] = roots[root]

    return communities


def assess_hierarchical_structure(
    graph: nx.Graph, method: str = "agglomerative", weight: str = "weight"
) -> NetworkResult:
    """Comprehensive hierarchical community structure assessment.

    Args:
        graph: Input graph
        method: Clustering method
        weight: Edge weight attribute

    Returns:
        NetworkResult with hierarchical metrics
    """
    if graph.number_of_nodes() == 0:
        return NetworkResult(
            metrics={"optimal_k": 0, "max_modularity": 0.0},
            nodes={},
            metadata={"communities": [], "method": method},
        )

    nodes = list(graph.nodes())

    # Perform clustering
    detector = HierarchicalCommunityDetector(method=method, weight=weight)
    detector.fit(graph)

    # Try different numbers of communities
    modularity_scores = []
    all_communities = []

    for k in range(2, min(graph.number_of_nodes(), 15)):
        try:
            comms = detector.cut_at_level(k, nodes)
            if not comms:
                break
            Q = calculate_modularity(graph, comms, weight=weight)
            modularity_scores.append(Q)
            all_communities.append(comms)
        except:
            break

    # Find optimal
    if modularity_scores:
        best_idx = np.argmax(modularity_scores)
        best_k = best_idx + 2
        best_Q = modularity_scores[best_idx]
        best_comms = all_communities[best_idx]
    else:
        best_k = 1
        best_Q = 0.0
        best_comms = [set(graph.nodes())]

    # Community sizes
    sizes = [len(c) for c in best_comms]

    return NetworkResult(
        metrics={
            "optimal_k": best_k,
            "max_modularity": best_Q,
            "num_levels": len(modularity_scores),
            "avg_community_size": np.mean(sizes) if sizes else 0,
        },
        nodes={
            node: {"community": comm_id} for comm_id, comm in enumerate(best_comms) for node in comm
        },
        metadata={
            "communities": best_comms,
            "modularity_by_k": modularity_scores,
            "method": method,
        },
    )
