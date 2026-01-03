# ----------------------------------------------------------------------
# © 2025 KR-Labs. All rights reserved.
# KR-Labs™ is a trademark of Quipu Research Labs, LLC,
# a subsidiary of Sudiata Giddasira, Inc.
# ----------------------------------------------------------------------
# SPDX-License-Identifier: Apache-2.0

"""
Tests for core network infrastructure.
"""

import networkx as nx
import pandas as pd
import pytest

from krl_network.core import (
    BaseNetwork,
    ComputationError,
    DataError,
    InvalidNetworkError,
    NetworkConfig,
    NetworkError,
    NetworkResult,
)
from krl_network.core.result import add_metric, get_metric, get_top_nodes


class ConcreteNetwork(BaseNetwork):
    """Concrete implementation for testing BaseNetwork."""

    @classmethod
    def from_dataframe(
        cls,
        df: pd.DataFrame,
        source_col: str,
        target_col: str,
        weight_col: str | None = None,
        **kwargs,
    ) -> "ConcreteNetwork":
        """Implement abstract method."""
        config = kwargs.get("config", NetworkConfig())
        network = cls(config=config)

        for _, row in df.iterrows():
            source = row[source_col]
            target = row[target_col]
            weight = row[weight_col] if weight_col else None
            network.add_edge(source, target, weight=weight)

        return network


@pytest.fixture
def simple_graph():
    """Create a simple test graph."""
    G = nx.Graph()
    G.add_edges_from([(1, 2), (2, 3), (3, 4), (4, 1)])
    return G


@pytest.fixture
def weighted_digraph():
    """Create a weighted directed graph."""
    G = nx.DiGraph()
    G.add_edge(1, 2, weight=1.0)
    G.add_edge(2, 3, weight=2.0)
    G.add_edge(3, 1, weight=0.5)
    return G


class TestNetworkConfig:
    """Tests for NetworkConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = NetworkConfig()
        assert config.directed is False
        assert config.weighted is True
        assert config.default_weight == 1.0
        assert config.self_loops is False
        assert config.cache_results is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = NetworkConfig(
            directed=True,
            weighted=False,
            default_weight=2.0,
            self_loops=True,
        )
        assert config.directed is True
        assert config.weighted is False
        assert config.default_weight == 2.0
        assert config.self_loops is True


class TestBaseNetwork:
    """Tests for BaseNetwork."""

    def test_initialization_empty(self):
        """Test creating an empty network."""
        network = ConcreteNetwork()
        assert network.num_nodes() == 0
        assert network.num_edges() == 0
        assert network.config.directed is False

    def test_initialization_with_graph(self, simple_graph):
        """Test creating network from existing graph."""
        network = ConcreteNetwork(graph=simple_graph)
        assert network.num_nodes() == 4
        assert network.num_edges() == 4

    def test_add_node(self):
        """Test adding nodes."""
        network = ConcreteNetwork()
        network.add_node(1)
        network.add_node(2, attributes={"label": "Node2"})

        assert network.has_node(1)
        assert network.has_node(2)
        assert network.get_node_attributes(2)["label"] == "Node2"

    def test_add_edge(self):
        """Test adding edges."""
        network = ConcreteNetwork()
        network.add_edge(1, 2, weight=1.5)
        network.add_edge(2, 3)

        assert network.has_edge(1, 2)
        assert network.has_edge(2, 3)
        assert network.get_edge_attributes(1, 2)["weight"] == 1.5

    def test_remove_node(self):
        """Test removing nodes."""
        network = ConcreteNetwork()
        network.add_node(1)
        network.add_node(2)
        network.add_edge(1, 2)

        network.remove_node(1)
        assert not network.has_node(1)
        assert network.has_node(2)
        assert not network.has_edge(1, 2)

    def test_remove_edge(self):
        """Test removing edges."""
        network = ConcreteNetwork()
        network.add_edge(1, 2)
        network.add_edge(2, 3)

        network.remove_edge(1, 2)
        assert not network.has_edge(1, 2)
        assert network.has_edge(2, 3)

    def test_neighbors(self):
        """Test getting neighbors."""
        network = ConcreteNetwork()
        network.add_edge(1, 2)
        network.add_edge(1, 3)
        network.add_edge(2, 3)

        neighbors_1 = network.neighbors(1)
        assert 2 in neighbors_1
        assert 3 in neighbors_1

    def test_degree(self):
        """Test degree calculation."""
        network = ConcreteNetwork()
        network.add_edge(1, 2)
        network.add_edge(1, 3)
        network.add_edge(2, 3)

        assert network.degree(1) == 2
        assert network.degree(2) == 2
        assert network.degree(3) == 2

    def test_density(self, simple_graph):
        """Test density calculation."""
        network = ConcreteNetwork(graph=simple_graph)
        density = network.density()
        assert 0.0 <= density <= 1.0

    def test_is_connected(self):
        """Test connectivity check."""
        network = ConcreteNetwork()
        network.add_edge(1, 2)
        network.add_edge(2, 3)
        assert network.is_connected()

        network.add_node(4)
        assert not network.is_connected()

    def test_connected_components(self):
        """Test getting connected components."""
        network = ConcreteNetwork()
        network.add_edge(1, 2)
        network.add_edge(3, 4)

        components = network.connected_components()
        assert len(components) == 2

    def test_subgraph(self, simple_graph):
        """Test creating subgraph."""
        network = ConcreteNetwork(graph=simple_graph)
        sub = network.subgraph([1, 2, 3])

        assert sub.num_nodes() == 3
        assert sub.has_edge(1, 2)
        assert sub.has_edge(2, 3)
        assert not sub.has_node(4)

    def test_to_dataframe(self):
        """Test converting to DataFrames."""
        network = ConcreteNetwork()
        network.add_edge(1, 2, weight=1.0)
        network.add_edge(2, 3, weight=2.0)

        nodes_df, edges_df = network.to_dataframe()

        assert len(nodes_df) == 3
        assert len(edges_df) == 2
        assert "source" in edges_df.columns
        assert "target" in edges_df.columns

    def test_validate_success(self):
        """Test successful validation."""
        network = ConcreteNetwork()
        network.add_edge(1, 2)
        network.add_edge(2, 3)

        assert network.validate() is True

    def test_validate_self_loops(self):
        """Test validation with self-loops."""
        config = NetworkConfig(self_loops=False)
        network = ConcreteNetwork(config=config)
        network.graph.add_edge(1, 1)

        with pytest.raises(InvalidNetworkError, match="self-loops"):
            network.validate()

    def test_validate_negative_weights(self):
        """Test validation with negative weights."""
        network = ConcreteNetwork()
        network.graph.add_edge(1, 2, weight=-1.0)

        with pytest.raises(InvalidNetworkError, match="negative weights"):
            network.validate()

    def test_summary(self, simple_graph):
        """Test generating network summary."""
        network = ConcreteNetwork(graph=simple_graph, name="TestNet")
        summary = network.summary()

        assert "TestNet" in summary
        assert "Nodes: 4" in summary
        assert "Edges: 4" in summary

    def test_len(self, simple_graph):
        """Test __len__ returns number of nodes."""
        network = ConcreteNetwork(graph=simple_graph)
        assert len(network) == 4

    def test_contains(self, simple_graph):
        """Test __contains__ checks node membership."""
        network = ConcreteNetwork(graph=simple_graph)
        assert 1 in network
        assert 5 not in network

    def test_repr(self):
        """Test string representation."""
        network = ConcreteNetwork(name="TestNetwork")
        network.add_edge(1, 2)

        repr_str = repr(network)
        assert "ConcreteNetwork" in repr_str
        assert "TestNetwork" in repr_str


class TestNetworkResult:
    """Tests for NetworkResult."""

    def test_initialization_empty(self):
        """Test creating empty result."""
        result = NetworkResult()
        assert len(result.metrics) == 0
        assert result.nodes is None
        assert result.communities is None

    def test_initialization_with_data(self):
        """Test creating result with data."""
        metrics = {"density": 0.5, "num_nodes": 10}
        nodes_df = pd.DataFrame({"node": [1, 2, 3], "centrality": [0.5, 0.8, 0.3]})

        result = NetworkResult(metrics=metrics, nodes=nodes_df)

        assert result.metrics["density"] == 0.5
        assert len(result.nodes) == 3

    def test_add_metric(self):
        """Test adding metrics."""
        result = NetworkResult()
        add_metric(result, "density", 0.75)
        add_metric(result, "diameter", 5)

        assert get_metric(result, "density") == 0.75
        assert get_metric(result, "diameter") == 5

    def test_get_metric_default(self):
        """Test getting metric with default value."""
        result = NetworkResult()
        assert get_metric(result, "nonexistent", default=0) == 0

    def test_get_top_nodes(self):
        """Test getting top nodes by metric."""
        nodes_df = pd.DataFrame(
            {
                "node": [1, 2, 3, 4, 5],
                "centrality": [0.1, 0.9, 0.3, 0.7, 0.5],
            }
        )
        result = NetworkResult(nodes=nodes_df)

        top_nodes = get_top_nodes(result, "centrality", n=3)

        assert len(top_nodes) == 3
        assert top_nodes.iloc[0]["node"] == 2  # Highest centrality

    def test_summary(self):
        """Test generating result summary."""
        result = NetworkResult(
            metrics={"density": 0.5, "diameter": 4},
            nodes=pd.DataFrame({"node": [1, 2, 3]}),
        )

        summary = result.summary()

        assert "Network Analysis Results" in summary
        assert "density" in summary
        assert "Nodes: 3" in summary

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = NetworkResult(metrics={"density": 0.5})
        result_dict = result.to_dict()

        assert "metrics" in result_dict
        assert "nodes" in result_dict
        assert result_dict["metrics"]["density"] == 0.5


class TestExceptions:
    """Tests for custom exceptions."""

    def test_network_error(self):
        """Test NetworkError."""
        with pytest.raises(NetworkError):
            raise NetworkError("Test error")

    def test_invalid_network_error(self):
        """Test InvalidNetworkError."""
        with pytest.raises(InvalidNetworkError):
            raise InvalidNetworkError("Invalid network")

    def test_computation_error(self):
        """Test ComputationError."""
        with pytest.raises(ComputationError):
            raise ComputationError("Computation failed")

    def test_data_error(self):
        """Test DataError."""
        with pytest.raises(DataError):
            raise DataError("Invalid data")

    def test_exception_inheritance(self):
        """Test exception inheritance."""
        assert issubclass(InvalidNetworkError, NetworkError)
        assert issubclass(ComputationError, NetworkError)
        assert issubclass(DataError, NetworkError)
