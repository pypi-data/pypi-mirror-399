"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Tests for spectral clustering methods.
"""

import networkx as nx
import numpy as np
import pytest

from krl_network.community.modularity import calculate_modularity
from krl_network.community.spectral import (
    assess_spectral_structure,
    recursive_spectral_bisection,
    spectral_bisection,
    spectral_clustering,
)
from krl_network.core.exceptions import ComputationError


class TestSpectralClustering:
    """Test spectral clustering algorithm."""

    def test_basic_spectral_clustering(self):
        """Test basic spectral clustering."""
        # Karate club
        G = nx.karate_club_graph()
        communities = spectral_clustering(G, n_communities=2)

        assert len(communities) == 2
        assert len(communities[0]) + len(communities[1]) == G.number_of_nodes()

    def test_known_structure(self):
        """Test on graph with known community structure."""
        # Two cliques connected by single edge
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])  # Clique 1
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])  # Clique 2
        G.add_edge(2, 3)  # Bridge

        communities = spectral_clustering(G, n_communities=2)

        assert len(communities) == 2

        # Check that cliques are together
        comm_dict = {}
        for i, comm in enumerate(communities):
            for node in comm:
                comm_dict[node] = i

        # Nodes 0,1,2 should be in same community
        assert comm_dict[0] == comm_dict[1] == comm_dict[2]
        # Nodes 3,4,5 should be in same community
        assert comm_dict[3] == comm_dict[4] == comm_dict[5]
        # But different from first community
        assert comm_dict[0] != comm_dict[3]

    def test_laplacian_methods(self):
        """Test different Laplacian methods."""
        G = nx.karate_club_graph()

        # All methods should work
        for method in ["unnormalized", "normalized", "random_walk"]:
            communities = spectral_clustering(G, n_communities=2, method=method)
            assert len(communities) == 2

    def test_weighted_graph(self):
        """Test with weighted edges."""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (0, 1, 10.0),
                (1, 2, 10.0),
                (0, 2, 10.0),  # Strong clique
                (3, 4, 10.0),
                (4, 5, 10.0),
                (3, 5, 10.0),  # Strong clique
                (2, 3, 0.1),  # Weak bridge
            ]
        )

        communities = spectral_clustering(G, n_communities=2, weight="weight")

        # Should separate at weak bridge
        assert len(communities) == 2

    def test_random_state(self):
        """Test random state reproducibility."""
        G = nx.karate_club_graph()

        comm1 = spectral_clustering(G, n_communities=2, random_state=42)
        comm2 = spectral_clustering(G, n_communities=2, random_state=42)

        assert comm1 == comm2

    def test_empty_graph(self):
        """Test with empty graph."""
        G = nx.Graph()
        communities = spectral_clustering(G, n_communities=2)

        assert len(communities) == 0

    def test_single_node(self):
        """Test with single node."""
        G = nx.Graph()
        G.add_node(0)

        communities = spectral_clustering(G, n_communities=1)
        assert len(communities) == 1
        assert communities[0] == {0}

    def test_invalid_n_communities(self):
        """Test with invalid number of communities."""
        G = nx.karate_club_graph()

        with pytest.raises(ValueError):
            spectral_clustering(G, n_communities=0)


class TestSpectralBisection:
    """Test spectral bisection."""

    def test_basic_bisection(self):
        """Test basic bisection."""
        # Two cliques
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])
        G.add_edge(2, 3)

        comm1, comm2 = spectral_bisection(G)

        assert len(comm1) + len(comm2) == 6
        assert len(comm1) > 0 and len(comm2) > 0

    def test_karate_club(self):
        """Test on karate club."""
        G = nx.karate_club_graph()
        comm1, comm2 = spectral_bisection(G)

        assert len(comm1) > 0 and len(comm2) > 0
        assert len(comm1) + len(comm2) == 34

    def test_weighted_bisection(self):
        """Test weighted bisection."""
        G = nx.Graph()
        G.add_weighted_edges_from([(0, 1, 1.0), (1, 2, 1.0), (2, 3, 0.1), (3, 4, 1.0), (4, 5, 1.0)])

        comm1, comm2 = spectral_bisection(G, weight="weight")

        # Should cut at weak edge
        assert len(comm1) > 0 and len(comm2) > 0


class TestRecursiveSpectralBisection:
    """Test recursive spectral bisection."""

    def test_basic_recursive(self):
        """Test basic recursive bisection."""
        G = nx.karate_club_graph()
        communities = recursive_spectral_bisection(G, n_communities=4)

        assert len(communities) == 4
        total_nodes = sum(len(c) for c in communities)
        assert total_nodes == G.number_of_nodes()

    def test_known_structure(self):
        """Test on graph with four cliques."""
        G = nx.Graph()
        # Four cliques
        for i in range(4):
            nodes = [i * 3, i * 3 + 1, i * 3 + 2]
            G.add_edges_from([(nodes[0], nodes[1]), (nodes[1], nodes[2]), (nodes[0], nodes[2])])

        # Connect cliques weakly
        G.add_edge(2, 3)
        G.add_edge(5, 6)
        G.add_edge(8, 9)

        communities = recursive_spectral_bisection(G, n_communities=4)

        assert len(communities) == 4

    def test_weighted_recursive(self):
        """Test weighted recursive bisection."""
        G = nx.Graph()
        # Two strong communities, each with weak subcommunities
        G.add_weighted_edges_from(
            [
                (0, 1, 10),
                (1, 2, 5),  # Comm 1
                (3, 4, 10),
                (4, 5, 5),  # Comm 2
                (2, 3, 1),  # Weak bridge
            ]
        )

        communities = recursive_spectral_bisection(G, n_communities=2, weight="weight")
        assert len(communities) == 2


class TestAssessSpectralStructure:
    """Test spectral structure assessment."""

    def test_basic_assessment(self):
        """Test basic assessment."""
        G = nx.karate_club_graph()
        result = assess_spectral_structure(G, max_k=5)

        assert "optimal_k" in result.metrics
        assert "max_modularity" in result.metrics
        assert "spectral_gap" in result.metrics
        assert result.metrics["optimal_k"] >= 2

    def test_known_structure(self):
        """Test assessment on known structure."""
        # Two clear communities
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 2), (0, 3), (1, 3), (2, 3)])  # Clique 1
        G.add_edges_from([(4, 5), (4, 6), (5, 6), (4, 7), (5, 7), (6, 7)])  # Clique 2
        G.add_edge(3, 4)  # Bridge

        result = assess_spectral_structure(G, max_k=5)

        # Should identify 2 communities
        assert result.metrics["optimal_k"] == 2
        assert result.metrics["max_modularity"] > 0.3

    def test_different_methods(self):
        """Test different Laplacian methods."""
        G = nx.karate_club_graph()

        for method in ["unnormalized", "normalized", "random_walk"]:
            result = assess_spectral_structure(G, max_k=5, method=method)
            assert result.metrics["optimal_k"] >= 2

    def test_metadata(self):
        """Test metadata includes modularity scores."""
        G = nx.karate_club_graph()
        result = assess_spectral_structure(G, max_k=5)

        assert "method" in result.metadata
        assert "modularity_by_k" in result.metadata
        assert len(result.metadata["modularity_by_k"]) > 0


class TestEdgeCases:
    """Test edge cases for spectral methods."""

    def test_disconnected_graph(self):
        """Test disconnected graph."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.add_edges_from([(3, 4), (4, 5)])

        communities = spectral_clustering(G, n_communities=2)

        # Should handle disconnected components
        assert len(communities) == 2

    def test_complete_graph(self):
        """Test complete graph (single community)."""
        G = nx.complete_graph(10)

        communities = spectral_clustering(G, n_communities=2)

        # Complete graph has weak structure, but should still partition
        assert len(communities) == 2

    def test_star_graph(self):
        """Test star graph."""
        G = nx.star_graph(10)

        communities = spectral_clustering(G, n_communities=2)

        # Star has weak community structure
        assert len(communities) == 2

    def test_tree_graph(self):
        """Test tree graph."""
        G = nx.balanced_tree(2, 3)

        communities = spectral_clustering(G, n_communities=3)

        assert len(communities) == 3


class TestIntegration:
    """Integration tests combining spectral methods."""

    def test_full_workflow(self):
        """Test complete workflow."""
        G = nx.karate_club_graph()

        # Assessment
        result = assess_spectral_structure(G, max_k=5)
        best_k = result.metrics["optimal_k"]

        # Clustering with best k
        communities = spectral_clustering(G, n_communities=best_k)

        # Modularity check
        Q = calculate_modularity(G, communities)
        assert Q > 0.3

    def test_compare_methods(self):
        """Compare different spectral methods."""
        G = nx.karate_club_graph()

        results = {}
        for method in ["unnormalized", "normalized", "random_walk"]:
            communities = spectral_clustering(G, n_communities=2, method=method)
            Q = calculate_modularity(G, communities)
            results[method] = Q

        # All should give reasonable modularity
        for Q in results.values():
            assert Q > 0.2

    def test_bisection_vs_clustering(self):
        """Compare bisection and k-way clustering."""
        G = nx.karate_club_graph()

        # Bisection
        comm1, comm2 = spectral_bisection(G)
        bisect_comms = [comm1, comm2]
        Q_bisect = calculate_modularity(G, bisect_comms)

        # K-way clustering
        cluster_comms = spectral_clustering(G, n_communities=2)
        Q_cluster = calculate_modularity(G, cluster_comms)

        # Both should be positive
        assert Q_bisect > 0
        assert Q_cluster > 0

    def test_weighted_workflow(self):
        """Test workflow with weighted graph."""
        G = nx.Graph()
        # Create weighted communities
        G.add_weighted_edges_from(
            [
                (0, 1, 5.0),
                (1, 2, 5.0),
                (0, 2, 5.0),
                (3, 4, 5.0),
                (4, 5, 5.0),
                (3, 5, 5.0),
                (2, 3, 0.5),
            ]
        )

        # Assessment
        result = assess_spectral_structure(G, max_k=3, weight="weight")

        # Should find 2 communities
        assert result.metrics["optimal_k"] == 2
        assert result.metrics["max_modularity"] > 0.4
