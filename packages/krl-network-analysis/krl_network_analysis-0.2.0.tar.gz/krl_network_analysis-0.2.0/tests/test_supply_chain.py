"""
Tests for supply chain network analysis.

This module tests:
- SupplyChainNetwork creation from various data sources
- Critical supplier identification
- Bottleneck detection
- Redundancy analysis
- Shock propagation simulation
- Risk assessment
"""

import numpy as np
import pandas as pd
import pytest

from krl_network.core.base import NetworkConfig
from krl_network.core.exceptions import ComputationError, DataError, InvalidNetworkError
from krl_network.networks.supply_chain import SupplyChainNetwork


@pytest.fixture
def simple_supply_chain():
    """Create simple linear supply chain."""
    network = SupplyChainNetwork()
    # Linear chain: Raw -> Part -> Assembly -> Product
    network.add_edge("Raw Material", "Part Supplier", weight=100)
    network.add_edge("Part Supplier", "Assembly Plant", weight=80)
    network.add_edge("Assembly Plant", "End Product", weight=60)
    return network


@pytest.fixture
def complex_supply_chain():
    """Create complex multi-tier supply chain."""
    network = SupplyChainNetwork()

    # Tier 3 (raw materials)
    network.add_edge("Raw_A", "Component_1", weight=50)
    network.add_edge("Raw_B", "Component_1", weight=30)
    network.add_edge("Raw_C", "Component_2", weight=40)

    # Tier 2 (components)
    network.add_edge("Component_1", "Assembly_1", weight=60)
    network.add_edge("Component_2", "Assembly_1", weight=50)
    network.add_edge("Component_2", "Assembly_2", weight=45)

    # Tier 1 (assemblies)
    network.add_edge("Assembly_1", "Product_A", weight=70)
    network.add_edge("Assembly_2", "Product_B", weight=55)

    return network


@pytest.fixture
def shipment_data():
    """Create sample shipment data."""
    return pd.DataFrame(
        {
            "supplier": ["S1", "S2", "S3", "S1", "S2"],
            "buyer": ["M1", "M1", "M2", "M2", "M3"],
            "volume": [100, 150, 200, 120, 180],
            "lead_time": [5, 7, 10, 6, 8],
        }
    )


@pytest.fixture
def bom_data():
    """Create sample bill of materials data."""
    return pd.DataFrame(
        {
            "parent": ["Product_A", "Product_A", "Product_B", "SubAssy_1"],
            "component": ["SubAssy_1", "Part_1", "SubAssy_1", "Part_2"],
            "quantity": [2, 4, 1, 3],
        }
    )


class TestSupplyChainCreation:
    """Test supply chain network creation."""

    def test_default_initialization(self):
        """Test default initialization creates directed weighted network."""
        network = SupplyChainNetwork()
        assert network.config.directed is True
        assert network.config.weighted is True
        assert len(network.graph) == 0

    def test_custom_config(self):
        """Test initialization with custom config."""
        config = NetworkConfig(directed=True, weighted=True, self_loops=True)
        network = SupplyChainNetwork(config=config)
        assert network.config.self_loops is True

    def test_metadata(self):
        """Test metadata storage."""
        metadata = {"industry": "automotive", "year": 2024}
        network = SupplyChainNetwork(metadata=metadata)
        assert network.metadata["industry"] == "automotive"

    def test_from_shipment_data(self, shipment_data):
        """Test creation from shipment data."""
        network = SupplyChainNetwork.from_shipment_data(
            shipment_data, volume_col="volume", lead_time_col="lead_time"
        )

        assert network.graph.number_of_nodes() == 6  # S1, S2, S3, M1, M2, M3
        assert network.graph.number_of_edges() == 5
        assert network.graph["S1"]["M1"]["weight"] == 100
        assert ("S1", "M2") in network.lead_times

    def test_from_shipment_aggregation(self, shipment_data):
        """Test shipment data aggregation for duplicate edges."""
        network = SupplyChainNetwork.from_shipment_data(shipment_data, volume_col="volume")
        # S1 -> M1 appears once (100), S1 -> M2 appears once (120)
        assert network.graph["S1"]["M1"]["weight"] == 100
        assert network.graph["S1"]["M2"]["weight"] == 120

    def test_from_bom(self, bom_data):
        """Test creation from bill of materials."""
        network = SupplyChainNetwork.from_bom(bom_data, quantity_col="quantity")

        assert network.graph.number_of_nodes() == 5
        assert network.graph.number_of_edges() == 4
        assert network.graph["SubAssy_1"]["Product_A"]["weight"] == 2
        assert network.graph["Part_2"]["SubAssy_1"]["weight"] == 3

    def test_from_shipment_missing_columns(self):
        """Test error on missing required columns."""
        df = pd.DataFrame({"supplier": ["S1"], "missing": ["M1"]})
        with pytest.raises(DataError):
            SupplyChainNetwork.from_shipment_data(df)


class TestTierCalculation:
    """Test supply chain tier calculation."""

    def test_simple_chain_tiers(self, simple_supply_chain):
        """Test tier calculation for linear chain."""
        tiers = simple_supply_chain.calculate_tiers()

        assert tiers["End Product"] == 0  # Tier 0
        assert tiers["Assembly Plant"] == 1  # Tier 1
        assert tiers["Part Supplier"] == 2  # Tier 2
        assert tiers["Raw Material"] == 3  # Tier 3

    def test_complex_chain_tiers(self, complex_supply_chain):
        """Test tier calculation for multi-tier chain."""
        tiers = complex_supply_chain.calculate_tiers()

        # Products are tier 0
        assert tiers["Product_A"] == 0
        assert tiers["Product_B"] == 0

        # Assemblies are tier 1
        assert tiers["Assembly_1"] == 1
        assert tiers["Assembly_2"] == 1

        # Components are tier 2
        assert tiers["Component_1"] == 2
        assert tiers["Component_2"] == 2

        # Raw materials are tier 3
        assert tiers["Raw_A"] == 3

    def test_tiers_with_specified_end_products(self, complex_supply_chain):
        """Test tier calculation with specified end products."""
        tiers = complex_supply_chain.calculate_tiers(end_products=["Product_A"])

        # Only Product_A is tier 0
        assert tiers["Product_A"] == 0
        # Product_B not in tiers (not specified as end product)
        assert "Product_B" not in tiers

    def test_tiers_undirected_network_error(self):
        """Test error when calculating tiers on undirected network."""
        network = SupplyChainNetwork(config=NetworkConfig(directed=False))
        network.add_edge("A", "B")

        with pytest.raises(InvalidNetworkError):
            network.calculate_tiers()

    def test_tiers_no_end_products_error(self):
        """Test error when no end products found."""
        network = SupplyChainNetwork()
        # Create cycle - no nodes with out_degree=0
        network.add_edge("A", "B")
        network.add_edge("B", "A")

        with pytest.raises(ComputationError):
            network.calculate_tiers()


class TestCriticalSuppliers:
    """Test critical supplier identification."""

    def test_betweenness_method(self, complex_supply_chain):
        """Test critical suppliers using betweenness centrality."""
        critical = complex_supply_chain.identify_critical_suppliers(method="betweenness", top_k=5)

        assert len(critical) <= 5
        assert "node" in critical.columns
        assert "centrality" in critical.columns
        assert "rank" in critical.columns

    def test_tier_method(self, complex_supply_chain):
        """Test critical suppliers using tier-based method."""
        complex_supply_chain.calculate_tiers()
        critical = complex_supply_chain.identify_critical_suppliers(method="tier", top_k=5)

        assert len(critical) <= 5
        assert "tier" in critical.columns
        assert "criticality" in critical.columns
        # Tier 0 should have highest criticality
        assert critical.iloc[0]["criticality"] == 1.0

    def test_degree_method(self, simple_supply_chain):
        """Test critical suppliers using degree centrality."""
        critical = simple_supply_chain.identify_critical_suppliers(method="degree", top_k=3)

        assert len(critical) <= 3
        assert critical["rank"].tolist() == [1, 2, 3]


class TestBottleneckDetection:
    """Test bottleneck detection."""

    def test_detect_bottlenecks(self, complex_supply_chain):
        """Test bottleneck detection."""
        bottlenecks = complex_supply_chain.detect_bottlenecks(
            capacity_attr="weight", flow_fraction=0.5
        )

        assert "source" in bottlenecks.columns
        assert "target" in bottlenecks.columns
        assert "capacity" in bottlenecks.columns
        assert "utilization" in bottlenecks.columns

    def test_bottlenecks_sorted_by_utilization(self, complex_supply_chain):
        """Test bottlenecks are sorted by utilization."""
        bottlenecks = complex_supply_chain.detect_bottlenecks(flow_fraction=0.3)

        if len(bottlenecks) > 1:
            # Check descending order
            utilizations = bottlenecks["utilization"].tolist()
            assert utilizations == sorted(utilizations, reverse=True)

    def test_no_bottlenecks(self, simple_supply_chain):
        """Test when no bottlenecks found."""
        # Use very high threshold so no bottlenecks are detected
        bottlenecks = simple_supply_chain.detect_bottlenecks(flow_fraction=1.5)

        # Should return empty DataFrame with correct columns
        assert len(bottlenecks) == 0
        assert "source" in bottlenecks.columns


class TestRedundancyAnalysis:
    """Test redundancy analysis."""

    def test_redundancy_with_multiple_paths(self):
        """Test redundancy analysis with multiple paths."""
        network = SupplyChainNetwork()
        # Create network with 2 paths: A->B->D and A->C->D
        network.add_edge("A", "B")
        network.add_edge("B", "D")
        network.add_edge("A", "C")
        network.add_edge("C", "D")

        result = network.analyze_redundancy("A", "D", max_paths=5)

        assert result["num_paths"] == 2
        assert len(result["paths"]) == 2
        assert result["shortest_path_length"] == 2
        assert result["redundancy_score"] > 0

    def test_redundancy_single_path(self, simple_supply_chain):
        """Test redundancy with single path."""
        result = simple_supply_chain.analyze_redundancy("Raw Material", "End Product", max_paths=5)

        assert result["num_paths"] == 1
        assert result["shortest_path_length"] == 3
        assert result["redundancy_score"] < 0.3  # Low redundancy

    def test_redundancy_no_path(self, simple_supply_chain):
        """Test redundancy when no path exists."""
        simple_supply_chain.add_node("Isolated")
        result = simple_supply_chain.analyze_redundancy("Raw Material", "Isolated", max_paths=5)

        assert result["num_paths"] == 0
        assert result["redundancy_score"] == 0.0

    def test_redundancy_invalid_nodes(self, simple_supply_chain):
        """Test error with invalid nodes."""
        with pytest.raises(InvalidNetworkError):
            simple_supply_chain.analyze_redundancy("NonExistent", "End Product")


class TestDependencyScore:
    """Test dependency score calculation."""

    def test_dependency_linear_chain(self, simple_supply_chain):
        """Test dependency in linear chain."""
        # Calculate tiers first (optional but good practice)
        simple_supply_chain.calculate_tiers()

        # Raw Material supplies everything downstream
        raw_dep = simple_supply_chain.calculate_dependency_score("Raw Material")
        # End Product supplies nothing
        product_dep = simple_supply_chain.calculate_dependency_score("End Product")

        assert raw_dep > product_dep
        assert product_dep == 0.0

    def test_dependency_complex_chain(self, complex_supply_chain):
        """Test dependency in complex chain."""
        # Component_2 supplies to both Assembly_1 and Assembly_2
        comp2_dep = complex_supply_chain.calculate_dependency_score("Component_2")
        # Raw_A only supplies to Component_1
        raw_dep = complex_supply_chain.calculate_dependency_score("Raw_A")

        assert comp2_dep > raw_dep

    def test_dependency_direct_only(self, complex_supply_chain):
        """Test dependency with only direct successors."""
        direct_dep = complex_supply_chain.calculate_dependency_score(
            "Component_2", include_indirect=False
        )
        indirect_dep = complex_supply_chain.calculate_dependency_score(
            "Component_2", include_indirect=True
        )

        # Indirect should be >= direct (includes more nodes)
        assert indirect_dep >= direct_dep

    def test_dependency_invalid_node(self, simple_supply_chain):
        """Test dependency for non-existent node."""
        dep = simple_supply_chain.calculate_dependency_score("NonExistent")
        assert dep == 0.0


class TestShockSimulation:
    """Test supply shock simulation."""

    def test_shock_no_propagation(self, simple_supply_chain):
        """Test shock that doesn't propagate."""
        result = simple_supply_chain.simulate_supply_shock(
            disrupted_nodes=["End Product"], propagation_threshold=0.9  # High threshold
        )

        assert result["total_disrupted"] == 1
        assert result["num_waves"] == 1  # Only initial wave
        assert len(result["final_disrupted"]) == 1

    def test_shock_full_propagation(self, simple_supply_chain):
        """Test shock that propagates through chain."""
        result = simple_supply_chain.simulate_supply_shock(
            disrupted_nodes=["Raw Material"], propagation_threshold=0.5
        )

        # Should disrupt all downstream nodes
        assert result["total_disrupted"] == 4  # All nodes
        assert result["impact_fraction"] == 1.0
        assert result["num_waves"] >= 1

    def test_shock_partial_propagation(self, complex_supply_chain):
        """Test shock with partial propagation."""
        result = complex_supply_chain.simulate_supply_shock(
            disrupted_nodes=["Raw_A"], propagation_threshold=0.6
        )

        # Should disrupt Component_1 (loses 1 of 2 suppliers = 50%)
        # But Component_1 won't propagate (below 60% threshold)
        assert result["total_disrupted"] >= 1
        assert "Raw_A" in result["final_disrupted"]

    def test_shock_multiple_initial(self, complex_supply_chain):
        """Test shock with multiple initial disruptions."""
        result = complex_supply_chain.simulate_supply_shock(
            disrupted_nodes=["Raw_A", "Raw_B"], propagation_threshold=0.5
        )

        # Component_1 loses both suppliers, should fail
        assert result["total_disrupted"] >= 2
        assert result["impact_fraction"] > 0

    def test_shock_undirected_error(self):
        """Test error for undirected network."""
        network = SupplyChainNetwork(config=NetworkConfig(directed=False))
        network.add_edge("A", "B")

        with pytest.raises(InvalidNetworkError):
            network.simulate_supply_shock(["A"])


class TestRiskAssessment:
    """Test comprehensive risk assessment."""

    def test_risk_assessment_structure(self, complex_supply_chain):
        """Test risk assessment returns correct structure."""
        result = complex_supply_chain.assess_supply_chain_risk()

        assert "num_nodes" in result.metrics
        assert "num_edges" in result.metrics
        assert "resilience" in result.metrics
        assert "avg_degree" in result.metrics
        assert "max_tier" in result.metrics
        assert "num_bottlenecks" in result.metrics

    def test_risk_assessment_nodes(self, complex_supply_chain):
        """Test node-level risk metrics."""
        result = complex_supply_chain.assess_supply_chain_risk()

        assert result.nodes is not None
        assert "node" in result.nodes.columns
        assert "degree" in result.nodes.columns
        assert "risk_score" in result.nodes.columns
        assert "dependency_score" in result.nodes.columns

    def test_risk_assessment_metadata(self, complex_supply_chain):
        """Test risk assessment metadata."""
        result = complex_supply_chain.assess_supply_chain_risk()

        assert "critical_suppliers" in result.metadata
        assert "bottlenecks" in result.metadata
        assert isinstance(result.metadata["critical_suppliers"], list)

    def test_risk_assessment_empty_network(self):
        """Test risk assessment on empty network."""
        network = SupplyChainNetwork()
        result = network.assess_supply_chain_risk()

        assert result.metrics["num_nodes"] == 0
        assert result.metrics["resilience"] == 0.0


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_network(self):
        """Test operations on empty network."""
        network = SupplyChainNetwork()

        # Should handle gracefully
        result = network.assess_supply_chain_risk()
        assert result.metrics["num_nodes"] == 0

    def test_single_node(self):
        """Test operations on single node."""
        network = SupplyChainNetwork()
        network.add_node("OnlyNode")

        dep = network.calculate_dependency_score("OnlyNode")
        assert dep == 0.0

    def test_disconnected_components(self):
        """Test network with disconnected components."""
        network = SupplyChainNetwork()
        # Component 1
        network.add_edge("A", "B")
        # Component 2 (isolated)
        network.add_edge("C", "D")

        result = network.assess_supply_chain_risk()
        assert result.metrics["is_connected"] is False
        assert result.metrics["resilience"] < 1.0

    def test_self_loops(self):
        """Test handling of self-loops."""
        config = NetworkConfig(directed=True, weighted=True, self_loops=True)
        network = SupplyChainNetwork(config=config)
        network.add_edge("A", "A", weight=10)  # Self-loop
        network.add_edge("A", "B", weight=20)

        assert network.graph.number_of_edges() == 2


class TestIntegration:
    """Integration tests for supply chain analysis."""

    def test_full_workflow_from_shipment_data(self, shipment_data):
        """Test complete workflow from data to risk assessment."""
        # Create network
        network = SupplyChainNetwork.from_shipment_data(
            shipment_data,
            volume_col="volume",
            lead_time_col="lead_time",
            metadata={"source": "test_data", "year": 2024},
        )

        # Calculate tiers
        tiers = network.calculate_tiers()
        assert len(tiers) > 0

        # Identify critical suppliers
        critical = network.identify_critical_suppliers(method="betweenness", top_k=3)
        assert len(critical) > 0

        # Detect bottlenecks
        bottlenecks = network.detect_bottlenecks()
        assert "source" in bottlenecks.columns

        # Assess risk
        result = network.assess_supply_chain_risk()
        assert result.metrics["num_nodes"] == 6
        assert result.metadata["source"] == "test_data"

    def test_shock_analysis_workflow(self, complex_supply_chain):
        """Test shock analysis workflow."""
        # Identify critical suppliers
        critical = complex_supply_chain.identify_critical_suppliers(method="tier", top_k=3)

        # Simulate shock on most critical
        most_critical = critical.iloc[0]["node"]
        shock_result = complex_supply_chain.simulate_supply_shock(
            disrupted_nodes=[most_critical], propagation_threshold=0.5
        )

        assert shock_result["total_disrupted"] >= 1
        assert most_critical in shock_result["final_disrupted"]
