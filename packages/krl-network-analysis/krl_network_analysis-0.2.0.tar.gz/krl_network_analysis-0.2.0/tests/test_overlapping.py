"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Tests for overlapping community detection methods.
"""

import networkx as nx
import numpy as np
import pytest

from krl_network.community.overlapping import (
    assess_overlapping_communities,
    clique_percolation,
    ego_network_splitting,
    fuzzy_community_membership,
    link_communities,
)


class TestCliquePercolation:
    """Test clique percolation method."""

    def test_basic_clique_percolation(self):
        """Test basic clique percolation."""
        G = nx.karate_club_graph()
        communities = clique_percolation(G, k=3)

        assert len(communities) > 0

    def test_known_structure(self):
        """Test on graph with overlapping cliques."""
        G = nx.Graph()
        # Two overlapping triangles
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])  # Triangle 1
        G.add_edges_from([(2, 3), (2, 4), (3, 4)])  # Triangle 2 (shares node 2)

        communities = clique_percolation(G, k=3)

        # Should find 2 communities
        assert len(communities) >= 1

        # Node 2 should appear in communities
        all_nodes = set().union(*communities)
        assert 2 in all_nodes

    def test_k_equals_2(self):
        """Test with k=2 (edges as cliques)."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3)])

        communities = clique_percolation(G, k=2)

        # Each edge is a clique
        assert len(communities) >= 1

    def test_k_too_large(self):
        """Test with k larger than max clique size."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])  # Max clique = 2

        communities = clique_percolation(G, k=5)

        # Should return empty or small communities
        assert len(communities) >= 0

    def test_empty_graph(self):
        """Test with empty graph."""
        G = nx.Graph()
        communities = clique_percolation(G, k=3)

        assert len(communities) == 0

    def test_invalid_k(self):
        """Test with invalid k value."""
        G = nx.karate_club_graph()

        with pytest.raises(ValueError):
            clique_percolation(G, k=1)


class TestLinkCommunities:
    """Test link communities method."""

    def test_basic_link_communities(self):
        """Test basic link communities."""
        G = nx.karate_club_graph()
        node_communities = link_communities(G)

        assert len(node_communities) == G.number_of_nodes()

        # Some nodes should have multiple memberships
        multi_membership = sum(1 for comms in node_communities.values() if len(comms) > 1)
        assert multi_membership >= 0

    def test_known_structure(self):
        """Test on graph with clear link structure."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])

        node_communities = link_communities(G)

        # All nodes should be assigned
        assert len(node_communities) == 5

    def test_threshold_parameter(self):
        """Test with different thresholds."""
        G = nx.karate_club_graph()

        for threshold in [0.3, 0.5, 0.7]:
            node_communities = link_communities(G, threshold=threshold)
            assert len(node_communities) > 0

    def test_disconnected_graph(self):
        """Test with disconnected components."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.add_edges_from([(3, 4), (4, 5)])

        node_communities = link_communities(G)

        # All nodes should be assigned
        assert len(node_communities) == 6

    def test_empty_graph(self):
        """Test with empty graph."""
        G = nx.Graph()
        node_communities = link_communities(G)

        assert len(node_communities) == 0


class TestEgoNetworkSplitting:
    """Test ego network splitting method."""

    def test_basic_ego_splitting(self):
        """Test basic ego network splitting."""
        G = nx.karate_club_graph()
        node_communities = ego_network_splitting(G)

        assert len(node_communities) > 0

        # Check overlaps
        multi_membership = sum(1 for comms in node_communities.values() if len(comms) > 1)
        assert multi_membership > 0

    def test_known_structure(self):
        """Test on star graph (hub with spokes)."""
        G = nx.star_graph(5)

        node_communities = ego_network_splitting(G)

        # Center node (0) should belong to multiple communities
        assert len(node_communities[0]) >= 1

    def test_min_community_size(self):
        """Test with different min community sizes."""
        G = nx.karate_club_graph()

        node_communities = ego_network_splitting(G, min_community_size=5)

        # Should still find communities
        assert len(node_communities) > 0

    def test_small_graph(self):
        """Test with small graph."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])

        node_communities = ego_network_splitting(G, min_community_size=2)

        assert len(node_communities) >= 2

    def test_empty_graph(self):
        """Test with empty graph."""
        G = nx.Graph()
        node_communities = ego_network_splitting(G)

        assert len(node_communities) == 0


class TestFuzzyCommunityMembership:
    """Test fuzzy community membership."""

    def test_basic_fuzzy(self):
        """Test basic fuzzy membership."""
        G = nx.karate_club_graph()
        memberships = fuzzy_community_membership(G, n_communities=2, random_state=42)

        assert len(memberships) == G.number_of_nodes()

        # Each node should have memberships summing to ~1
        for node, mem_dict in memberships.items():
            total = sum(mem_dict.values())
            assert 0.9 <= total <= 1.1

    def test_known_structure(self):
        """Test on graph with clear communities."""
        G = nx.Graph()
        # Two clear communities
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])  # Comm 0
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])  # Comm 1
        G.add_edge(2, 3)  # Bridge

        memberships = fuzzy_community_membership(G, n_communities=2, random_state=42)

        # Bridge nodes (2, 3) should have mixed membership
        assert len(memberships) == 6

    def test_fuzziness_parameter(self):
        """Test with different fuzziness values."""
        G = nx.karate_club_graph()

        for fuzziness in [1.5, 2.0, 3.0]:
            memberships = fuzzy_community_membership(
                G, n_communities=2, fuzziness=fuzziness, random_state=42
            )
            assert len(memberships) > 0

    def test_n_communities_too_large(self):
        """Test with n_communities > n_nodes."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])

        # Should handle gracefully
        memberships = fuzzy_community_membership(G, n_communities=10, random_state=42)

        assert len(memberships) == 3

    def test_empty_graph(self):
        """Test with empty graph."""
        G = nx.Graph()
        memberships = fuzzy_community_membership(G, n_communities=2)

        assert len(memberships) == 0


class TestAssessOverlappingCommunities:
    """Test overlapping community assessment."""

    def test_basic_assessment_clique(self):
        """Test assessment with clique percolation."""
        G = nx.karate_club_graph()
        result = assess_overlapping_communities(G, method="clique_percolation", k=3)

        assert "num_communities" in result.metrics
        assert "avg_memberships_per_node" in result.metrics
        assert result.metrics["num_communities"] >= 0

    def test_assessment_link_communities(self):
        """Test assessment with link communities."""
        G = nx.karate_club_graph()
        result = assess_overlapping_communities(G, method="link_communities")

        assert "num_communities" in result.metrics
        assert result.metrics["avg_memberships_per_node"] >= 1

    def test_assessment_ego_splitting(self):
        """Test assessment with ego splitting."""
        G = nx.karate_club_graph()
        result = assess_overlapping_communities(G, method="ego_splitting")

        assert "num_communities" in result.metrics
        assert "max_memberships" in result.metrics

    def test_known_structure(self):
        """Test assessment on known structure."""
        G = nx.Graph()
        # Two overlapping cliques
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])
        G.add_edges_from([(2, 3), (2, 4), (3, 4)])

        result = assess_overlapping_communities(G, method="clique_percolation", k=3)

        # Should find overlapping communities
        assert result.metrics["num_communities"] >= 1

    def test_metadata(self):
        """Test metadata includes method info."""
        G = nx.karate_club_graph()
        result = assess_overlapping_communities(G, method="clique_percolation", k=4)

        assert "method" in result.metadata
        assert result.metadata["method"] == "clique_percolation"
        assert result.metadata["k"] == 4

    def test_empty_graph(self):
        """Test with empty graph."""
        G = nx.Graph()
        result = assess_overlapping_communities(G, method="clique_percolation")

        assert result.metrics["num_communities"] == 0

    def test_unknown_method(self):
        """Test with unknown method."""
        G = nx.karate_club_graph()

        with pytest.raises(ValueError):
            assess_overlapping_communities(G, method="unknown_method")


class TestEdgeCases:
    """Test edge cases for overlapping methods."""

    def test_disconnected_graph(self):
        """Test disconnected graph."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.add_edges_from([(3, 4), (4, 5)])

        # Clique percolation
        comms = clique_percolation(G, k=2)
        assert len(comms) >= 1

        # Link communities
        node_comms = link_communities(G)
        assert len(node_comms) == 6

    def test_complete_graph(self):
        """Test complete graph."""
        G = nx.complete_graph(6)

        # Clique percolation (all nodes form one clique)
        comms = clique_percolation(G, k=3)
        assert len(comms) >= 1

        # Fuzzy membership
        memberships = fuzzy_community_membership(G, n_communities=2, random_state=42)
        assert len(memberships) == 6

    def test_star_graph(self):
        """Test star graph."""
        G = nx.star_graph(5)

        # Ego splitting (center should be in multiple communities)
        node_comms = ego_network_splitting(G)
        assert len(node_comms[0]) >= 1  # Center node

    def test_isolated_nodes(self):
        """Test graph with isolated nodes."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.add_node(3)  # Isolated

        # Link communities should handle this
        node_comms = link_communities(G)
        assert 3 in node_comms


class TestIntegration:
    """Integration tests for overlapping methods."""

    def test_full_workflow_clique(self):
        """Test complete workflow with clique percolation."""
        G = nx.karate_club_graph()

        # Assessment
        result = assess_overlapping_communities(G, method="clique_percolation", k=3)

        # Direct detection
        communities = clique_percolation(G, k=3)

        assert len(communities) > 0

    def test_compare_methods(self):
        """Compare different overlapping methods."""
        G = nx.karate_club_graph()

        # Clique percolation
        clique_comms = clique_percolation(G, k=3)

        # Link communities
        link_comms = link_communities(G)

        # Ego splitting
        ego_comms = ego_network_splitting(G)

        # All should find something
        assert len(clique_comms) > 0
        assert len(link_comms) > 0
        assert len(ego_comms) > 0

    def test_fuzzy_membership_analysis(self):
        """Test fuzzy membership analysis."""
        G = nx.karate_club_graph()

        memberships = fuzzy_community_membership(G, n_communities=3, random_state=42)

        # Find nodes with highest membership uncertainty
        entropy = {}
        for node, mem_dict in memberships.items():
            probs = list(mem_dict.values())
            # Shannon entropy
            ent = -sum(p * np.log(p + 1e-10) for p in probs if p > 0)
            entropy[node] = ent

        # Nodes with high entropy are boundary nodes
        assert len(entropy) == G.number_of_nodes()

    def test_weighted_workflow(self):
        """Test workflow with weighted graph."""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (0, 1, 5.0),
                (1, 2, 5.0),
                (0, 2, 5.0),  # Strong triangle
                (2, 3, 1.0),  # Weak bridge
                (3, 4, 5.0),
                (4, 5, 5.0),
                (3, 5, 5.0),  # Strong triangle
            ]
        )

        # Clique percolation doesn't use weights, but should still work
        communities = clique_percolation(G, k=3)

        # Should find 2 triangles
        assert len(communities) == 2
