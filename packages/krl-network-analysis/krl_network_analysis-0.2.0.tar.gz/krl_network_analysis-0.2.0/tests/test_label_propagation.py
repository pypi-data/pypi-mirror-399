"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Tests for label propagation methods.
"""

import networkx as nx
import numpy as np
import pytest

from krl_network.community.label_propagation import (
    assess_label_propagation_structure,
    label_propagation,
    multi_label_propagation,
    semi_supervised_label_propagation,
    synchronous_label_propagation,
)
from krl_network.community.modularity import calculate_modularity


class TestLabelPropagation:
    """Test basic label propagation."""

    def test_basic_label_propagation(self):
        """Test basic label propagation."""
        G = nx.karate_club_graph()
        communities = label_propagation(G, random_state=42)

        assert len(communities) > 0
        total_nodes = sum(len(c) for c in communities)
        assert total_nodes == G.number_of_nodes()

    def test_known_structure(self):
        """Test on graph with clear communities."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])  # Clique 1
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])  # Clique 2
        G.add_edge(2, 3)  # Weak bridge

        communities = label_propagation(G, random_state=42)

        # Should find 2 communities
        assert len(communities) == 2

    def test_weighted_graph(self):
        """Test with weighted edges."""
        G = nx.Graph()
        G.add_weighted_edges_from(
            [
                (0, 1, 10.0),
                (1, 2, 10.0),  # Strong
                (3, 4, 10.0),
                (4, 5, 10.0),  # Strong
                (2, 3, 0.1),  # Weak
            ]
        )

        communities = label_propagation(G, weight="weight", random_state=42)

        assert len(communities) >= 2

    def test_max_iterations(self):
        """Test max iterations parameter."""
        G = nx.karate_club_graph()

        # Should converge
        communities = label_propagation(G, max_iterations=10, random_state=42)
        assert len(communities) > 0

    def test_random_state(self):
        """Test reproducibility with random state."""
        G = nx.karate_club_graph()

        comm1 = label_propagation(G, random_state=42)
        comm2 = label_propagation(G, random_state=42)

        assert comm1 == comm2

    def test_empty_graph(self):
        """Test with empty graph."""
        G = nx.Graph()
        communities = label_propagation(G)

        assert len(communities) == 0

    def test_single_node(self):
        """Test with single node."""
        G = nx.Graph()
        G.add_node(0)

        communities = label_propagation(G)
        assert len(communities) == 1
        assert communities[0] == {0}


class TestSemiSupervisedLabelPropagation:
    """Test semi-supervised label propagation."""

    def test_basic_semi_supervised(self):
        """Test basic semi-supervised propagation."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])

        # Fix labels for nodes 0 and 4
        seed_labels = {0: 0, 4: 1}

        communities = semi_supervised_label_propagation(G, seed_labels)

        assert len(communities) == 2

    def test_known_structure(self):
        """Test with known community structure and seeds."""
        G = nx.Graph()
        # Two clear communities
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])  # Comm 0
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])  # Comm 1
        G.add_edge(2, 3)  # Bridge

        # Seed one node from each community
        seed_labels = {0: 0, 5: 1}

        communities = semi_supervised_label_propagation(G, seed_labels)

        # Should respect seeds
        comm_dict = {}
        for i, comm in enumerate(communities):
            for node in comm:
                comm_dict[node] = i

        assert comm_dict[0] != comm_dict[5]

    def test_all_seeds(self):
        """Test when all nodes have seeds."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])

        seed_labels = {0: 0, 1: 0, 2: 1}

        communities = semi_supervised_label_propagation(G, seed_labels)

        # Should match seed labels
        assert len(communities) == 2

    def test_empty_graph(self):
        """Test with empty graph."""
        G = nx.Graph()
        communities = semi_supervised_label_propagation(G, {})

        assert len(communities) == 0


class TestSynchronousLabelPropagation:
    """Test synchronous label propagation."""

    def test_basic_synchronous(self):
        """Test basic synchronous propagation."""
        G = nx.karate_club_graph()
        communities = synchronous_label_propagation(G, random_state=42)

        assert len(communities) > 0
        total_nodes = sum(len(c) for c in communities)
        assert total_nodes == G.number_of_nodes()

    def test_convergence(self):
        """Test convergence of synchronous method."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3)])

        communities = synchronous_label_propagation(G, max_iterations=100, random_state=42)

        # Should converge to stable state
        assert len(communities) > 0

    def test_weighted_sync(self):
        """Test with weighted edges."""
        G = nx.Graph()
        G.add_weighted_edges_from([(0, 1, 5.0), (1, 2, 5.0), (2, 3, 0.1), (3, 4, 5.0)])

        communities = synchronous_label_propagation(G, weight="weight", random_state=42)

        assert len(communities) >= 2


class TestMultiLabelPropagation:
    """Test multi-label propagation for overlapping communities."""

    def test_basic_multi_label(self):
        """Test basic multi-label propagation."""
        G = nx.karate_club_graph()
        node_labels = multi_label_propagation(G, max_labels_per_node=2, random_state=42)

        assert len(node_labels) == G.number_of_nodes()

        # Check that nodes have multiple labels
        multi_membership = sum(1 for labels in node_labels.values() if len(labels) > 1)
        assert multi_membership > 0

    def test_known_structure(self):
        """Test on graph with overlapping communities."""
        G = nx.Graph()
        # Two communities with a bridge node
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])  # Comm 1
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])  # Comm 2
        G.add_edge(2, 3)  # Bridge connects communities

        node_labels = multi_label_propagation(G, max_labels_per_node=2, random_state=42)

        # Bridge nodes (2, 3) might have multiple labels
        assert len(node_labels) == 6

    def test_max_labels(self):
        """Test max_labels_per_node parameter."""
        G = nx.karate_club_graph()

        node_labels = multi_label_propagation(G, max_labels_per_node=3, random_state=42)

        # No node should have more than 3 labels
        for labels in node_labels.values():
            assert len(labels) <= 3

    def test_empty_graph(self):
        """Test with empty graph."""
        G = nx.Graph()
        node_labels = multi_label_propagation(G)

        assert len(node_labels) == 0


class TestAssessLabelPropagationStructure:
    """Test label propagation structure assessment."""

    def test_basic_assessment(self):
        """Test basic assessment."""
        G = nx.karate_club_graph()
        result = assess_label_propagation_structure(G, n_trials=5)

        assert "num_communities" in result.metrics
        assert "modularity" in result.metrics
        assert "stability" in result.metrics
        assert result.metrics["num_communities"] >= 2

    def test_known_structure(self):
        """Test assessment on known structure."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])  # Clique 1
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])  # Clique 2
        G.add_edge(2, 3)  # Bridge

        result = assess_label_propagation_structure(G, n_trials=10)

        # Should find ~2 communities
        assert result.metrics["num_communities"] >= 2
        assert result.metrics["modularity"] > 0.2

    def test_stability(self):
        """Test stability metric."""
        G = nx.karate_club_graph()
        result = assess_label_propagation_structure(G, n_trials=10)

        # Stability should be between 0 and 1
        assert 0 <= result.metrics["stability"] <= 1

    def test_metadata(self):
        """Test metadata includes trial results."""
        G = nx.karate_club_graph()
        result = assess_label_propagation_structure(G, n_trials=5)

        assert "method" in result.metadata
        assert "n_trials" in result.metadata
        assert "all_modularity_scores" in result.metadata
        assert len(result.metadata["all_modularity_scores"]) == 5

    def test_empty_graph(self):
        """Test with empty graph."""
        G = nx.Graph()
        result = assess_label_propagation_structure(G)

        assert result.metrics["num_communities"] == 0
        assert result.metrics["modularity"] == 0.0


class TestEdgeCases:
    """Test edge cases for label propagation methods."""

    def test_disconnected_graph(self):
        """Test disconnected graph."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.add_edges_from([(3, 4), (4, 5)])

        communities = label_propagation(G, random_state=42)

        # Should handle disconnected components
        assert len(communities) >= 2

    def test_complete_graph(self):
        """Test complete graph."""
        G = nx.complete_graph(10)

        communities = label_propagation(G, random_state=42)

        # Complete graph may end up as single community
        assert len(communities) >= 1

    def test_star_graph(self):
        """Test star graph."""
        G = nx.star_graph(10)

        communities = label_propagation(G, random_state=42)

        assert len(communities) >= 1

    def test_isolated_nodes(self):
        """Test graph with isolated nodes."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])
        G.add_node(3)  # Isolated

        communities = label_propagation(G, random_state=42)

        # Isolated node should be in its own community
        assert len(communities) >= 2


class TestIntegration:
    """Integration tests for label propagation methods."""

    def test_full_workflow(self):
        """Test complete workflow."""
        G = nx.karate_club_graph()

        # Assessment
        result = assess_label_propagation_structure(G, n_trials=5)

        # Direct clustering
        communities = label_propagation(G, random_state=42)

        # Modularity check
        Q = calculate_modularity(G, communities)
        assert Q > 0

    def test_compare_sync_async(self):
        """Compare synchronous and asynchronous methods."""
        G = nx.karate_club_graph()

        async_comms = label_propagation(G, random_state=42)
        sync_comms = synchronous_label_propagation(G, random_state=42)

        Q_async = calculate_modularity(G, async_comms)
        Q_sync = calculate_modularity(G, sync_comms)

        # Both should give positive modularity
        assert Q_async > 0
        assert Q_sync > 0

    def test_semi_supervised_workflow(self):
        """Test semi-supervised workflow."""
        G = nx.karate_club_graph()

        # Use known clubs as seeds
        seed_labels = {0: 0, 33: 1}

        communities = semi_supervised_label_propagation(G, seed_labels)

        Q = calculate_modularity(G, communities)
        assert Q > 0.15  # Semi-supervised may be slightly lower

    def test_weighted_workflow(self):
        """Test workflow with weighted graph."""
        G = nx.Graph()
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
        result = assess_label_propagation_structure(G, n_trials=10, weight="weight")

        # Should find 2 communities
        assert result.metrics["num_communities"] >= 2
        assert result.metrics["modularity"] > 0.3
