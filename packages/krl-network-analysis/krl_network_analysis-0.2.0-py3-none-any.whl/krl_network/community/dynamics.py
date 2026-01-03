"""
© 2025 KR-Labs. All rights reserved.
KR-Labs™ is a trademark of Quipu Research Labs, LLC, a subsidiary of Sudiata Giddasira, Inc.

SPDX-License-Identifier: Apache-2.0

Community dynamics and evolution tracking.
"""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Set, Tuple

import networkx as nx
import numpy as np

from krl_network.core.exceptions import ComputationError
from krl_network.core.result import NetworkResult


@dataclass
class CommunityEvent:
    """Represents a community evolution event."""

    timestamp: int
    event_type: str  # 'birth', 'death', 'merge', 'split', 'growth', 'shrink', 'stable'
    communities_involved: List[int]
    nodes_affected: Set[Any]
    metadata: Dict[str, Any]


def jaccard_similarity(set1: Set[Any], set2: Set[Any]) -> float:
    """Calculate Jaccard similarity between two sets.

    Args:
        set1: First set
        set2: Second set

    Returns:
        Jaccard similarity [0, 1]
    """
    if not set1 and not set2:
        return 1.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    return intersection / union if union > 0 else 0.0


def match_communities(
    communities_t1: List[Set[Any]], communities_t2: List[Set[Any]], threshold: float = 0.5
) -> Dict[int, int]:
    """Match communities between two time steps.

    Args:
        communities_t1: Communities at time t1
        communities_t2: Communities at time t2
        threshold: Minimum similarity for matching

    Returns:
        Dict mapping t1 community indices to t2 indices
    """
    matches = {}

    # Calculate similarity matrix
    n1 = len(communities_t1)
    n2 = len(communities_t2)

    if n1 == 0 or n2 == 0:
        return matches

    similarity = np.zeros((n1, n2))

    for i, c1 in enumerate(communities_t1):
        for j, c2 in enumerate(communities_t2):
            similarity[i, j] = jaccard_similarity(c1, c2)

    # Greedy matching: highest similarity first
    used_t2 = set()

    for i in range(n1):
        best_j = None
        best_sim = -1  # Start below threshold so >= threshold will match

        for j in range(n2):
            if j not in used_t2 and similarity[i, j] >= threshold and similarity[i, j] > best_sim:
                best_j = j
                best_sim = similarity[i, j]

        if best_j is not None:
            matches[i] = best_j
            used_t2.add(best_j)

    return matches


def detect_community_events(
    communities_prev: List[Set[Any]],
    communities_curr: List[Set[Any]],
    timestamp: int,
    similarity_threshold: float = 0.5,
) -> List[CommunityEvent]:
    """Detect events between consecutive community snapshots.

    Args:
        communities_prev: Communities at previous time
        communities_curr: Communities at current time
        timestamp: Current timestamp
        similarity_threshold: Threshold for matching

    Returns:
        List of detected events
    """
    events = []

    # Track nodes in each community
    nodes_prev = {i: comm for i, comm in enumerate(communities_prev)}
    nodes_curr = {i: comm for i, comm in enumerate(communities_curr)}

    # Build ALL similarities above threshold (not just greedy matches)
    # This is needed to detect merges (multiple prev -> one curr) and splits (one prev -> multiple curr)
    similarities = []
    for i in range(len(communities_prev)):
        for j in range(len(communities_curr)):
            sim = jaccard_similarity(nodes_prev[i], nodes_curr[j])
            if sim >= similarity_threshold:
                similarities.append((i, j, sim))

    # Detect merges: multiple prev communities similar to one curr community
    curr_to_prev = defaultdict(list)
    for i, j, sim in similarities:
        curr_to_prev[j].append((i, sim))

    merge_involved_prev = set()
    merge_involved_curr = set()
    for j, prev_list in curr_to_prev.items():
        if len(prev_list) > 1:
            merged_nodes = set()
            prev_indices = []
            for i, sim in prev_list:
                merged_nodes.update(nodes_prev[i])
                merge_involved_prev.add(i)
                prev_indices.append(i)
            merge_involved_curr.add(j)

            events.append(
                CommunityEvent(
                    timestamp=timestamp,
                    event_type="merge",
                    communities_involved=[j],
                    nodes_affected=merged_nodes,
                    metadata={"merged_from": prev_indices},
                )
            )

    # Detect splits: one prev community similar to multiple curr communities
    prev_to_curr = defaultdict(list)
    for i, j, sim in similarities:
        prev_to_curr[i].append((j, sim))

    split_involved = set()
    for i, curr_list in prev_to_curr.items():
        if len(curr_list) > 1 and i not in merge_involved_prev:
            split_nodes = nodes_prev[i]
            curr_indices = []
            for j, sim in curr_list:
                if j not in merge_involved_curr:
                    split_involved.add(j)
                    curr_indices.append(j)

            if len(curr_indices) > 1:  # Only count as split if multiple curr communities
                events.append(
                    CommunityEvent(
                        timestamp=timestamp,
                        event_type="split",
                        communities_involved=curr_indices,
                        nodes_affected=split_nodes,
                        metadata={"split_into": curr_indices},
                    )
                )

    # For remaining communities (not involved in merge/split), use greedy matching for growth/shrink/stable
    matches = match_communities(communities_prev, communities_curr, similarity_threshold)

    for i, j in matches.items():
        if i in merge_involved_prev or j in merge_involved_curr or j in split_involved:
            continue  # Skip - already handled as merge/split

        prev_nodes = nodes_prev[i]
        curr_nodes = nodes_curr[j]

        # Growth/shrink
        if len(curr_nodes) > len(prev_nodes) * 1.2:
            events.append(
                CommunityEvent(
                    timestamp=timestamp,
                    event_type="growth",
                    communities_involved=[j],
                    nodes_affected=curr_nodes - prev_nodes,
                    metadata={"size_change": len(curr_nodes) - len(prev_nodes)},
                )
            )
        elif len(curr_nodes) < len(prev_nodes) * 0.8:
            events.append(
                CommunityEvent(
                    timestamp=timestamp,
                    event_type="shrink",
                    communities_involved=[j],
                    nodes_affected=prev_nodes - curr_nodes,
                    metadata={"size_change": len(prev_nodes) - len(curr_nodes)},
                )
            )
        else:
            # Stable
            events.append(
                CommunityEvent(
                    timestamp=timestamp,
                    event_type="stable",
                    communities_involved=[j],
                    nodes_affected=set(),
                    metadata={"jaccard": jaccard_similarity(prev_nodes, curr_nodes)},
                )
            )

    # Detect deaths: prev communities not involved in any event
    for i in range(len(communities_prev)):
        if i not in matches and i not in merge_involved_prev:
            events.append(
                CommunityEvent(
                    timestamp=timestamp,
                    event_type="death",
                    communities_involved=[i],
                    nodes_affected=nodes_prev[i],
                    metadata={},
                )
            )

    # Detect births: curr communities not involved in any event
    # These are communities that don't have any similar predecessor
    matched_curr = set(matches.values())
    for j in range(len(communities_curr)):
        if j not in matched_curr and j not in merge_involved_curr and j not in split_involved:
            events.append(
                CommunityEvent(
                    timestamp=timestamp,
                    event_type="birth",
                    communities_involved=[j],
                    nodes_affected=nodes_curr[j],
                    metadata={},
                )
            )

    return events


def track_communities_over_time(
    temporal_communities: List[List[Set[Any]]], similarity_threshold: float = 0.5
) -> Tuple[List[List[CommunityEvent]], Dict[str, int]]:
    """Track community evolution over time.

    Args:
        temporal_communities: List of community snapshots (one per timestamp)
        similarity_threshold: Threshold for matching

    Returns:
        Tuple of (events per timestamp, event counts by type)
    """
    if len(temporal_communities) < 2:
        return [], {}

    all_events = []
    event_counts = defaultdict(int)

    for t in range(1, len(temporal_communities)):
        events = detect_community_events(
            temporal_communities[t - 1], temporal_communities[t], t, similarity_threshold
        )

        all_events.append(events)

        for event in events:
            event_counts[event.event_type] += 1

    return all_events, dict(event_counts)


def calculate_community_stability(
    temporal_communities: List[List[Set[Any]]], window_size: int = 3
) -> Dict[str, float]:
    """Calculate stability metrics for temporal communities.

    Args:
        temporal_communities: List of community snapshots
        window_size: Window for stability calculation

    Returns:
        Dict of stability metrics
    """
    if len(temporal_communities) < 2:
        return {"avg_stability": 0.0, "num_snapshots": len(temporal_communities)}

    # Track community membership stability
    stabilities = []

    for t in range(1, len(temporal_communities)):
        matches = match_communities(
            temporal_communities[t - 1], temporal_communities[t], threshold=0.3
        )

        if matches:
            # Calculate average Jaccard for matched communities
            jaccards = []
            for i, j in matches.items():
                jacc = jaccard_similarity(
                    temporal_communities[t - 1][i], temporal_communities[t][j]
                )
                jaccards.append(jacc)

            stabilities.append(np.mean(jaccards))

    # Number of communities over time
    num_communities = [len(comms) for comms in temporal_communities]

    # Stability of community count
    if len(num_communities) > 1:
        count_stability = 1.0 - (np.std(num_communities) / (np.mean(num_communities) + 1e-10))
    else:
        count_stability = 1.0

    return {
        "avg_stability": float(np.mean(stabilities)) if stabilities else 0.0,
        "min_stability": float(np.min(stabilities)) if stabilities else 0.0,
        "max_stability": float(np.max(stabilities)) if stabilities else 0.0,
        "count_stability": float(max(0.0, count_stability)),
        "num_snapshots": len(temporal_communities),
    }


def community_lifecycle_analysis(all_events: List[List[CommunityEvent]]) -> Dict[str, Any]:
    """Analyze community lifecycles from events.

    Args:
        all_events: Events per timestamp

    Returns:
        Lifecycle statistics
    """
    # Track community lifespans
    community_births = {}  # comm_id -> birth_time
    community_deaths = {}  # comm_id -> death_time

    for t, events in enumerate(all_events):
        for event in events:
            if event.event_type == "birth":
                for comm_id in event.communities_involved:
                    if comm_id not in community_births:
                        community_births[comm_id] = t

            elif event.event_type == "death":
                for comm_id in event.communities_involved:
                    if comm_id in community_births and comm_id not in community_deaths:
                        community_deaths[comm_id] = t

    # Calculate lifespans
    lifespans = []
    for comm_id in community_births:
        birth = community_births[comm_id]
        death = community_deaths.get(comm_id, len(all_events))
        lifespans.append(death - birth)

    # Event statistics
    event_types = defaultdict(int)
    for events in all_events:
        for event in events:
            event_types[event.event_type] += 1

    return {
        "avg_lifespan": float(np.mean(lifespans)) if lifespans else 0.0,
        "max_lifespan": int(max(lifespans)) if lifespans else 0,
        "min_lifespan": int(min(lifespans)) if lifespans else 0,
        "num_births": int(event_types["birth"]),
        "num_deaths": int(event_types["death"]),
        "num_merges": int(event_types["merge"]),
        "num_splits": int(event_types["split"]),
        "event_counts": dict(event_types),
    }


def detect_persistent_communities(
    temporal_communities: List[List[Set[Any]]],
    min_persistence: int = 3,
    similarity_threshold: float = 0.5,
) -> List[Tuple[Set[Any], int, int]]:
    """Detect communities that persist across multiple snapshots.

    Args:
        temporal_communities: List of community snapshots
        min_persistence: Minimum number of consecutive snapshots
        similarity_threshold: Matching threshold

    Returns:
        List of (community_nodes, start_time, end_time)
    """
    if len(temporal_communities) < min_persistence:
        return []

    persistent = []

    # Track each community's persistence
    active_tracks = []  # List of (nodes, start_time, last_time)

    for t in range(len(temporal_communities)):
        current_comms = temporal_communities[t]
        new_tracks = []
        matched_comms = set()

        # Try to extend existing tracks
        for nodes, start, last in active_tracks:
            best_match = None
            best_sim = similarity_threshold

            for i, comm in enumerate(current_comms):
                if i not in matched_comms:
                    sim = jaccard_similarity(nodes, comm)
                    if sim > best_sim:
                        best_match = i
                        best_sim = sim

            if best_match is not None:
                matched_comms.add(best_match)
                new_tracks.append((current_comms[best_match], start, t))
            else:
                # Track ended
                if t - start >= min_persistence:
                    persistent.append((nodes, start, last))

        # Start new tracks for unmatched communities
        for i, comm in enumerate(current_comms):
            if i not in matched_comms:
                new_tracks.append((comm, t, t))

        active_tracks = new_tracks

    # Add remaining active tracks that meet persistence criterion
    for nodes, start, last in active_tracks:
        if last - start + 1 >= min_persistence:
            persistent.append((nodes, start, last))

    return persistent


def analyze_community_evolution(
    graphs: List[nx.Graph],
    detection_method: Callable,
    similarity_threshold: float = 0.5,
    **detection_kwargs,
) -> NetworkResult:
    """Comprehensive community evolution analysis.

    Args:
        graphs: List of temporal graph snapshots
        detection_method: Community detection function
        similarity_threshold: Matching threshold
        **detection_kwargs: Arguments for detection method

    Returns:
        NetworkResult with evolution analysis
    """
    if len(graphs) == 0:
        return NetworkResult(
            metrics={"num_snapshots": 0}, nodes={}, metadata={"method": "evolution_analysis"}
        )

    # Detect communities at each timestamp
    temporal_communities = []

    for graph in graphs:
        try:
            communities = detection_method(graph, **detection_kwargs)
            # Ensure it's a list of sets
            if isinstance(communities, list):
                if communities and isinstance(communities[0], set):
                    temporal_communities.append(communities)
                else:
                    # Convert to sets if needed
                    temporal_communities.append([set(c) for c in communities])
            else:
                temporal_communities.append([])
        except:
            temporal_communities.append([])

    # Track events
    all_events, event_counts = track_communities_over_time(
        temporal_communities, similarity_threshold
    )

    # Stability analysis
    stability = calculate_community_stability(temporal_communities)

    # Lifecycle analysis
    lifecycle = community_lifecycle_analysis(all_events)

    # Persistent communities
    persistent = detect_persistent_communities(
        temporal_communities,
        min_persistence=max(2, len(graphs) // 3),
        similarity_threshold=similarity_threshold,
    )

    return NetworkResult(
        metrics={
            "num_snapshots": len(graphs),
            "avg_communities_per_snapshot": float(np.mean([len(c) for c in temporal_communities])),
            "avg_stability": stability["avg_stability"],
            "count_stability": stability["count_stability"],
            "num_persistent_communities": len(persistent),
            "total_events": sum(event_counts.values()),
            **lifecycle,
        },
        nodes={},
        metadata={
            "method": "evolution_analysis",
            "temporal_communities": temporal_communities,
            "events": all_events,
            "event_counts": event_counts,
            "stability": stability,
            "persistent_communities": persistent,
            "detection_method": (
                detection_method.__name__ if hasattr(detection_method, "__name__") else "unknown"
            ),
        },
    )
