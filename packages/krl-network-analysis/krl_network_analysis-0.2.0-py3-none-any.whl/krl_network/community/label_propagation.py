"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Label propagation methods for community detection.
"""

import random
from collections import Counter, defaultdict
from typing import Any, Dict, List, Optional, Set

import networkx as nx
import numpy as np

from krl_network.community.modularity import calculate_modularity
from krl_network.core.exceptions import ComputationError
from krl_network.core.result import NetworkResult


def label_propagation(
    graph: nx.Graph,
    max_iterations: int = 100,
    weight: str = "weight",
    random_state: Optional[int] = None,
) -> List[Set[Any]]:
    """Asynchronous label propagation algorithm.

    Nodes adopt the label that most of their neighbors have.
    Very fast O(m) but non-deterministic.

    Args:
        graph: Input graph
        max_iterations: Maximum iterations
        weight: Edge weight attribute
        random_state: Random seed

    Returns:
        List of community sets

    Reference:
        Raghavan et al. (2007). Near linear time algorithm to detect community structures.
    """
    if graph.number_of_nodes() == 0:
        return []

    if random_state is not None:
        random.seed(random_state)
        np.random.seed(random_state)

    # Initialize: each node has unique label
    labels = {node: i for i, node in enumerate(graph.nodes())}

    # Iterate
    for iteration in range(max_iterations):
        # Random node order
        nodes = list(graph.nodes())
        random.shuffle(nodes)

        changed = False

        for node in nodes:
            # Count neighbor labels (weighted)
            neighbor_labels = Counter()

            for neighbor in graph.neighbors(node):
                w = graph[node][neighbor].get(weight, 1.0)
                neighbor_labels[labels[neighbor]] += w

            if not neighbor_labels:
                continue

            # Find most common label
            max_weight = max(neighbor_labels.values())
            candidates = [label for label, w in neighbor_labels.items() if w == max_weight]

            # Break ties randomly
            new_label = random.choice(candidates)

            if new_label != labels[node]:
                labels[node] = new_label
                changed = True

        # Converged?
        if not changed:
            break

    # Convert to communities
    communities = defaultdict(set)
    for node, label in labels.items():
        communities[label].add(node)

    return list(communities.values())


def semi_supervised_label_propagation(
    graph: nx.Graph, seed_labels: Dict[Any, int], max_iterations: int = 100, weight: str = "weight"
) -> List[Set[Any]]:
    """Semi-supervised label propagation with seed labels.

    Some nodes have fixed labels that don't change.

    Args:
        graph: Input graph
        seed_labels: Dict mapping seed nodes to their fixed labels
        max_iterations: Maximum iterations
        weight: Edge weight attribute

    Returns:
        List of community sets
    """
    if graph.number_of_nodes() == 0:
        return []

    # Initialize labels
    labels = {}
    next_label = 0

    for node in graph.nodes():
        if node in seed_labels:
            labels[node] = seed_labels[node]
            next_label = max(next_label, seed_labels[node] + 1)
        else:
            labels[node] = next_label
            next_label += 1

    # Iterate (seeds don't change)
    for iteration in range(max_iterations):
        nodes = [n for n in graph.nodes() if n not in seed_labels]
        random.shuffle(nodes)

        changed = False

        for node in nodes:
            # Count neighbor labels
            neighbor_labels = Counter()

            for neighbor in graph.neighbors(node):
                w = graph[node][neighbor].get(weight, 1.0)
                neighbor_labels[labels[neighbor]] += w

            if not neighbor_labels:
                continue

            # Most common label
            max_weight = max(neighbor_labels.values())
            candidates = [label for label, w in neighbor_labels.items() if w == max_weight]
            new_label = random.choice(candidates)

            if new_label != labels[node]:
                labels[node] = new_label
                changed = True

        if not changed:
            break

    # Convert to communities
    communities = defaultdict(set)
    for node, label in labels.items():
        communities[label].add(node)

    return list(communities.values())


def synchronous_label_propagation(
    graph: nx.Graph,
    max_iterations: int = 100,
    weight: str = "weight",
    random_state: Optional[int] = None,
) -> List[Set[Any]]:
    """Synchronous label propagation.

    All nodes update labels simultaneously (more stable than async).

    Args:
        graph: Input graph
        max_iterations: Maximum iterations
        weight: Edge weight attribute
        random_state: Random seed

    Returns:
        List of community sets
    """
    if graph.number_of_nodes() == 0:
        return []

    if random_state is not None:
        random.seed(random_state)
        np.random.seed(random_state)

    # Initialize
    labels = {node: i for i, node in enumerate(graph.nodes())}

    for iteration in range(max_iterations):
        new_labels = {}
        changed = False

        for node in graph.nodes():
            # Count neighbor labels
            neighbor_labels = Counter()

            for neighbor in graph.neighbors(node):
                w = graph[node][neighbor].get(weight, 1.0)
                neighbor_labels[labels[neighbor]] += w

            if not neighbor_labels:
                new_labels[node] = labels[node]
                continue

            # Most common
            max_weight = max(neighbor_labels.values())
            candidates = [label for label, w in neighbor_labels.items() if w == max_weight]
            new_label = random.choice(candidates)

            new_labels[node] = new_label

            if new_label != labels[node]:
                changed = True

        labels = new_labels

        if not changed:
            break

    # Convert to communities
    communities = defaultdict(set)
    for node, label in labels.items():
        communities[label].add(node)

    return list(communities.values())


def multi_label_propagation(
    graph: nx.Graph,
    max_labels_per_node: int = 3,
    max_iterations: int = 100,
    weight: str = "weight",
    random_state: Optional[int] = None,
) -> Dict[Any, Set[int]]:
    """Multi-label propagation for overlapping communities.

    Nodes can belong to multiple communities.

    Args:
        graph: Input graph
        max_labels_per_node: Maximum labels per node
        max_iterations: Maximum iterations
        weight: Edge weight attribute
        random_state: Random seed

    Returns:
        Dict mapping nodes to sets of community labels
    """
    if graph.number_of_nodes() == 0:
        return {}

    if random_state is not None:
        random.seed(random_state)
        np.random.seed(random_state)

    # Initialize: each node has unique label set
    labels = {node: {i} for i, node in enumerate(graph.nodes())}

    for iteration in range(max_iterations):
        nodes = list(graph.nodes())
        random.shuffle(nodes)

        changed = False

        for node in nodes:
            # Count neighbor labels
            neighbor_labels = Counter()

            for neighbor in graph.neighbors(node):
                w = graph[node][neighbor].get(weight, 1.0)
                for label in labels[neighbor]:
                    neighbor_labels[label] += w

            if not neighbor_labels:
                continue

            # Take top k most common labels
            most_common = neighbor_labels.most_common(max_labels_per_node)
            new_labels = {label for label, _ in most_common}

            if new_labels != labels[node]:
                labels[node] = new_labels
                changed = True

        if not changed:
            break

    return labels


def assess_label_propagation_structure(
    graph: nx.Graph, n_trials: int = 10, max_iterations: int = 100, weight: str = "weight"
) -> NetworkResult:
    """Assess community structure using label propagation.

    Runs multiple trials and selects best result.

    Args:
        graph: Input graph
        n_trials: Number of trials (LP is stochastic)
        max_iterations: Maximum iterations per trial
        weight: Edge weight attribute

    Returns:
        NetworkResult with best communities found
    """
    if graph.number_of_nodes() == 0:
        return NetworkResult(
            metrics={"num_communities": 0, "modularity": 0.0},
            nodes={},
            metadata={"method": "label_propagation"},
        )

    best_Q = -1
    best_comms = None
    all_results = []

    for trial in range(n_trials):
        comms = label_propagation(
            graph, max_iterations=max_iterations, weight=weight, random_state=trial
        )

        Q = calculate_modularity(graph, comms, weight=weight)
        all_results.append((Q, len(comms)))

        if Q > best_Q:
            best_Q = Q
            best_comms = comms

    # Stability: how consistent are results?
    num_comms = [n for _, n in all_results]
    stability = 1.0 - (np.std(num_comms) / (np.mean(num_comms) + 1e-10))

    sizes = [len(c) for c in best_comms]

    return NetworkResult(
        metrics={
            "num_communities": len(best_comms),
            "modularity": best_Q,
            "stability": stability,
            "avg_community_size": np.mean(sizes) if sizes else 0,
        },
        nodes={
            node: {"community": comm_id} for comm_id, comm in enumerate(best_comms) for node in comm
        },
        metadata={
            "communities": best_comms,
            "method": "label_propagation",
            "n_trials": n_trials,
            "all_modularity_scores": [Q for Q, _ in all_results],
        },
    )
