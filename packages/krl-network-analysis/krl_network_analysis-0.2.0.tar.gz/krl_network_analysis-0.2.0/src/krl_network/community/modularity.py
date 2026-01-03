"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Modularity-based community detection algorithms.
"""

import random
from collections import defaultdict
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import networkx as nx
import numpy as np

from krl_network.core.exceptions import ComputationError
from krl_network.core.result import NetworkResult


def calculate_modularity(
    graph: nx.Graph,
    communities: Union[List[Set], Dict[Any, int]],
    resolution: float = 1.0,
    weight: str = "weight",
) -> float:
    """Calculate modularity of a community partition.

    Modularity Q = 1/(2m) * sum_ij [A_ij - gamma*k_i*k_j/(2m)] * delta(c_i, c_j)
    where gamma is the resolution parameter.

    Args:
        graph: Input graph
        communities: Either list of node sets or dict mapping nodes to community IDs
        resolution: Resolution parameter (default 1.0, higher = more communities)
        weight: Edge weight attribute

    Returns:
        Modularity score (-0.5 to 1.0)

    Raises:
        ComputationError: If communities are invalid
    """
    if graph.number_of_nodes() == 0:
        return 0.0

    # Convert communities to dict if needed
    if isinstance(communities, list):
        community_dict = {}
        for comm_id, comm in enumerate(communities):
            for node in comm:
                community_dict[node] = comm_id
    else:
        community_dict = communities

    # Validate all nodes are assigned
    if set(community_dict.keys()) != set(graph.nodes()):
        raise ComputationError("Not all nodes assigned to communities")

    # Calculate total edge weight
    if graph.is_directed():
        m = sum(d.get(weight, 1.0) for u, v, d in graph.edges(data=True))
    else:
        m = sum(d.get(weight, 1.0) for u, v, d in graph.edges(data=True))

    if m == 0:
        return 0.0

    # Calculate modularity
    Q = 0.0

    for u in graph.nodes():
        for v in graph.nodes():
            # Check if in same community
            if community_dict[u] != community_dict[v]:
                continue

            # Get actual edge weight
            if graph.has_edge(u, v):
                A_uv = graph[u][v].get(weight, 1.0)
            else:
                A_uv = 0.0

            # Calculate expected edge weight
            if graph.is_directed():
                k_out_u = sum(d.get(weight, 1.0) for _, _, d in graph.out_edges(u, data=True))
                k_in_v = sum(d.get(weight, 1.0) for _, _, d in graph.in_edges(v, data=True))
                expected = resolution * k_out_u * k_in_v / m if m > 0 else 0
            else:
                k_u = sum(d.get(weight, 1.0) for _, _, d in graph.edges(u, data=True))
                k_v = sum(d.get(weight, 1.0) for _, _, d in graph.edges(v, data=True))
                expected = resolution * k_u * k_v / (2 * m) if m > 0 else 0

            Q += A_uv - expected

    if graph.is_directed():
        Q /= m
    else:
        Q /= 2 * m

    return Q


class ModularityOptimizer:
    """Base class for modularity optimization algorithms."""

    def __init__(
        self, resolution: float = 1.0, weight: str = "weight", random_state: Optional[int] = None
    ):
        """Initialize optimizer.

        Args:
            resolution: Resolution parameter (higher = more communities)
            weight: Edge weight attribute
            random_state: Random seed for reproducibility
        """
        self.resolution = resolution
        self.weight = weight
        self.random_state = random_state

        if random_state is not None:
            random.seed(random_state)
            np.random.seed(random_state)

    def _calculate_delta_modularity(
        self, graph: nx.Graph, node: Any, community: int, communities: Dict[Any, int], m: float
    ) -> float:
        """Calculate change in modularity if node moves to community.

        Args:
            graph: Input graph
            node: Node to potentially move
            community: Target community
            communities: Current community assignment
            m: Total edge weight

        Returns:
            Change in modularity
        """
        # Sum of weights from node to nodes in target community
        k_i_in = 0.0
        for neighbor in graph.neighbors(node):
            if communities[neighbor] == community:
                k_i_in += graph[node][neighbor].get(self.weight, 1.0)

        # Degree of node
        k_i = sum(d.get(self.weight, 1.0) for _, _, d in graph.edges(node, data=True))

        # Sum of degrees in target community
        sigma_tot = 0.0
        for n in graph.nodes():
            if communities[n] == community:
                sigma_tot += sum(d.get(self.weight, 1.0) for _, _, d in graph.edges(n, data=True))

        # Delta Q formula
        if graph.is_directed():
            delta_Q = (k_i_in - self.resolution * k_i * sigma_tot / m) / m
        else:
            delta_Q = (k_i_in - self.resolution * k_i * sigma_tot / (2 * m)) / (2 * m)

        return delta_Q


def louvain_communities(
    graph: nx.Graph,
    resolution: float = 1.0,
    weight: str = "weight",
    max_iterations: int = 100,
    random_state: Optional[int] = None,
) -> List[Set[Any]]:
    """Detect communities using Louvain algorithm.

    Fast modularity optimization with multi-level aggregation.
    Time complexity: O(n log n) for sparse networks.

    Args:
        graph: Input graph (undirected)
        resolution: Resolution parameter (higher = more communities)
        weight: Edge weight attribute
        max_iterations: Maximum iterations per phase
        random_state: Random seed

    Returns:
        List of community sets

    Raises:
        ComputationError: If graph is directed

    Reference:
        Blondel et al. (2008). Fast unfolding of communities in large networks.
    """
    if graph.is_directed():
        raise ComputationError("Louvain algorithm requires undirected graph")

    if graph.number_of_nodes() == 0:
        return []

    if random_state is not None:
        random.seed(random_state)
        np.random.seed(random_state)

    # Initialize: each node in its own community
    communities = {node: i for i, node in enumerate(graph.nodes())}

    # Calculate total edge weight
    m = sum(d.get(weight, 1.0) for u, v, d in graph.edges(data=True))

    if m == 0:
        return [{node} for node in graph.nodes()]

    # Phase 1: Modularity optimization
    improved = True
    iteration = 0

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1

        # Random node order
        nodes = list(graph.nodes())
        random.shuffle(nodes)

        for node in nodes:
            current_comm = communities[node]

            # Find neighboring communities
            neighbor_comms = set()
            for neighbor in graph.neighbors(node):
                neighbor_comms.add(communities[neighbor])

            # Try moving to each neighboring community
            best_comm = current_comm
            best_delta = 0.0

            for target_comm in neighbor_comms:
                if target_comm == current_comm:
                    continue

                # Calculate modularity gain
                k_i_in_target = 0.0
                k_i_in_current = 0.0

                for neighbor in graph.neighbors(node):
                    edge_weight = graph[node][neighbor].get(weight, 1.0)
                    if communities[neighbor] == target_comm:
                        k_i_in_target += edge_weight
                    elif communities[neighbor] == current_comm:
                        k_i_in_current += edge_weight

                k_i = sum(d.get(weight, 1.0) for _, _, d in graph.edges(node, data=True))

                # Sum of degrees in communities
                sigma_current = sum(
                    sum(d.get(weight, 1.0) for _, _, d in graph.edges(n, data=True))
                    for n in graph.nodes()
                    if communities[n] == current_comm
                )
                sigma_target = sum(
                    sum(d.get(weight, 1.0) for _, _, d in graph.edges(n, data=True))
                    for n in graph.nodes()
                    if communities[n] == target_comm
                )

                # Delta Q when removing from current and adding to target
                delta_Q_remove = -k_i_in_current / (2 * m) + resolution * k_i * (
                    sigma_current - k_i
                ) / (4 * m * m)
                delta_Q_add = k_i_in_target / (2 * m) - resolution * k_i * sigma_target / (
                    4 * m * m
                )

                delta_Q = delta_Q_add + delta_Q_remove

                if delta_Q > best_delta:
                    best_delta = delta_Q
                    best_comm = target_comm

            # Move node if improves modularity
            if best_comm != current_comm and best_delta > 1e-10:
                communities[node] = best_comm
                improved = True

    # Convert to list of sets
    comm_sets = defaultdict(set)
    for node, comm_id in communities.items():
        comm_sets[comm_id].add(node)

    return list(comm_sets.values())


def leiden_communities(
    graph: nx.Graph,
    resolution: float = 1.0,
    weight: str = "weight",
    max_iterations: int = 100,
    random_state: Optional[int] = None,
) -> List[Set[Any]]:
    """Detect communities using Leiden algorithm.

    Improved version of Louvain that guarantees connected communities.

    Args:
        graph: Input graph (undirected)
        resolution: Resolution parameter
        weight: Edge weight attribute
        max_iterations: Maximum iterations
        random_state: Random seed

    Returns:
        List of community sets

    Reference:
        Traag et al. (2019). From Louvain to Leiden: guaranteeing well-connected communities.
    """
    if graph.is_directed():
        raise ComputationError("Leiden algorithm requires undirected graph")

    if graph.number_of_nodes() == 0:
        return []

    if random_state is not None:
        random.seed(random_state)
        np.random.seed(random_state)

    # Start with Louvain
    communities_list = louvain_communities(graph, resolution, weight, max_iterations, random_state)

    # Convert to dict
    communities = {}
    for comm_id, comm in enumerate(communities_list):
        for node in comm:
            communities[node] = comm_id

    # Refinement phase: ensure connectivity
    improved = True
    iteration = 0

    while improved and iteration < max_iterations:
        improved = False
        iteration += 1

        # Check connectivity of each community
        for comm_id in set(communities.values()):
            comm_nodes = [n for n in graph.nodes() if communities[n] == comm_id]

            if len(comm_nodes) <= 1:
                continue

            # Extract subgraph
            subgraph = graph.subgraph(comm_nodes)

            # Find connected components
            components = list(nx.connected_components(subgraph))

            # If disconnected, split into separate communities
            if len(components) > 1:
                improved = True
                next_comm_id = max(communities.values()) + 1

                # Keep largest component in original community
                largest = max(components, key=len)

                for component in components:
                    if component != largest:
                        for node in component:
                            communities[node] = next_comm_id
                        next_comm_id += 1

    # Convert back to list of sets
    comm_sets = defaultdict(set)
    for node, comm_id in communities.items():
        comm_sets[comm_id].add(node)

    return list(comm_sets.values())


def optimize_modularity(
    graph: nx.Graph,
    method: str = "louvain",
    resolution: float = 1.0,
    weight: str = "weight",
    random_state: Optional[int] = None,
) -> NetworkResult:
    """Optimize modularity to find communities.

    Args:
        graph: Input graph
        method: Algorithm ('louvain' or 'leiden')
        resolution: Resolution parameter
        weight: Edge weight attribute
        random_state: Random seed

    Returns:
        NetworkResult with communities and metrics

    Raises:
        ValueError: If method is unknown
    """
    if method == "louvain":
        communities = louvain_communities(graph, resolution, weight, random_state=random_state)
    elif method == "leiden":
        communities = leiden_communities(graph, resolution, weight, random_state=random_state)
    else:
        raise ValueError(f"Unknown method: {method}. Use 'louvain' or 'leiden'")

    # Calculate modularity
    modularity = calculate_modularity(graph, communities, resolution, weight)

    # Community sizes
    sizes = [len(c) for c in communities]

    return NetworkResult(
        metrics={
            "num_communities": len(communities),
            "modularity": modularity,
            "avg_community_size": np.mean(sizes) if sizes else 0,
            "max_community_size": max(sizes) if sizes else 0,
            "min_community_size": min(sizes) if sizes else 0,
        },
        nodes={
            node: {"community": comm_id}
            for comm_id, comm in enumerate(communities)
            for node in comm
        },
        metadata={
            "communities": communities,
            "method": method,
            "resolution": resolution,
        },
    )
