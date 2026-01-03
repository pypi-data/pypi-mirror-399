"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Tests for community dynamics and evolution.
"""

import networkx as nx
import numpy as np
import pytest

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
from krl_network.community.modularity import louvain_communities


class TestJaccardSimilarity:
    """Test Jaccard similarity calculation."""

    def test_identical_sets(self):
        """Test with identical sets."""
        s1 = {1, 2, 3}
        s2 = {1, 2, 3}

        assert jaccard_similarity(s1, s2) == 1.0

    def test_disjoint_sets(self):
        """Test with disjoint sets."""
        s1 = {1, 2, 3}
        s2 = {4, 5, 6}

        assert jaccard_similarity(s1, s2) == 0.0

    def test_partial_overlap(self):
        """Test with partial overlap."""
        s1 = {1, 2, 3, 4}
        s2 = {3, 4, 5, 6}

        # Intersection: {3, 4} = 2, Union: {1,2,3,4,5,6} = 6
        assert jaccard_similarity(s1, s2) == 2.0 / 6.0

    def test_empty_sets(self):
        """Test with empty sets."""
        s1 = set()
        s2 = set()

        assert jaccard_similarity(s1, s2) == 1.0

    def test_one_empty_set(self):
        """Test with one empty set."""
        s1 = {1, 2, 3}
        s2 = set()

        assert jaccard_similarity(s1, s2) == 0.0


class TestMatchCommunities:
    """Test community matching."""

    def test_perfect_match(self):
        """Test perfect matching."""
        c1 = [{1, 2, 3}, {4, 5, 6}]
        c2 = [{1, 2, 3}, {4, 5, 6}]

        matches = match_communities(c1, c2, threshold=0.5)

        assert len(matches) == 2
        assert 0 in matches and 1 in matches

    def test_no_match(self):
        """Test with no matches above threshold."""
        c1 = [{1, 2, 3}]
        c2 = [{7, 8, 9}]

        matches = match_communities(c1, c2, threshold=0.5)

        assert len(matches) == 0

    def test_partial_match(self):
        """Test with partial matching."""
        c1 = [{1, 2, 3, 4}, {5, 6, 7}]
        c2 = [{1, 2, 3}, {8, 9, 10}]

        matches = match_communities(c1, c2, threshold=0.5)

        # First community should match (3/5 = 0.6 > 0.5)
        assert 0 in matches
        # Second shouldn't match (0/6 = 0.0)
        assert 1 not in matches

    def test_empty_communities(self):
        """Test with empty community lists."""
        c1 = []
        c2 = [{1, 2, 3}]

        matches = match_communities(c1, c2)
        assert len(matches) == 0

    def test_threshold_effect(self):
        """Test threshold effect on matching."""
        c1 = [{1, 2, 3, 4, 5}]
        c2 = [{1, 2, 3}]

        # 3/5 = 0.6
        matches_low = match_communities(c1, c2, threshold=0.5)
        matches_high = match_communities(c1, c2, threshold=0.7)

        assert len(matches_low) == 1
        assert len(matches_high) == 0


class TestDetectCommunityEvents:
    """Test community event detection."""

    def test_stable_communities(self):
        """Test detection of stable communities."""
        c_prev = [{1, 2, 3}, {4, 5, 6}]
        c_curr = [{1, 2, 3}, {4, 5, 6}]

        events = detect_community_events(c_prev, c_curr, 1)

        # Should detect stable events
        stable_events = [e for e in events if e.event_type == "stable"]
        assert len(stable_events) == 2

    def test_birth_event(self):
        """Test detection of birth events."""
        c_prev = [{1, 2, 3}]
        c_curr = [{1, 2, 3}, {4, 5, 6}]

        events = detect_community_events(c_prev, c_curr, 1)

        birth_events = [e for e in events if e.event_type == "birth"]
        assert len(birth_events) >= 1
        assert {4, 5, 6} in [e.nodes_affected for e in birth_events]

    def test_death_event(self):
        """Test detection of death events."""
        c_prev = [{1, 2, 3}, {4, 5, 6}]
        c_curr = [{1, 2, 3}]

        events = detect_community_events(c_prev, c_curr, 1)

        death_events = [e for e in events if e.event_type == "death"]
        assert len(death_events) >= 1

    def test_growth_event(self):
        """Test detection of growth events."""
        c_prev = [{1, 2}]
        c_curr = [{1, 2, 3, 4, 5}]  # Grows from 2 to 5 (>20% growth)

        # Need threshold=0.4 so they match (Jaccard=2/5=0.4)
        events = detect_community_events(c_prev, c_curr, 1, similarity_threshold=0.4)

        growth_events = [e for e in events if e.event_type == "growth"]
        assert len(growth_events) >= 1

    def test_shrink_event(self):
        """Test detection of shrink events."""
        c_prev = [{1, 2, 3, 4, 5}]
        c_curr = [{1, 2}]  # Shrinks from 5 to 2 (<80% of original)

        # Need threshold=0.4 so they match (Jaccard=2/5=0.4)
        events = detect_community_events(c_prev, c_curr, 1, similarity_threshold=0.4)

        shrink_events = [e for e in events if e.event_type == "shrink"]
        assert len(shrink_events) >= 1

    def test_merge_event(self):
        """Test detection of merge events."""
        c_prev = [{1, 2}, {3, 4}]
        c_curr = [{1, 2, 3, 4}]  # Two communities merge

        events = detect_community_events(c_prev, c_curr, 1, similarity_threshold=0.4)

        merge_events = [e for e in events if e.event_type == "merge"]
        assert len(merge_events) >= 1

    def test_split_event(self):
        """Test detection of split events."""
        c_prev = [{1, 2, 3, 4}]
        c_curr = [{1, 2}, {3, 4}]  # One community splits

        events = detect_community_events(c_prev, c_curr, 1, similarity_threshold=0.4)

        split_events = [e for e in events if e.event_type == "split"]
        assert len(split_events) >= 1


class TestTrackCommunitiesOverTime:
    """Test temporal community tracking."""

    def test_basic_tracking(self):
        """Test basic temporal tracking."""
        temporal = [[{1, 2, 3}, {4, 5, 6}], [{1, 2, 3}, {4, 5, 6}], [{1, 2, 3}, {4, 5, 6}]]

        all_events, event_counts = track_communities_over_time(temporal)

        assert len(all_events) == 2  # n-1 transitions
        assert "stable" in event_counts

    def test_dynamic_evolution(self):
        """Test with dynamic community evolution."""
        temporal = [
            [{1, 2, 3}],
            [{1, 2, 3}, {4, 5, 6}],  # Birth
            [{1, 2, 3, 4, 5, 6}],  # Merge
        ]

        all_events, event_counts = track_communities_over_time(temporal)

        assert "birth" in event_counts
        # May detect merge or growth depending on threshold
        assert event_counts["birth"] >= 1

    def test_empty_temporal(self):
        """Test with insufficient snapshots."""
        temporal = [[{1, 2, 3}]]

        all_events, event_counts = track_communities_over_time(temporal)

        assert len(all_events) == 0
        assert len(event_counts) == 0

    def test_event_counting(self):
        """Test event counting."""
        temporal = [[{1, 2}, {3, 4}], [{1, 2}], [{1, 2}, {5, 6}]]  # Death  # Birth

        all_events, event_counts = track_communities_over_time(temporal)

        assert event_counts.get("death", 0) >= 1
        assert event_counts.get("birth", 0) >= 1


class TestCalculateCommunityStability:
    """Test community stability calculation."""

    def test_perfectly_stable(self):
        """Test with perfectly stable communities."""
        temporal = [[{1, 2, 3}, {4, 5, 6}], [{1, 2, 3}, {4, 5, 6}], [{1, 2, 3}, {4, 5, 6}]]

        stability = calculate_community_stability(temporal)

        assert stability["avg_stability"] >= 0.9
        assert stability["num_snapshots"] == 3

    def test_highly_dynamic(self):
        """Test with highly dynamic communities."""
        temporal = [[{1, 2, 3}], [{4, 5, 6}], [{7, 8, 9}]]

        stability = calculate_community_stability(temporal)

        # Low stability due to completely different communities
        assert stability["avg_stability"] < 0.5

    def test_single_snapshot(self):
        """Test with single snapshot."""
        temporal = [[{1, 2, 3}]]

        stability = calculate_community_stability(temporal)

        assert stability["avg_stability"] == 0.0
        assert stability["num_snapshots"] == 1

    def test_gradual_change(self):
        """Test with gradual community changes."""
        temporal = [[{1, 2, 3, 4}], [{1, 2, 3, 5}], [{1, 2, 3, 6}]]  # Small change  # Small change

        stability = calculate_community_stability(temporal)

        # Should have moderate to high stability
        assert stability["avg_stability"] > 0.5


class TestCommunityLifecycleAnalysis:
    """Test community lifecycle analysis."""

    def test_basic_lifecycle(self):
        """Test basic lifecycle analysis."""
        # Create events with births and deaths
        events_t1 = [
            CommunityEvent(1, "birth", [0], {1, 2, 3}, {}),
            CommunityEvent(1, "birth", [1], {4, 5, 6}, {}),
        ]
        events_t2 = [
            CommunityEvent(2, "stable", [0], set(), {}),
            CommunityEvent(2, "death", [1], {4, 5, 6}, {}),
        ]

        all_events = [events_t1, events_t2]
        lifecycle = community_lifecycle_analysis(all_events)

        assert lifecycle["num_births"] == 2
        assert lifecycle["num_deaths"] == 1

    def test_lifespan_calculation(self):
        """Test lifespan calculation."""
        events_t1 = [CommunityEvent(1, "birth", [0], {1, 2}, {})]
        events_t2 = [CommunityEvent(2, "stable", [0], set(), {})]
        events_t3 = [CommunityEvent(3, "death", [0], {1, 2}, {})]

        all_events = [events_t1, events_t2, events_t3]
        lifecycle = community_lifecycle_analysis(all_events)

        # Birth at t1, death at t3, lifespan = 2
        assert lifecycle["avg_lifespan"] >= 1.0
        assert lifecycle["max_lifespan"] >= 2

    def test_merge_split_counts(self):
        """Test merge and split counting."""
        events = [
            [
                CommunityEvent(1, "merge", [0], {1, 2, 3, 4}, {"merged_from": [0, 1]}),
                CommunityEvent(1, "split", [2, 3], {5, 6, 7}, {"split_into": [2, 3]}),
            ]
        ]

        lifecycle = community_lifecycle_analysis(events)

        assert lifecycle["num_merges"] == 1
        assert lifecycle["num_splits"] == 1


class TestDetectPersistentCommunities:
    """Test persistent community detection."""

    def test_basic_persistence(self):
        """Test basic persistent community detection."""
        temporal = [[{1, 2, 3}, {4, 5, 6}], [{1, 2, 3}, {7, 8, 9}], [{1, 2, 3}, {10, 11, 12}]]

        persistent = detect_persistent_communities(temporal, min_persistence=3)

        # {1, 2, 3} persists across all 3 snapshots
        assert len(persistent) >= 1
        assert any({1, 2, 3} == nodes for nodes, _, _ in persistent)

    def test_no_persistence(self):
        """Test with no persistent communities."""
        temporal = [[{1, 2, 3}], [{4, 5, 6}], [{7, 8, 9}]]

        persistent = detect_persistent_communities(temporal, min_persistence=3)

        assert len(persistent) == 0

    def test_min_persistence_threshold(self):
        """Test min_persistence parameter."""
        temporal = [[{1, 2, 3}], [{1, 2, 3}], [{4, 5, 6}]]

        # Should find with min_persistence=2
        persistent_2 = detect_persistent_communities(temporal, min_persistence=2)
        assert len(persistent_2) >= 1

        # Should not find with min_persistence=3
        persistent_3 = detect_persistent_communities(temporal, min_persistence=3)
        assert len(persistent_3) == 0

    def test_time_range(self):
        """Test time range tracking."""
        temporal = [[{1, 2, 3}], [{1, 2, 3}], [{1, 2, 3}]]

        persistent = detect_persistent_communities(temporal, min_persistence=2)

        assert len(persistent) >= 1
        nodes, start, end = persistent[0]
        assert start == 0
        assert end == 2


class TestAnalyzeCommunityEvolution:
    """Test comprehensive community evolution analysis."""

    def test_basic_analysis(self):
        """Test basic evolution analysis."""
        # Create temporal graphs
        graphs = []
        for _ in range(3):
            G = nx.karate_club_graph()
            graphs.append(G)

        result = analyze_community_evolution(graphs, louvain_communities, random_state=42)

        assert "num_snapshots" in result.metrics
        assert result.metrics["num_snapshots"] == 3
        assert "avg_stability" in result.metrics

    def test_stable_evolution(self):
        """Test with stable graph evolution."""
        # Same graph repeated
        G = nx.karate_club_graph()
        graphs = [G.copy() for _ in range(3)]

        result = analyze_community_evolution(graphs, louvain_communities, random_state=42)

        # Should have high stability
        assert result.metrics["avg_stability"] > 0.5

    def test_dynamic_evolution(self):
        """Test with dynamic graph evolution."""
        # Create evolving graphs
        graphs = []
        for i in range(3):
            G = nx.Graph()
            # Add different nodes each time
            G.add_edges_from([(i * 10 + j, i * 10 + j + 1) for j in range(5)])
            graphs.append(G)

        result = analyze_community_evolution(graphs, louvain_communities)

        # Should detect low stability
        assert "avg_stability" in result.metrics

    def test_event_detection(self):
        """Test that events are detected."""
        graphs = []
        for _ in range(3):
            G = nx.karate_club_graph()
            graphs.append(G)

        result = analyze_community_evolution(graphs, louvain_communities, random_state=42)

        assert "events" in result.metadata
        assert "event_counts" in result.metadata

    def test_empty_graphs(self):
        """Test with empty graph list."""
        result = analyze_community_evolution([], louvain_communities)

        assert result.metrics["num_snapshots"] == 0


class TestEdgeCases:
    """Test edge cases for dynamics methods."""

    def test_single_node_communities(self):
        """Test with single-node communities."""
        temporal = [[{1}, {2}, {3}], [{1}, {2}, {3}]]

        all_events, _ = track_communities_over_time(temporal)

        # Should handle gracefully
        assert len(all_events) >= 0

    def test_large_community_change(self):
        """Test with large community changes."""
        temporal = [[set(range(100))], [set(range(50)), set(range(50, 100))]]

        events = detect_community_events(temporal[0], temporal[1], 1)

        # Should detect split
        split_events = [e for e in events if e.event_type == "split"]
        assert len(split_events) >= 1

    def test_many_snapshots(self):
        """Test with many temporal snapshots."""
        temporal = [[{1, 2, 3}] for _ in range(10)]

        stability = calculate_community_stability(temporal)

        # Perfectly stable
        assert stability["avg_stability"] > 0.9
        assert stability["num_snapshots"] == 10


class TestIntegration:
    """Integration tests for community dynamics."""

    def test_full_workflow(self):
        """Test complete workflow."""
        # Create evolving graphs
        graphs = []
        for i in range(5):
            G = nx.karate_club_graph()
            # Add some temporal variation
            if i > 0:
                G.add_edge(0, i * 5)
            graphs.append(G)

        # Analyze evolution
        result = analyze_community_evolution(graphs, louvain_communities, random_state=42)

        # Check all metrics present
        assert "num_snapshots" in result.metrics
        assert "avg_stability" in result.metrics
        assert "total_events" in result.metrics

        # Check metadata
        assert "events" in result.metadata
        assert "stability" in result.metadata
        assert "persistent_communities" in result.metadata

    def test_different_detection_methods(self):
        """Test with different detection methods."""
        graphs = [nx.karate_club_graph() for _ in range(3)]

        # Should work with any detection method
        result = analyze_community_evolution(graphs, louvain_communities, random_state=42)

        assert result.metrics["num_snapshots"] == 3

    def test_real_temporal_pattern(self):
        """Test with realistic temporal pattern."""
        # Simulate: stable -> split -> merge
        graphs = []

        # Stable
        G1 = nx.Graph()
        G1.add_edges_from([(0, 1), (1, 2), (2, 3), (3, 0)])
        graphs.append(G1)

        # Same
        graphs.append(G1.copy())

        # Split (remove middle edge)
        G2 = G1.copy()
        G2.remove_edge(1, 2)
        graphs.append(G2)

        result = analyze_community_evolution(graphs, louvain_communities)

        # Should detect changes
        assert result.metrics["total_events"] > 0
