"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Community detection module.
"""

from krl_network.community.dynamics import (
    CommunityEvent,
    analyze_community_evolution,
    calculate_community_stability,
    community_lifecycle_analysis,
    detect_community_events,
    detect_persistent_communities,
    jaccard_similarity,
    match_communities,
    track_communities_over_time,
)
from krl_network.community.hierarchical import (
    HierarchicalCommunityDetector,
    assess_hierarchical_structure,
    dendrogram_cut,
    girvan_newman,
    hierarchical_clustering,
)
from krl_network.community.label_propagation import (
    assess_label_propagation_structure,
    label_propagation,
    multi_label_propagation,
    semi_supervised_label_propagation,
    synchronous_label_propagation,
)
from krl_network.community.modularity import (
    ModularityOptimizer,
    calculate_modularity,
    leiden_communities,
    louvain_communities,
    optimize_modularity,
)
from krl_network.community.overlapping import (
    assess_overlapping_communities,
    clique_percolation,
    ego_network_splitting,
    fuzzy_community_membership,
    link_communities,
)
from krl_network.community.spectral import (
    assess_spectral_structure,
    recursive_spectral_bisection,
    spectral_bisection,
    spectral_clustering,
)

__all__ = [
    # Modularity
    "calculate_modularity",
    "louvain_communities",
    "leiden_communities",
    "optimize_modularity",
    "ModularityOptimizer",
    # Hierarchical
    "hierarchical_clustering",
    "girvan_newman",
    "dendrogram_cut",
    "HierarchicalCommunityDetector",
    "assess_hierarchical_structure",
    # Spectral
    "spectral_clustering",
    "spectral_bisection",
    "recursive_spectral_bisection",
    "assess_spectral_structure",
    # Label propagation
    "label_propagation",
    "semi_supervised_label_propagation",
    "synchronous_label_propagation",
    "multi_label_propagation",
    "assess_label_propagation_structure",
    # Overlapping
    "clique_percolation",
    "link_communities",
    "ego_network_splitting",
    "fuzzy_community_membership",
    "assess_overlapping_communities",
    # Dynamics
    "CommunityEvent",
    "jaccard_similarity",
    "match_communities",
    "detect_community_events",
    "track_communities_over_time",
    "calculate_community_stability",
    "community_lifecycle_analysis",
    "detect_persistent_communities",
    "analyze_community_evolution",
]
