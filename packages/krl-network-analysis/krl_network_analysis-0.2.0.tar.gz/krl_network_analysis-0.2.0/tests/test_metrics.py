# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Tests for network metrics.
"""

import networkx as nx
import pandas as pd
import pytest

from krl_network.core.exceptions import ComputationError, InvalidNetworkError
from krl_network.metrics import (  # Centrality; Clustering; Path analysis; Statistics
    all_pairs_shortest_path,
    assortativity,
    average_clustering,
    average_shortest_path_length,
    betweenness_centrality,
    closeness_centrality,
    clustering_coefficient,
    degree_assortativity,
    degree_centrality,
    density,
    diameter,
    eccentricity,
    eigenvector_centrality,
    katz_centrality,
    pagerank,
    reciprocity,
    shortest_path,
    transitivity,
    triangles,
)


@pytest.fixture
def simple_graph():
    """Create a simple connected graph."""
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1), (1, 3)])
    return G


@pytest.fixture
def weighted_graph():
    """Create a weighted graph."""
    G = nx.Graph()
    G.add_edge(1, 2, weight=1.0)
    G.add_edge(2, 3, weight=2.0)
    G.add_edge(3, 4, weight=0.5)
    G.add_edge(4, 1, weight=1.5)
    return G


@pytest.fixture
def directed_graph():
    """Create a directed graph."""
    G = nx.DiGraph()
    G.add_edges_from([(1, 2), (2, 3), (3, 1), (2, 4)])
    return G


@pytest.fixture
def star_graph():
    """Create a star graph (central hub with spokes)."""
    G = nx.Graph()
    G.add_edges_from([(1, 2), (1, 3), (1, 4), (1, 5)])
    return G


class TestCentrality:
    """Tests for centrality measures."""

    def test_degree_centrality(self, simple_graph):
        """Test degree centrality computation."""
        centrality = degree_centrality(simple_graph)

        assert isinstance(centrality, dict)
        assert len(centrality) == 4
        assert all(0 <= v <= 1 for v in centrality.values())

    def test_degree_centrality_star(self, star_graph):
        """Test degree centrality on star graph."""
        centrality = degree_centrality(star_graph)

        # Node 1 (center) should have highest centrality
        assert centrality[1] == max(centrality.values())
        # All other nodes should have equal centrality
        outer_values = [centrality[i] for i in [2, 3, 4, 5]]
        assert len(set(outer_values)) == 1

    def test_betweenness_centrality(self, simple_graph):
        """Test betweenness centrality computation."""
        centrality = betweenness_centrality(simple_graph)

        assert isinstance(centrality, dict)
        assert len(centrality) == 4
        assert all(0 <= v <= 1 for v in centrality.values())

    def test_betweenness_centrality_weighted(self, weighted_graph):
        """Test weighted betweenness centrality."""
        centrality = betweenness_centrality(weighted_graph, weight="weight")

        assert isinstance(centrality, dict)
        assert all(0 <= v <= 1 for v in centrality.values())

    def test_closeness_centrality(self, simple_graph):
        """Test closeness centrality computation."""
        centrality = closeness_centrality(simple_graph)

        assert isinstance(centrality, dict)
        assert len(centrality) == 4
        assert all(0 <= v <= 1 for v in centrality.values())

    def test_eigenvector_centrality(self, simple_graph):
        """Test eigenvector centrality computation."""
        centrality = eigenvector_centrality(simple_graph)

        assert isinstance(centrality, dict)
        assert len(centrality) == 4
        assert all(v >= 0 for v in centrality.values())

    def test_pagerank(self, simple_graph):
        """Test PageRank computation."""
        pr = pagerank(simple_graph)

        assert isinstance(pr, dict)
        assert len(pr) == 4
        # PageRank values should sum to approximately 1
        assert abs(sum(pr.values()) - 1.0) < 0.01

    def test_pagerank_alpha(self, simple_graph):
        """Test PageRank with different alpha values."""
        pr1 = pagerank(simple_graph, alpha=0.85)
        pr2 = pagerank(simple_graph, alpha=0.5)

        assert pr1 != pr2

    def test_katz_centrality(self, simple_graph):
        """Test Katz centrality computation."""
        centrality = katz_centrality(simple_graph, alpha=0.1)

        assert isinstance(centrality, dict)
        assert len(centrality) == 4
        assert all(v > 0 for v in centrality.values())


class TestClustering:
    """Tests for clustering measures."""

    def test_clustering_coefficient_all(self, simple_graph):
        """Test clustering coefficient for all nodes."""
        clustering = clustering_coefficient(simple_graph)

        assert isinstance(clustering, dict)
        assert len(clustering) == 4
        assert all(0 <= v <= 1 for v in clustering.values())

    def test_clustering_coefficient_single_node(self, simple_graph):
        """Test clustering coefficient for single node."""
        clustering = clustering_coefficient(simple_graph, nodes=1)

        assert isinstance(clustering, float)
        assert 0 <= clustering <= 1

    def test_average_clustering(self, simple_graph):
        """Test average clustering coefficient."""
        avg_clustering = average_clustering(simple_graph)

        assert isinstance(avg_clustering, float)
        assert 0 <= avg_clustering <= 1

    def test_transitivity(self, simple_graph):
        """Test transitivity computation."""
        trans = transitivity(simple_graph)

        assert isinstance(trans, float)
        assert 0 <= trans <= 1

    def test_triangles_all(self, simple_graph):
        """Test triangle counting for all nodes."""
        tri = triangles(simple_graph)

        assert isinstance(tri, dict)
        assert all(v >= 0 for v in tri.values())

    def test_triangles_single_node(self, simple_graph):
        """Test triangle counting for single node."""
        tri = triangles(simple_graph, nodes=1)

        assert isinstance(tri, int)
        assert tri >= 0


class TestPathAnalysis:
    """Tests for path analysis functions."""

    def test_shortest_path_single_target(self, simple_graph):
        """Test shortest path to single target."""
        path = shortest_path(simple_graph, source=1, target=4)

        assert isinstance(path, list)
        assert path[0] == 1
        assert path[-1] == 4

    def test_shortest_path_all_targets(self, simple_graph):
        """Test shortest paths to all targets."""
        paths = shortest_path(simple_graph, source=1)

        assert isinstance(paths, dict)
        assert 1 in paths
        assert all(isinstance(p, list) for p in paths.values())

    def test_shortest_path_weighted(self, weighted_graph):
        """Test weighted shortest path."""
        path = shortest_path(
            weighted_graph,
            source=1,
            target=3,
            weight="weight",
            method="dijkstra",
        )

        assert isinstance(path, list)
        assert path[0] == 1
        assert path[-1] == 3

    def test_shortest_path_invalid_node(self, simple_graph):
        """Test shortest path with invalid node."""
        with pytest.raises(InvalidNetworkError):
            shortest_path(simple_graph, source=99, target=1)

    def test_all_pairs_shortest_path(self, simple_graph):
        """Test all pairs shortest paths."""
        all_paths = all_pairs_shortest_path(simple_graph)

        assert isinstance(all_paths, dict)
        assert len(all_paths) == 4
        # Check that we have paths from each node
        for source in simple_graph.nodes():
            assert source in all_paths

    def test_average_shortest_path_length(self, simple_graph):
        """Test average shortest path length."""
        avg_length = average_shortest_path_length(simple_graph)

        assert isinstance(avg_length, float)
        assert avg_length > 0

    def test_diameter(self, simple_graph):
        """Test network diameter."""
        diam = diameter(simple_graph)

        assert isinstance(diam, (int, float))
        assert diam > 0

    def test_eccentricity_all(self, simple_graph):
        """Test eccentricity for all nodes."""
        ecc = eccentricity(simple_graph)

        assert isinstance(ecc, dict)
        assert len(ecc) == 4
        assert all(v > 0 for v in ecc.values())

    def test_eccentricity_single_node(self, simple_graph):
        """Test eccentricity for single node."""
        ecc = eccentricity(simple_graph, v=1)

        assert isinstance(ecc, (int, float))
        assert ecc > 0


class TestStatistics:
    """Tests for network statistics."""

    def test_density(self, simple_graph):
        """Test density computation."""
        dens = density(simple_graph)

        assert isinstance(dens, float)
        assert 0 <= dens <= 1

    def test_density_complete_graph(self):
        """Test density of complete graph."""
        G = nx.complete_graph(5)
        dens = density(G)

        assert abs(dens - 1.0) < 0.01

    def test_reciprocity_directed(self, directed_graph):
        """Test reciprocity for directed graph."""
        recip = reciprocity(directed_graph)

        assert isinstance(recip, float)
        assert 0 <= recip <= 1

    def test_reciprocity_undirected(self, simple_graph):
        """Test reciprocity raises error for undirected graph."""
        with pytest.raises(ComputationError, match="directed"):
            reciprocity(simple_graph)

    def test_degree_assortativity(self, simple_graph):
        """Test degree assortativity."""
        assortativity_coef = degree_assortativity(simple_graph)

        assert isinstance(assortativity_coef, float)
        assert -1 <= assortativity_coef <= 1

    def test_attribute_assortativity(self):
        """Test attribute assortativity."""
        G = nx.Graph()
        G.add_edges_from([(1, 2), (2, 3), (3, 4)])
        nx.set_node_attributes(G, {1: "A", 2: "A", 3: "B", 4: "B"}, "type")

        assortativity_coef = assortativity(G, "type")

        assert isinstance(assortativity_coef, float)
        assert -1 <= assortativity_coef <= 1


class TestMetricsEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_graph(self):
        """Test metrics on empty graph."""
        G = nx.Graph()

        # Empty graph returns empty dict
        centrality = degree_centrality(G)
        assert centrality == {}

    def test_single_node_graph(self):
        """Test metrics on single node."""
        G = nx.Graph()
        G.add_node(1)

        centrality = degree_centrality(G)
        # Single node has centrality of 1 by convention in NetworkX
        assert centrality[1] == 1

    def test_disconnected_graph_diameter(self):
        """Test diameter raises error for disconnected graph."""
        G = nx.Graph()
        G.add_edges_from([(1, 2), (3, 4)])

        with pytest.raises(InvalidNetworkError, match="connected"):
            diameter(G)

    def test_disconnected_graph_avg_path(self):
        """Test average path length raises error for disconnected graph."""
        G = nx.Graph()
        G.add_edges_from([(1, 2), (3, 4)])

        with pytest.raises(InvalidNetworkError, match="connected"):
            average_shortest_path_length(G)


class TestMetricsIntegration:
    """Integration tests for metrics."""

    def test_centrality_ranking(self, star_graph):
        """Test that different centrality measures agree on star graph."""
        deg_cent = degree_centrality(star_graph)
        bet_cent = betweenness_centrality(star_graph)
        close_cent = closeness_centrality(star_graph)

        # Node 1 (center) should be top in all measures
        assert deg_cent[1] == max(deg_cent.values())
        assert bet_cent[1] == max(bet_cent.values())
        assert close_cent[1] == max(close_cent.values())

    def test_clustering_vs_transitivity(self, simple_graph):
        """Test relationship between clustering and transitivity."""
        avg_clust = average_clustering(simple_graph)
        trans = transitivity(simple_graph)

        # Both should be in [0, 1]
        assert 0 <= avg_clust <= 1
        assert 0 <= trans <= 1
        # They measure similar but not identical things
        assert isinstance(avg_clust, float)
        assert isinstance(trans, float)
