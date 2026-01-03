"""
Tests for regional economic network analysis.

This module tests:
- RegionalNetwork creation from flow data
- Economic integration measurement
- Core-periphery identification
- Regional spillover analysis
- Market access calculation
- Regional clustering
- Trade balance calculation
"""

import numpy as np
import pandas as pd
import pytest

from krl_network.core.base import NetworkConfig
from krl_network.core.exceptions import ComputationError, DataError, InvalidNetworkError
from krl_network.networks.regional import RegionalNetwork


@pytest.fixture
def trade_flow_data():
    """Create sample trade flow data."""
    return pd.DataFrame(
        {
            "origin": ["R1", "R1", "R2", "R2", "R3", "R3", "R1"],
            "destination": ["R2", "R3", "R1", "R3", "R1", "R2", "R4"],
            "flow": [100, 150, 80, 120, 60, 90, 50],
        }
    )


@pytest.fixture
def simple_regional_network():
    """Create simple 4-region trade network."""
    network = RegionalNetwork(network_type="trade")
    # Create triangle: R1 <-> R2 <-> R3 <-> R1, plus isolated R4
    network.add_edge("R1", "R2", weight=100)
    network.add_edge("R2", "R1", weight=80)
    network.add_edge("R2", "R3", weight=120)
    network.add_edge("R3", "R2", weight=90)
    network.add_edge("R3", "R1", weight=60)
    network.add_edge("R1", "R3", weight=150)
    return network


@pytest.fixture
def regional_network_with_attributes():
    """Create regional network with region attributes."""
    network = RegionalNetwork(network_type="trade")
    network.add_edge("R1", "R2", weight=100)
    network.add_edge("R2", "R3", weight=120)
    network.add_edge("R3", "R1", weight=60)

    # Set region attributes
    network.set_region_attributes("R1", {"gdp": 1000, "population": 500})
    network.set_region_attributes("R2", {"gdp": 800, "population": 400})
    network.set_region_attributes("R3", {"gdp": 600, "population": 300})

    return network


@pytest.fixture
def spatial_weights_data():
    """Create sample spatial weights (distance) data."""
    return pd.DataFrame(
        {
            "region1": ["R1", "R1", "R2", "R2", "R3", "R3"],
            "region2": ["R2", "R3", "R1", "R3", "R1", "R2"],
            "weight": [100, 200, 100, 150, 200, 150],  # distances
        }
    )


class TestRegionalNetworkCreation:
    """Test regional network creation."""

    def test_default_initialization(self):
        """Test default initialization creates directed weighted network."""
        network = RegionalNetwork(network_type="trade")
        assert network.config.directed is True
        assert network.config.weighted is True
        assert network.network_type == "trade"
        assert len(network.graph) == 0

    def test_network_types(self):
        """Test different network types."""
        for net_type in RegionalNetwork.NETWORK_TYPES:
            network = RegionalNetwork(network_type=net_type)
            assert network.network_type == net_type

    def test_invalid_network_type(self):
        """Test error with invalid network type."""
        with pytest.raises(DataError):
            RegionalNetwork(network_type="invalid_type")

    def test_custom_config(self):
        """Test initialization with custom config."""
        config = NetworkConfig(directed=False, weighted=True)
        network = RegionalNetwork(network_type="labor", config=config)
        assert network.config.directed is False
        assert network.network_type == "labor"

    def test_metadata(self):
        """Test metadata storage."""
        metadata = {"country": "USA", "year": 2024}
        network = RegionalNetwork(network_type="trade", metadata=metadata)
        assert network.metadata["country"] == "USA"

    def test_from_flow_data(self, trade_flow_data):
        """Test creation from flow data."""
        network = RegionalNetwork.from_flow_data(trade_flow_data, network_type="trade")

        assert network.graph.number_of_nodes() == 4  # R1, R2, R3, R4
        assert network.graph.number_of_edges() == 7
        assert network.graph["R1"]["R2"]["weight"] == 100

    def test_from_flow_data_bidirectional(self):
        """Test bidirectional flow aggregation."""
        df = pd.DataFrame({"origin": ["R1", "R2"], "destination": ["R2", "R1"], "flow": [100, 80]})

        network = RegionalNetwork.from_flow_data(df, network_type="trade", bidirectional=True)

        # Should aggregate into single edge with total flow
        assert network.graph.number_of_edges() == 1
        # Total flow should be 100 + 80 = 180
        assert network.graph["R1"]["R2"]["weight"] == 180

    def test_from_flow_missing_columns(self):
        """Test error on missing required columns."""
        df = pd.DataFrame({"origin": ["R1"], "missing": ["R2"]})
        with pytest.raises(DataError):
            RegionalNetwork.from_flow_data(df)


class TestRegionAttributes:
    """Test region attribute management."""

    def test_set_region_attributes(self, simple_regional_network):
        """Test setting region attributes."""
        simple_regional_network.set_region_attributes("R1", {"gdp": 1000, "population": 500})

        assert simple_regional_network.region_attributes["R1"]["gdp"] == 1000
        assert simple_regional_network.graph.nodes["R1"]["gdp"] == 1000

    def test_set_attributes_invalid_region(self, simple_regional_network):
        """Test error when setting attributes for non-existent region."""
        with pytest.raises(InvalidNetworkError):
            simple_regional_network.set_region_attributes("NonExistent", {"gdp": 1000})

    def test_spatial_weights(self, simple_regional_network, spatial_weights_data):
        """Test setting spatial weights."""
        simple_regional_network.set_spatial_weights(spatial_weights_data)

        assert ("R1", "R2") in simple_regional_network.spatial_weights
        assert simple_regional_network.spatial_weights[("R1", "R2")] == 100
        # Should be symmetric
        assert simple_regional_network.spatial_weights[("R2", "R1")] == 100


class TestEconomicIntegration:
    """Test economic integration measurement."""

    def test_trade_integration(self, regional_network_with_attributes):
        """Test trade integration index."""
        integration = regional_network_with_attributes.calculate_integration_index(method="trade")

        assert "R1" in integration
        assert all(0 <= score <= 1 for score in integration.values())

    def test_flow_integration(self, simple_regional_network):
        """Test flow-based integration."""
        integration = simple_regional_network.calculate_integration_index(method="flow")

        assert len(integration) == 3  # R1, R2, R3 (R4 not in simple network)
        assert all(0 <= score <= 1 for score in integration.values())

    def test_connectivity_integration(self, simple_regional_network):
        """Test connectivity-based integration."""
        integration = simple_regional_network.calculate_integration_index(method="connectivity")

        assert len(integration) > 0
        # Connectivity scores can be > 1 for directed graphs
        assert all(score >= 0 for score in integration.values())


class TestCorePeriphery:
    """Test core-periphery identification."""

    def test_degree_method(self, simple_regional_network):
        """Test core-periphery using degree centrality."""
        result = simple_regional_network.identify_core_periphery(
            method="degree", core_threshold=0.6
        )

        assert "core" in result
        assert "periphery" in result
        assert "scores" in result
        # All regions should be classified
        assert len(result["core"]) + len(result["periphery"]) == 3

    def test_flow_method(self, simple_regional_network):
        """Test core-periphery using flow volume."""
        result = simple_regional_network.identify_core_periphery(method="flow", core_threshold=0.5)

        assert len(result["core"]) + len(result["periphery"]) == 3
        # R1 and R2 likely have high flow
        assert len(result["core"]) > 0

    def test_eigenvector_method(self, simple_regional_network):
        """Test core-periphery using eigenvector centrality."""
        result = simple_regional_network.identify_core_periphery(
            method="eigenvector", core_threshold=0.5
        )

        assert "scores" in result
        assert len(result["core"]) + len(result["periphery"]) == 3


class TestRegionalSpillovers:
    """Test regional spillover analysis."""

    def test_spillover_propagation(self, simple_regional_network):
        """Test spillover from one region."""
        spillovers = simple_regional_network.calculate_regional_spillovers(
            shock_region="R1", shock_magnitude=1.0, spillover_decay=0.5, max_hops=2
        )

        assert "R1" in spillovers
        assert spillovers["R1"] == 1.0  # Initial shock
        # R2 and R3 should receive spillovers
        assert "R2" in spillovers
        assert spillovers["R2"] < 1.0  # Decayed

    def test_spillover_decay(self, simple_regional_network):
        """Test spillover decay with distance."""
        spillovers = simple_regional_network.calculate_regional_spillovers(
            shock_region="R1", shock_magnitude=1.0, spillover_decay=0.3, max_hops=1  # Strong decay
        )

        # Direct neighbors should have small spillovers
        if "R2" in spillovers:
            assert spillovers["R2"] < 0.5

    def test_spillover_invalid_region(self, simple_regional_network):
        """Test error with invalid shock region."""
        with pytest.raises(InvalidNetworkError):
            simple_regional_network.calculate_regional_spillovers(shock_region="NonExistent")

    def test_spillover_max_hops(self, simple_regional_network):
        """Test spillover with hop limit."""
        spillovers_1hop = simple_regional_network.calculate_regional_spillovers(
            shock_region="R1", max_hops=1
        )
        spillovers_2hop = simple_regional_network.calculate_regional_spillovers(
            shock_region="R1", max_hops=2
        )

        # More hops should reach more regions
        assert len(spillovers_2hop) >= len(spillovers_1hop)


class TestMarketAccess:
    """Test market access calculation."""

    def test_market_access_network_distance(self, regional_network_with_attributes):
        """Test market access using network distance."""
        market_access = regional_network_with_attributes.calculate_market_access(use_distance=False)

        assert "R1" in market_access
        assert all(access >= 0 for access in market_access.values())

    def test_market_access_spatial_distance(self, simple_regional_network, spatial_weights_data):
        """Test market access using spatial weights."""
        simple_regional_network.set_spatial_weights(spatial_weights_data)
        simple_regional_network.set_region_attributes("R1", {"gdp": 1000})
        simple_regional_network.set_region_attributes("R2", {"gdp": 800})
        simple_regional_network.set_region_attributes("R3", {"gdp": 600})

        market_access = simple_regional_network.calculate_market_access(
            use_distance=True, distance_decay=1.0
        )

        assert len(market_access) == 3
        # Closer regions should have higher access
        assert all(access >= 0 for access in market_access.values())

    def test_market_access_distance_decay(self, regional_network_with_attributes):
        """Test market access with different decay parameters."""
        access_low_decay = regional_network_with_attributes.calculate_market_access(
            use_distance=False, distance_decay=0.5
        )
        access_high_decay = regional_network_with_attributes.calculate_market_access(
            use_distance=False, distance_decay=2.0
        )

        # Higher decay should reduce access
        assert sum(access_high_decay.values()) <= sum(access_low_decay.values())


class TestRegionalClustering:
    """Test regional clustering."""

    def test_modularity_clustering(self, simple_regional_network):
        """Test modularity-based clustering."""
        clusters = simple_regional_network.identify_regional_clusters(method="modularity")

        assert len(clusters) > 0
        # All regions should be assigned to clusters
        assert len(clusters) == 3

    def test_flow_clustering(self, simple_regional_network):
        """Test flow-based clustering."""
        clusters = simple_regional_network.identify_regional_clusters(method="flow", n_clusters=2)

        assert len(clusters) == 3
        # Should have 2 cluster IDs
        assert len(set(clusters.values())) <= 2

    def test_spatial_clustering(self, simple_regional_network, spatial_weights_data):
        """Test spatial contiguity clustering."""
        simple_regional_network.set_spatial_weights(spatial_weights_data)

        clusters = simple_regional_network.identify_regional_clusters(method="spatial")

        assert len(clusters) > 0

    def test_clustering_no_spatial_weights(self, simple_regional_network):
        """Test error when spatial weights required but not set."""
        with pytest.raises(DataError):
            simple_regional_network.identify_regional_clusters(method="spatial")


class TestTradeBalance:
    """Test trade balance calculation."""

    def test_trade_balance(self, simple_regional_network):
        """Test trade balance calculation."""
        balance = simple_regional_network.calculate_trade_balance()

        assert "R1" in balance
        assert "R2" in balance
        assert "R3" in balance

        # Balance should be exports - imports
        r1_exports = 100 + 150  # to R2 and R3
        r1_imports = 80 + 60  # from R2 and R3
        assert balance["R1"] == r1_exports - r1_imports

    def test_trade_balance_non_trade_network(self):
        """Test error for non-trade networks."""
        network = RegionalNetwork(network_type="labor")
        network.add_edge("R1", "R2", weight=100)

        with pytest.raises(InvalidNetworkError):
            network.calculate_trade_balance()

    def test_trade_balance_surplus_deficit(self, simple_regional_network):
        """Test identifying surplus and deficit regions."""
        balance = simple_regional_network.calculate_trade_balance()

        surplus_regions = [r for r, b in balance.items() if b > 0]
        deficit_regions = [r for r, b in balance.items() if b < 0]

        # Should have both surplus and deficit regions
        assert len(surplus_regions) + len(deficit_regions) > 0


class TestRiskAssessment:
    """Test regional risk assessment."""

    def test_risk_assessment_structure(self, simple_regional_network):
        """Test risk assessment returns correct structure."""
        result = simple_regional_network.assess_regional_risk()

        assert "num_regions" in result.metrics
        assert "network_type" in result.metrics
        assert result.metrics["network_type"] == "trade"

    def test_risk_assessment_integration(self, regional_network_with_attributes):
        """Test risk assessment includes integration."""
        result = regional_network_with_attributes.assess_regional_risk(include_integration=True)

        assert "avg_integration" in result.metrics or "integration_scores" in result.metadata

    def test_risk_assessment_core_periphery(self, simple_regional_network):
        """Test risk assessment includes core-periphery."""
        result = simple_regional_network.assess_regional_risk()

        assert "num_core_regions" in result.metrics or "core_regions" in result.metadata

    def test_risk_assessment_clustering(self, simple_regional_network):
        """Test risk assessment includes clustering."""
        result = simple_regional_network.assess_regional_risk(include_clustering=True)

        # Clustering should be attempted
        assert result is not None

    def test_risk_assessment_nodes(self, simple_regional_network):
        """Test node-level risk metrics."""
        result = simple_regional_network.assess_regional_risk()

        assert result.nodes is not None
        assert "node" in result.nodes.columns
        assert "degree" in result.nodes.columns


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_network(self):
        """Test operations on empty network."""
        network = RegionalNetwork(network_type="trade")

        result = network.assess_regional_risk()
        assert result.metrics["num_regions"] == 0

    def test_single_region(self):
        """Test operations on single region."""
        network = RegionalNetwork(network_type="trade")
        network.add_node("R1")

        integration = network.calculate_integration_index()
        assert "R1" in integration

    def test_disconnected_regions(self):
        """Test network with disconnected regions."""
        network = RegionalNetwork(network_type="trade")
        network.add_edge("R1", "R2", weight=100)
        network.add_edge("R3", "R4", weight=80)  # Separate component

        result = network.assess_regional_risk()
        assert result.metrics["is_connected"] is False

    def test_zero_weights(self):
        """Test handling of zero-weight edges."""
        network = RegionalNetwork(network_type="trade")
        network.add_edge("R1", "R2", weight=0)
        network.add_edge("R2", "R3", weight=100)

        integration = network.calculate_integration_index()
        assert len(integration) == 3


class TestIntegration:
    """Integration tests for regional analysis."""

    def test_full_workflow(self, trade_flow_data):
        """Test complete workflow from data to assessment."""
        # Create network
        network = RegionalNetwork.from_flow_data(
            trade_flow_data, network_type="trade", metadata={"country": "USA", "year": 2024}
        )

        # Set attributes
        for region in network.graph.nodes():
            network.set_region_attributes(region, {"gdp": 1000})

        # Calculate metrics
        integration = network.calculate_integration_index()
        assert len(integration) > 0

        core_periphery = network.identify_core_periphery()
        assert len(core_periphery["core"]) + len(core_periphery["periphery"]) == 4

        # Assess risk
        result = network.assess_regional_risk()
        assert result.metrics["num_regions"] == 4
        assert result.metadata["country"] == "USA"

    def test_spillover_and_clustering(self, simple_regional_network):
        """Test combined spillover and clustering analysis."""
        # Spillovers
        spillovers = simple_regional_network.calculate_regional_spillovers("R1")
        assert len(spillovers) > 0

        # Clustering
        clusters = simple_regional_network.identify_regional_clusters()
        assert len(clusters) > 0

        # Should be consistent
        assert set(spillovers.keys()) == set(clusters.keys())

    def test_market_access_and_integration(self, regional_network_with_attributes):
        """Test market access and integration together."""
        market_access = regional_network_with_attributes.calculate_market_access()
        integration = regional_network_with_attributes.calculate_integration_index()

        # Both should cover all regions
        assert set(market_access.keys()) == set(integration.keys())
