"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Tests for hierarchical community detection.
"""

import networkx as nx
import numpy as np
import pytest

from krl_network.community.hierarchical import (
    HierarchicalCommunityDetector,
    assess_hierarchical_structure,
    dendrogram_cut,
    girvan_newman,
    hierarchical_clustering,
)
from krl_network.core.exceptions import ComputationError


class TestHierarchicalCommunityDetector:
    """Test HierarchicalCommunityDetector class."""

    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = HierarchicalCommunityDetector(method="agglomerative", linkage="average")

        assert detector.method == "agglomerative"
        assert detector.linkage == "average"
        assert detector.dendrogram_ is None

    def test_detector_invalid_method(self):
        """Test error on invalid method."""
        with pytest.raises(ValueError):
            HierarchicalCommunityDetector(method="invalid")

    def test_detector_invalid_linkage(self):
        """Test error on invalid linkage."""
        with pytest.raises(ValueError):
            HierarchicalCommunityDetector(linkage="invalid")

    def test_detector_fit_agglomerative(self):
        """Test fitting with agglomerative method."""
        G = nx.karate_club_graph()

        detector = HierarchicalCommunityDetector(method="agglomerative")
        detector.fit(G)

        assert detector.dendrogram_ is not None
        assert isinstance(detector.dendrogram_, list)

    def test_detector_fit_divisive(self):
        """Test fitting with divisive method."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3)])

        detector = HierarchicalCommunityDetector(method="divisive")
        detector.fit(G)

        assert detector.dendrogram_ is not None

    def test_detector_cut_before_fit(self):
        """Test error when cutting before fit."""
        detector = HierarchicalCommunityDetector()

        with pytest.raises(ComputationError):
            detector.cut_at_level(2, [0, 1, 2])


class TestHierarchicalClustering:
    """Test hierarchical clustering function."""

    def test_hierarchical_clustering_basic(self):
        """Test basic hierarchical clustering."""
        G = nx.karate_club_graph()

        communities = hierarchical_clustering(G, n_communities=2)

        assert len(communities) == 2

        # All nodes should be assigned
        all_nodes = set()
        for comm in communities:
            all_nodes.update(comm)
        assert all_nodes == set(G.nodes())

    def test_hierarchical_clustering_agglomerative(self):
        """Test agglomerative clustering."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (3, 4), (4, 5)])

        communities = hierarchical_clustering(G, method="agglomerative", n_communities=2)

        assert len(communities) <= 2

    def test_hierarchical_clustering_divisive(self):
        """Test divisive clustering."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (3, 4)])

        communities = hierarchical_clustering(G, method="divisive", n_communities=2)

        assert len(communities) >= 1

    def test_hierarchical_clustering_linkage_methods(self):
        """Test different linkage methods."""
        G = nx.karate_club_graph()

        for linkage in ["single", "average", "complete"]:
            communities = hierarchical_clustering(
                G, method="agglomerative", linkage=linkage, n_communities=3
            )

            assert len(communities) >= 1

    def test_hierarchical_clustering_auto_k(self):
        """Test automatic k selection with modularity."""
        G = nx.Graph()
        # Two clear communities
        for i in range(5):
            for j in range(i + 1, 5):
                G.add_edge(i, j)
        for i in range(5, 10):
            for j in range(i + 1, 10):
                G.add_edge(i, j)
        G.add_edge(4, 5)

        communities = hierarchical_clustering(G, n_communities=None)

        # Should find 2-3 communities
        assert 1 <= len(communities) <= 5

    def test_hierarchical_clustering_weighted(self):
        """Test with weighted edges."""
        G = nx.Graph()
        G.add_edge(0, 1, weight=5.0)
        G.add_edge(1, 2, weight=5.0)
        G.add_edge(2, 3, weight=0.5)
        G.add_edge(3, 4, weight=5.0)

        communities = hierarchical_clustering(G, weight="weight", n_communities=2)

        assert len(communities) >= 1


class TestGirvanNewman:
    """Test Girvan-Newman algorithm."""

    def test_girvan_newman_basic(self):
        """Test basic Girvan-Newman detection."""
        G = nx.karate_club_graph()

        communities = girvan_newman(G, k=2)

        assert len(communities) >= 2

        # All nodes assigned
        all_nodes = set()
        for comm in communities:
            all_nodes.update(comm)
        assert all_nodes == set(G.nodes())

    def test_girvan_newman_known_structure(self):
        """Test on graph with known structure."""
        # Two cliques connected by bridge
        G = nx.Graph()
        # Clique 1
        for i in range(4):
            for j in range(i + 1, 4):
                G.add_edge(i, j)
        # Clique 2
        for i in range(4, 8):
            for j in range(i + 1, 8):
                G.add_edge(i, j)
        # Bridge
        G.add_edge(3, 4)

        communities = girvan_newman(G, k=2)

        # Should find 2 communities
        assert len(communities) == 2

        # Check communities are roughly balanced
        sizes = [len(c) for c in communities]
        assert min(sizes) >= 3

    def test_girvan_newman_auto_k(self):
        """Test automatic k with modularity."""
        G = nx.karate_club_graph()

        communities = girvan_newman(G, k=None)

        # Should find reasonable number
        assert 2 <= len(communities) <= 10

    def test_girvan_newman_weighted(self):
        """Test with weighted edges."""
        G = nx.Graph()
        # Strong community 1
        G.add_edge(0, 1, weight=10.0)
        G.add_edge(1, 2, weight=10.0)
        # Strong community 2
        G.add_edge(3, 4, weight=10.0)
        G.add_edge(4, 5, weight=10.0)
        # Weak bridge (should be removed first)
        G.add_edge(2, 3, weight=1.0)

        communities = girvan_newman(G, k=2, weight="weight")

        assert len(communities) == 2

    def test_girvan_newman_progressive_split(self):
        """Test progressive splitting."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])

        # Test different k values
        comms_2 = girvan_newman(G, k=2)
        comms_3 = girvan_newman(G, k=3)

        assert len(comms_2) >= 2
        assert len(comms_3) >= len(comms_2)

    def test_girvan_newman_empty_graph(self):
        """Test on empty graph."""
        G = nx.Graph()
        communities = girvan_newman(G)

        assert communities == []

    def test_girvan_newman_single_node(self):
        """Test on single node."""
        G = nx.Graph()
        G.add_node(0)

        communities = girvan_newman(G)

        assert len(communities) == 1
        assert communities[0] == {0}


class TestDendrogramCut:
    """Test dendrogram cutting."""

    def test_dendrogram_cut_basic(self):
        """Test basic dendrogram cutting."""
        # Simple merge history - flat structure
        dendrogram = [
            (0, 1, 0.1, 2),  # Merge 0 and 1
            (2, 3, 0.2, 2),  # Merge 2 and 3
        ]

        communities = dendrogram_cut(dendrogram, n_communities=2)

        # Should have 2 communities
        assert len(set(communities.values())) == 2
        # 0 and 1 should be together, 2 and 3 should be together
        assert communities[0] == communities[1]
        assert communities[2] == communities[3]
        assert communities[0] != communities[2]

    def test_dendrogram_cut_all_separate(self):
        """Test cutting to get all nodes separate."""
        dendrogram = [(0, 1, 0.1, 2), (2, 3, 0.2, 2)]

        communities = dendrogram_cut(dendrogram, n_communities=4)

        # All nodes in separate communities
        assert len(set(communities.values())) == 4

    def test_dendrogram_cut_empty(self):
        """Test on empty dendrogram."""
        communities = dendrogram_cut([], n_communities=2)

        assert communities == {}

    def test_dendrogram_cut_invalid_k(self):
        """Test with invalid k."""
        dendrogram = [(0, 1, 0.1, 2)]

        communities = dendrogram_cut(dendrogram, n_communities=0)

        assert communities == {}


class TestAssessHierarchicalStructure:
    """Test hierarchical structure assessment."""

    def test_assess_structure_basic(self):
        """Test basic structure assessment."""
        G = nx.karate_club_graph()

        result = assess_hierarchical_structure(G)

        assert "optimal_k" in result.metrics
        assert "max_modularity" in result.metrics
        assert result.metrics["optimal_k"] >= 1
        assert result.metrics["max_modularity"] >= 0

    def test_assess_structure_method_selection(self):
        """Test different methods."""
        G = nx.karate_club_graph()

        result_agg = assess_hierarchical_structure(G, method="agglomerative")
        result_div = assess_hierarchical_structure(G, method="divisive")

        assert result_agg.metadata["method"] == "agglomerative"
        assert result_div.metadata["method"] == "divisive"

    def test_assess_structure_metadata(self):
        """Test metadata includes communities."""
        G = nx.karate_club_graph()

        result = assess_hierarchical_structure(G)

        assert "communities" in result.metadata
        assert "modularity_by_k" in result.metadata

        communities = result.metadata["communities"]
        assert isinstance(communities, list)
        assert all(isinstance(c, set) for c in communities)

    def test_assess_structure_nodes(self):
        """Test node-level assignments."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (3, 4)])

        result = assess_hierarchical_structure(G)

        # All nodes should have community assignment
        assert len(result.nodes) == G.number_of_nodes()
        for node, data in result.nodes.items():
            assert "community" in data


class TestEdgeCases:
    """Test edge cases."""

    def test_disconnected_graph_hierarchical(self):
        """Test on disconnected graph."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (2, 3)])  # Two components

        communities = hierarchical_clustering(G, n_communities=2)

        assert len(communities) >= 2

    def test_complete_graph_hierarchical(self):
        """Test on complete graph."""
        G = nx.complete_graph(6)

        communities = hierarchical_clustering(G, n_communities=3)

        # Should be able to partition
        assert 1 <= len(communities) <= 6

    def test_star_graph_girvan_newman(self):
        """Test Girvan-Newman on star graph."""
        G = nx.star_graph(5)

        communities = girvan_newman(G, k=2)

        # Should split into at least 2 communities
        assert len(communities) >= 2

    def test_tree_graph_hierarchical(self):
        """Test on tree."""
        G = nx.balanced_tree(2, 3)

        result = assess_hierarchical_structure(G)

        assert result.metrics["optimal_k"] >= 1
        assert result.metrics["max_modularity"] >= 0


class TestIntegration:
    """Test integration workflows."""

    def test_full_hierarchical_workflow(self):
        """Test complete hierarchical workflow."""
        G = nx.karate_club_graph()

        # Assess structure
        result = assess_hierarchical_structure(G, method="agglomerative")

        # Get optimal number of communities
        k_opt = result.metrics["optimal_k"]

        # Cluster with optimal k
        communities = hierarchical_clustering(G, n_communities=k_opt)

        assert len(communities) >= 1

        # All nodes assigned
        all_nodes = set()
        for comm in communities:
            all_nodes.update(comm)
        assert all_nodes == set(G.nodes())

    def test_compare_hierarchical_methods(self):
        """Test comparing different hierarchical methods."""
        G = nx.karate_club_graph()

        # Agglomerative with different linkages
        comms_single = hierarchical_clustering(G, linkage="single", n_communities=3)
        comms_average = hierarchical_clustering(G, linkage="average", n_communities=3)
        comms_complete = hierarchical_clustering(G, linkage="complete", n_communities=3)

        # All should produce valid partitions
        for comms in [comms_single, comms_average, comms_complete]:
            all_nodes = set()
            for c in comms:
                all_nodes.update(c)
            assert all_nodes == set(G.nodes())

    def test_girvan_newman_evolution(self):
        """Test tracking community evolution with Girvan-Newman."""
        G = nx.karate_club_graph()

        # Get partitions at different k
        partitions = []
        for k in range(2, 6):
            comms = girvan_newman(G, k=k)
            partitions.append(comms)

        # Number of communities should generally increase
        sizes = [len(p) for p in partitions]
        assert sizes[-1] >= sizes[0]

    def test_weighted_hierarchical_workflow(self):
        """Test workflow with weighted network."""
        G = nx.Graph()
        # Create weighted structure
        edges = [
            (0, 1, 10.0),
            (1, 2, 10.0),  # Strong community
            (3, 4, 10.0),
            (4, 5, 10.0),  # Strong community
            (2, 3, 1.0),  # Weak bridge
        ]
        for u, v, w in edges:
            G.add_edge(u, v, weight=w)

        result = assess_hierarchical_structure(G, method="agglomerative")

        # Should find structure
        assert result.metrics["optimal_k"] >= 2
        assert result.metrics["max_modularity"] > 0.2
