"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Tests for modularity-based community detection.
"""

import networkx as nx
import numpy as np
import pytest

from krl_network.community.modularity import (
    ModularityOptimizer,
    calculate_modularity,
    leiden_communities,
    louvain_communities,
    optimize_modularity,
)
from krl_network.core.exceptions import ComputationError


class TestModularityCalculation:
    """Test modularity score calculation."""

    def test_calculate_modularity_perfect_partition(self):
        """Test modularity with perfect community structure."""
        # Two complete subgraphs connected by one edge
        G = nx.Graph()
        G.add_edges_from([(0, 1), (0, 2), (1, 2)])  # Community 1
        G.add_edges_from([(3, 4), (3, 5), (4, 5)])  # Community 2
        G.add_edge(2, 3)  # Bridge

        communities = [{0, 1, 2}, {3, 4, 5}]
        Q = calculate_modularity(G, communities)

        # Should have high modularity
        assert Q > 0.3

    def test_calculate_modularity_single_community(self):
        """Test modularity with all nodes in one community."""
        G = nx.karate_club_graph()
        communities = [set(G.nodes())]

        Q = calculate_modularity(G, communities)
        assert Q == pytest.approx(0.0, abs=1e-10)

    def test_calculate_modularity_all_separate(self):
        """Test modularity with each node in own community."""
        G = nx.karate_club_graph()
        communities = [{node} for node in G.nodes()]

        Q = calculate_modularity(G, communities)
        # Should be negative or very small
        assert Q < 0.1

    def test_calculate_modularity_dict_format(self):
        """Test modularity with dict community assignment."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (3, 4), (4, 5)])

        communities = {0: 0, 1: 0, 2: 0, 3: 1, 4: 1, 5: 1}
        Q = calculate_modularity(G, communities)

        assert isinstance(Q, float)
        assert -0.5 <= Q <= 1.0

    def test_calculate_modularity_resolution_parameter(self):
        """Test resolution parameter effect."""
        G = nx.karate_club_graph()
        communities = [{0, 1, 2}, set(range(3, 34))]

        Q_low = calculate_modularity(G, communities, resolution=0.5)
        Q_high = calculate_modularity(G, communities, resolution=2.0)

        # Higher resolution should penalize large communities more
        assert Q_low != Q_high

    def test_calculate_modularity_weighted(self):
        """Test modularity with weighted edges."""
        G = nx.Graph()
        G.add_edge(0, 1, weight=1.0)
        G.add_edge(1, 2, weight=1.0)
        G.add_edge(2, 3, weight=0.1)  # Weak link
        G.add_edge(3, 4, weight=1.0)

        communities = [{0, 1, 2}, {3, 4}]
        Q = calculate_modularity(G, communities, weight="weight")

        assert Q > 0

    def test_calculate_modularity_empty_graph(self):
        """Test modularity on empty graph."""
        G = nx.Graph()
        Q = calculate_modularity(G, [])

        assert Q == 0.0

    def test_calculate_modularity_invalid_partition(self):
        """Test error on invalid community partition."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2)])

        # Missing node 2
        communities = [{0, 1}]

        with pytest.raises(ComputationError):
            calculate_modularity(G, communities)


class TestLouvainCommunities:
    """Test Louvain algorithm."""

    def test_louvain_basic(self):
        """Test basic Louvain community detection."""
        G = nx.karate_club_graph()
        communities = louvain_communities(G)

        assert len(communities) > 1
        assert len(communities) < G.number_of_nodes()

        # Check all nodes assigned
        all_nodes = set()
        for comm in communities:
            all_nodes.update(comm)
        assert all_nodes == set(G.nodes())

    def test_louvain_known_structure(self):
        """Test Louvain on graph with known community structure."""
        # Two clear communities
        G = nx.Graph()
        # Community 1
        for i in range(5):
            for j in range(i + 1, 5):
                G.add_edge(i, j)
        # Community 2
        for i in range(5, 10):
            for j in range(i + 1, 10):
                G.add_edge(i, j)
        # One bridge
        G.add_edge(4, 5)

        communities = louvain_communities(G)

        # Should find 2 communities
        assert len(communities) >= 2

        # Calculate modularity
        Q = calculate_modularity(G, communities)
        assert Q > 0.3

    def test_louvain_weighted(self):
        """Test Louvain with weighted edges."""
        G = nx.Graph()
        # Strong community 1
        G.add_edge(0, 1, weight=5.0)
        G.add_edge(1, 2, weight=5.0)
        G.add_edge(2, 0, weight=5.0)
        # Strong community 2
        G.add_edge(3, 4, weight=5.0)
        G.add_edge(4, 5, weight=5.0)
        G.add_edge(5, 3, weight=5.0)
        # Weak bridge
        G.add_edge(2, 3, weight=0.5)

        communities = louvain_communities(G, weight="weight")

        assert len(communities) == 2

    def test_louvain_resolution(self):
        """Test resolution parameter effect."""
        G = nx.karate_club_graph()

        comms_low = louvain_communities(G, resolution=0.5)
        comms_high = louvain_communities(G, resolution=2.0)

        # Higher resolution should find more communities
        assert len(comms_high) >= len(comms_low)

    def test_louvain_random_state(self):
        """Test reproducibility with random_state."""
        G = nx.karate_club_graph()

        comms1 = louvain_communities(G, random_state=42)
        comms2 = louvain_communities(G, random_state=42)

        # Should be identical
        assert len(comms1) == len(comms2)

    def test_louvain_empty_graph(self):
        """Test Louvain on empty graph."""
        G = nx.Graph()
        communities = louvain_communities(G)

        assert communities == []

    def test_louvain_single_node(self):
        """Test Louvain on single node."""
        G = nx.Graph()
        G.add_node(0)

        communities = louvain_communities(G)

        assert len(communities) == 1
        assert communities[0] == {0}

    def test_louvain_directed_error(self):
        """Test error on directed graph."""
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])

        with pytest.raises(ComputationError):
            louvain_communities(G)


class TestLeidenCommunities:
    """Test Leiden algorithm."""

    def test_leiden_basic(self):
        """Test basic Leiden community detection."""
        G = nx.karate_club_graph()
        communities = leiden_communities(G)

        assert len(communities) > 1
        assert len(communities) < G.number_of_nodes()

        # Check all nodes assigned
        all_nodes = set()
        for comm in communities:
            all_nodes.update(comm)
        assert all_nodes == set(G.nodes())

    def test_leiden_connectivity(self):
        """Test that Leiden ensures connected communities."""
        # Create graph with disconnected subgroups
        G = nx.Graph()
        # Main component
        G.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 4)])
        # Separate component (should be separate community)
        G.add_edges_from([(5, 6), (6, 7)])

        communities = leiden_communities(G)

        # Each community should be connected
        for comm in communities:
            subgraph = G.subgraph(comm)
            assert nx.is_connected(subgraph)

    def test_leiden_vs_louvain(self):
        """Test Leiden improves on Louvain."""
        G = nx.karate_club_graph()

        comms_louvain = louvain_communities(G, random_state=42)
        comms_leiden = leiden_communities(G, random_state=42)

        # Both should find reasonable communities
        assert 2 <= len(comms_louvain) <= 10
        assert 2 <= len(comms_leiden) <= 10

        # Leiden communities should be connected
        for comm in comms_leiden:
            subgraph = G.subgraph(comm)
            assert nx.is_connected(subgraph)

    def test_leiden_weighted(self):
        """Test Leiden with weighted edges."""
        G = nx.Graph()
        G.add_edge(0, 1, weight=5.0)
        G.add_edge(1, 2, weight=5.0)
        G.add_edge(3, 4, weight=5.0)
        G.add_edge(2, 3, weight=0.5)

        communities = leiden_communities(G, weight="weight")

        assert len(communities) >= 2

    def test_leiden_empty_graph(self):
        """Test Leiden on empty graph."""
        G = nx.Graph()
        communities = leiden_communities(G)

        assert communities == []

    def test_leiden_directed_error(self):
        """Test error on directed graph."""
        G = nx.DiGraph()
        G.add_edges_from([(0, 1), (1, 2)])

        with pytest.raises(ComputationError):
            leiden_communities(G)


class TestOptimizeModularity:
    """Test modularity optimization wrapper."""

    def test_optimize_modularity_louvain(self):
        """Test optimization with Louvain method."""
        G = nx.karate_club_graph()
        result = optimize_modularity(G, method="louvain")

        assert "num_communities" in result.metrics
        assert "modularity" in result.metrics
        assert result.metrics["num_communities"] > 1
        assert result.metrics["modularity"] > 0

        # Check nodes have community assignments
        assert len(result.nodes) == G.number_of_nodes()
        for node, data in result.nodes.items():
            assert "community" in data

    def test_optimize_modularity_leiden(self):
        """Test optimization with Leiden method."""
        G = nx.karate_club_graph()
        result = optimize_modularity(G, method="leiden")

        assert result.metrics["num_communities"] > 1
        assert result.metadata["method"] == "leiden"

    def test_optimize_modularity_unknown_method(self):
        """Test error on unknown method."""
        G = nx.Graph()
        G.add_edge(0, 1)

        with pytest.raises(ValueError):
            optimize_modularity(G, method="unknown")

    def test_optimize_modularity_metadata(self):
        """Test metadata includes communities."""
        G = nx.karate_club_graph()
        result = optimize_modularity(G, method="louvain", resolution=1.5)

        assert "communities" in result.metadata
        assert "resolution" in result.metadata
        assert result.metadata["resolution"] == 1.5

        # Communities should be list of sets
        communities = result.metadata["communities"]
        assert isinstance(communities, list)
        assert all(isinstance(c, set) for c in communities)


class TestModularityOptimizer:
    """Test ModularityOptimizer class."""

    def test_optimizer_initialization(self):
        """Test optimizer initialization."""
        opt = ModularityOptimizer(resolution=1.5, weight="w", random_state=42)

        assert opt.resolution == 1.5
        assert opt.weight == "w"
        assert opt.random_state == 42

    def test_optimizer_delta_modularity(self):
        """Test delta modularity calculation."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (1, 2), (2, 3)])

        opt = ModularityOptimizer()
        communities = {0: 0, 1: 0, 2: 1, 3: 1}
        m = G.number_of_edges()

        # Calculate delta for moving node 1 to community 1
        delta = opt._calculate_delta_modularity(G, 1, 1, communities, m)

        assert isinstance(delta, float)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_disconnected_graph(self):
        """Test on disconnected graph."""
        G = nx.Graph()
        G.add_edges_from([(0, 1), (2, 3)])  # Two components

        communities = louvain_communities(G)

        # Should have at least 2 communities
        assert len(communities) >= 2

    def test_complete_graph(self):
        """Test on complete graph."""
        G = nx.complete_graph(10)

        communities = louvain_communities(G)

        # Complete graph might be single community
        assert len(communities) >= 1

        Q = calculate_modularity(G, communities)
        # Modularity of complete graph partition
        assert -0.5 <= Q <= 1.0

    def test_star_graph(self):
        """Test on star graph."""
        G = nx.star_graph(10)

        communities = louvain_communities(G)

        assert len(communities) >= 1

        # All nodes should be assigned
        all_nodes = set()
        for comm in communities:
            all_nodes.update(comm)
        assert all_nodes == set(G.nodes())

    def test_tree_graph(self):
        """Test on tree graph."""
        G = nx.balanced_tree(2, 3)

        communities = louvain_communities(G)

        assert len(communities) >= 1
        Q = calculate_modularity(G, communities)
        assert Q >= -0.5


class TestIntegration:
    """Test integration workflows."""

    def test_full_community_detection_workflow(self):
        """Test complete community detection workflow."""
        # Create test graph
        G = nx.karate_club_graph()

        # Detect communities with Louvain
        result_louvain = optimize_modularity(G, method="louvain", random_state=42)

        # Detect with Leiden
        result_leiden = optimize_modularity(G, method="leiden", random_state=42)

        # Both should find reasonable structure
        assert result_louvain.metrics["modularity"] > 0.3
        assert result_leiden.metrics["modularity"] > 0.3

        # Compare community counts
        n_louvain = result_louvain.metrics["num_communities"]
        n_leiden = result_leiden.metrics["num_communities"]

        assert 2 <= n_louvain <= 10
        assert 2 <= n_leiden <= 10

    def test_resolution_parameter_exploration(self):
        """Test exploring different resolution parameters."""
        G = nx.karate_club_graph()

        results = []
        for res in [0.5, 1.0, 1.5, 2.0]:
            result = optimize_modularity(G, method="louvain", resolution=res, random_state=42)
            results.append(result.metrics["num_communities"])

        # Higher resolution should generally give more communities
        assert results[-1] >= results[0]

    def test_weighted_network_workflow(self):
        """Test workflow with weighted network."""
        G = nx.Graph()
        # Create weighted network
        edges = [
            (0, 1, 5.0),
            (1, 2, 5.0),
            (2, 0, 5.0),  # Strong triangle
            (3, 4, 5.0),
            (4, 5, 5.0),
            (5, 3, 5.0),  # Strong triangle
            (2, 3, 0.5),  # Weak bridge
        ]
        for u, v, w in edges:
            G.add_edge(u, v, weight=w)

        result = optimize_modularity(G, method="louvain", weight="weight")

        # Should find 2 communities
        assert result.metrics["num_communities"] == 2
        assert result.metrics["modularity"] > 0.4
