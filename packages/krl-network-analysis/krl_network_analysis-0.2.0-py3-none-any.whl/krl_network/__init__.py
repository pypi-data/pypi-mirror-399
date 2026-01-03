# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
KRL Network Analysis - Economic network analysis tools.

This package provides comprehensive network analysis capabilities for
economic and social networks, including:

- Community Detection: Louvain, Leiden, spectral clustering, label propagation
- Centrality Metrics: Degree, betweenness, closeness, eigenvector, PageRank
- Network Statistics: Clustering, path analysis, density, assortativity
- Economic Networks: Supply chain, input-output, trade, regional analysis

Example:
    >>> from krl_network import louvain_communities, degree_centrality
    >>> from krl_network import SupplyChainNetwork
    >>> 
    >>> # Detect communities
    >>> communities = louvain_communities(graph)
    >>> 
    >>> # Calculate centrality
    >>> centrality = degree_centrality(graph)
"""

from krl_network.__version__ import __author__, __license__, __version__

# =============================================================================
# Core Infrastructure
# =============================================================================
from krl_network.core import (
    BaseNetwork,
    NetworkConfig,
    NetworkResult,
    NetworkError,
    InvalidNetworkError,
    ComputationError,
    DataError,
)

# =============================================================================
# Community Detection
# =============================================================================
from krl_network.community import (
    # Modularity-based
    calculate_modularity,
    louvain_communities,
    leiden_communities,
    optimize_modularity,
    ModularityOptimizer,
    # Hierarchical
    hierarchical_clustering,
    girvan_newman,
    dendrogram_cut,
    HierarchicalCommunityDetector,
    assess_hierarchical_structure,
    # Spectral
    spectral_clustering,
    spectral_bisection,
    recursive_spectral_bisection,
    assess_spectral_structure,
    # Label propagation
    label_propagation,
    semi_supervised_label_propagation,
    synchronous_label_propagation,
    multi_label_propagation,
    assess_label_propagation_structure,
    # Overlapping
    clique_percolation,
    link_communities,
    ego_network_splitting,
    fuzzy_community_membership,
    assess_overlapping_communities,
    # Dynamics
    CommunityEvent,
    jaccard_similarity,
    match_communities,
    detect_community_events,
    track_communities_over_time,
    calculate_community_stability,
    community_lifecycle_analysis,
    detect_persistent_communities,
    analyze_community_evolution,
)

# =============================================================================
# Network Metrics
# =============================================================================
from krl_network.metrics import (
    # Centrality
    degree_centrality,
    betweenness_centrality,
    closeness_centrality,
    eigenvector_centrality,
    pagerank,
    katz_centrality,
    # Clustering
    clustering_coefficient,
    average_clustering,
    transitivity,
    triangles,
    # Path analysis
    shortest_path,
    all_pairs_shortest_path,
    average_shortest_path_length,
    diameter,
    eccentricity,
    # Statistics
    density,
    reciprocity,
    degree_assortativity,
    assortativity,
)

# =============================================================================
# Economic Networks
# =============================================================================
from krl_network.networks import (
    SupplyChainNetwork,
    RegionalNetwork,
    InputOutputNetwork,
    TradeNetwork,
)

# =============================================================================
# Public API
# =============================================================================
__all__ = [
    # Version
    "__version__",
    "__author__",
    "__license__",
    # Core
    "BaseNetwork",
    "NetworkConfig",
    "NetworkResult",
    "NetworkError",
    "InvalidNetworkError",
    "ComputationError",
    "DataError",
    # Community Detection - Modularity
    "calculate_modularity",
    "louvain_communities",
    "leiden_communities",
    "optimize_modularity",
    "ModularityOptimizer",
    # Community Detection - Hierarchical
    "hierarchical_clustering",
    "girvan_newman",
    "dendrogram_cut",
    "HierarchicalCommunityDetector",
    "assess_hierarchical_structure",
    # Community Detection - Spectral
    "spectral_clustering",
    "spectral_bisection",
    "recursive_spectral_bisection",
    "assess_spectral_structure",
    # Community Detection - Label Propagation
    "label_propagation",
    "semi_supervised_label_propagation",
    "synchronous_label_propagation",
    "multi_label_propagation",
    "assess_label_propagation_structure",
    # Community Detection - Overlapping
    "clique_percolation",
    "link_communities",
    "ego_network_splitting",
    "fuzzy_community_membership",
    "assess_overlapping_communities",
    # Community Detection - Dynamics
    "CommunityEvent",
    "jaccard_similarity",
    "match_communities",
    "detect_community_events",
    "track_communities_over_time",
    "calculate_community_stability",
    "community_lifecycle_analysis",
    "detect_persistent_communities",
    "analyze_community_evolution",
    # Centrality
    "degree_centrality",
    "betweenness_centrality",
    "closeness_centrality",
    "eigenvector_centrality",
    "pagerank",
    "katz_centrality",
    # Clustering Metrics
    "clustering_coefficient",
    "average_clustering",
    "transitivity",
    "triangles",
    # Path Analysis
    "shortest_path",
    "all_pairs_shortest_path",
    "average_shortest_path_length",
    "diameter",
    "eccentricity",
    # Network Statistics
    "density",
    "reciprocity",
    "degree_assortativity",
    "assortativity",
    # Economic Networks
    "SupplyChainNetwork",
    "RegionalNetwork",
    "InputOutputNetwork",
    "TradeNetwork",
]
