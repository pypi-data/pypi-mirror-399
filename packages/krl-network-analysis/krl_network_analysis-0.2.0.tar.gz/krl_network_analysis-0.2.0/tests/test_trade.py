"""
Tests for international trade network functionality.

Tests cover:
- Network construction from trade data
- Trade balance calculation
- Trade openness
- Revealed Comparative Advantage (RCA)
- Export similarity
- Trade bloc identification
- Trade diversification
- Network evolution analysis
- Comprehensive trade assessment
"""

import numpy as np
import pandas as pd
import pytest

from krl_network.core.exceptions import DataError
from krl_network.networks.trade import TradeNetwork


class TestTradeNetworkCreation:
    """Test trade network creation."""

    def test_from_trade_data_basic(self):
        """Test basic trade data import."""
        df = pd.DataFrame(
            {
                "exporter": ["USA", "USA", "CHN"],
                "importer": ["CHN", "MEX", "USA"],
                "value": [100, 50, 80],
            }
        )

        network = TradeNetwork.from_trade_data(df)

        assert network.graph.number_of_nodes() == 3
        assert network.graph.number_of_edges() == 3
        assert network.graph["USA"]["CHN"]["weight"] == 100

    def test_from_trade_data_aggregate_products(self):
        """Test aggregation across products."""
        df = pd.DataFrame(
            {
                "exporter": ["USA", "USA"],
                "importer": ["CHN", "CHN"],
                "value": [50, 50],
                "product": ["wheat", "corn"],
            }
        )

        network = TradeNetwork.from_trade_data(df, product_col="product", aggregate_products=True)

        # Should aggregate both products into single edge
        assert network.graph["USA"]["CHN"]["weight"] == 100

    def test_from_trade_data_keep_products(self):
        """Test keeping products separate."""
        df = pd.DataFrame(
            {
                "exporter": ["USA", "USA"],
                "importer": ["CHN", "CHN"],
                "value": [50, 50],
                "product": ["wheat", "corn"],
            }
        )

        network = TradeNetwork.from_trade_data(df, product_col="product", aggregate_products=False)

        # Should have product as edge attribute
        edges = list(network.graph.edges(data=True))
        assert any(e[2].get("product") == "wheat" for e in edges)

    def test_from_trade_data_with_year(self):
        """Test filtering by year."""
        df = pd.DataFrame(
            {
                "exporter": ["USA", "USA"],
                "importer": ["CHN", "CHN"],
                "value": [50, 100],
                "year": [2019, 2020],
            }
        )

        network = TradeNetwork.from_trade_data(df, year_col="year")

        # Should use latest year (2020)
        assert network.trade_year == 2020
        assert network.graph["USA"]["CHN"]["weight"] == 100

    def test_from_dataframe(self):
        """Test generic DataFrame construction."""
        df = pd.DataFrame({"from": ["USA", "CHN"], "to": ["CHN", "USA"], "trade_value": [100, 80]})

        network = TradeNetwork()
        network.from_dataframe(df, source_col="from", target_col="to", weight_col="trade_value")

        assert network.graph["USA"]["CHN"]["weight"] == 100
        assert network.graph["CHN"]["USA"]["weight"] == 80

    def test_from_trade_data_zero_values(self):
        """Test filtering zero trade values."""
        df = pd.DataFrame(
            {"exporter": ["USA", "CHN"], "importer": ["CHN", "USA"], "value": [100, 0]}
        )

        network = TradeNetwork.from_trade_data(df)

        # Should only include non-zero trade
        assert network.graph.number_of_edges() == 1
        assert network.graph.has_edge("USA", "CHN")
        assert not network.graph.has_edge("CHN", "USA")

    def test_from_trade_data_missing_column(self):
        """Test error handling for missing columns."""
        df = pd.DataFrame({"wrong_name": ["USA"], "importer": ["CHN"], "value": [100]})

        with pytest.raises(DataError):
            TradeNetwork.from_trade_data(df, exporter_col="exporter")  # Column doesn't exist


class TestTradeBalance:
    """Test trade balance calculation."""

    def test_calculate_trade_balance_basic(self):
        """Test basic trade balance."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)  # USA exports 100
        network.add_edge("CHN", "USA", weight=80)  # USA imports 80

        balance = network.calculate_trade_balance()

        # USA balance = 100 - 80 = 20 (surplus)
        assert balance["USA"] == 20
        # CHN balance = 80 - 100 = -20 (deficit)
        assert balance["CHN"] == -20

    def test_trade_balance_surplus_deficit(self):
        """Test identifying surplus and deficit countries."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.add_edge("CHN", "USA", weight=80)
        network.add_edge("MEX", "USA", weight=50)
        network.add_edge("USA", "MEX", weight=30)

        balance = network.calculate_trade_balance()

        # USA: exports (100 + 30) - imports (80 + 50) = 0
        assert balance["USA"] == 0
        # CHN: surplus
        assert balance["CHN"] < 0
        # MEX: surplus
        assert balance["MEX"] > 0

    def test_trade_balance_no_trade(self):
        """Test balance for country with no trade."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.graph.add_node("MEX")  # No edges

        balance = network.calculate_trade_balance()

        assert balance["MEX"] == 0


class TestTradeOpenness:
    """Test trade openness calculation."""

    def test_calculate_trade_openness_with_gdp(self):
        """Test openness with GDP data."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.add_edge("CHN", "USA", weight=80)

        gdp = pd.Series({"USA": 1000, "CHN": 800})
        openness = network.calculate_trade_openness(gdp)

        # USA: (100 exports + 80 imports) / 1000 GDP = 0.18
        assert openness["USA"] == pytest.approx(0.18)
        # CHN: (80 exports + 100 imports) / 800 GDP = 0.225
        assert openness["CHN"] == pytest.approx(0.225)

    def test_trade_openness_without_gdp(self):
        """Test normalized openness without GDP."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.add_edge("CHN", "USA", weight=80)

        openness = network.calculate_trade_openness()

        # Should return normalized values (0-1)
        assert 0 <= openness["USA"] <= 1
        assert 0 <= openness["CHN"] <= 1

    def test_trade_openness_zero_gdp(self):
        """Test handling of zero GDP."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)

        gdp = pd.Series({"USA": 0, "CHN": 800})  # USA has zero GDP
        openness = network.calculate_trade_openness(gdp)

        # Should handle gracefully
        assert openness["USA"] == 0


class TestRevealedComparativeAdvantage:
    """Test RCA calculation."""

    def test_calculate_rca_basic(self):
        """Test basic RCA calculation."""
        product_data = pd.DataFrame(
            {
                "country": ["USA", "USA", "CHN", "CHN"],
                "product": ["wheat", "electronics", "wheat", "electronics"],
                "exports": [100, 50, 20, 200],
            }
        )

        network = TradeNetwork()
        rca = network.calculate_revealed_comparative_advantage(product_data)

        # CHN should have high RCA in electronics
        chn_electronics = rca[(rca["country"] == "CHN") & (rca["product"] == "electronics")]
        assert chn_electronics["rca"].values[0] > 1
        assert chn_electronics["has_advantage"].values[0] == True

    def test_rca_interpretation(self):
        """Test RCA > 1 indicates comparative advantage."""
        product_data = pd.DataFrame(
            {"country": ["USA", "CHN"], "product": ["wheat", "wheat"], "exports": [100, 50]}
        )

        network = TradeNetwork()
        rca = network.calculate_revealed_comparative_advantage(product_data)

        # Both should have same RCA (only product)
        usa_rca = rca[rca["country"] == "USA"]["rca"].values[0]
        chn_rca = rca[rca["country"] == "CHN"]["rca"].values[0]

        assert usa_rca == pytest.approx(chn_rca)

    def test_rca_multiple_products(self):
        """Test RCA with multiple countries and products."""
        product_data = pd.DataFrame(
            {
                "country": ["A", "A", "B", "B", "C", "C"],
                "product": ["X", "Y", "X", "Y", "X", "Y"],
                "exports": [50, 50, 30, 70, 80, 20],
            }
        )

        network = TradeNetwork()
        rca = network.calculate_revealed_comparative_advantage(product_data)

        # Should have 6 rows (3 countries × 2 products)
        assert len(rca) == 6
        assert "rca" in rca.columns
        assert "has_advantage" in rca.columns


class TestExportSimilarity:
    """Test export similarity calculation."""

    def test_calculate_export_similarity_cosine(self):
        """Test cosine similarity."""
        product_data = pd.DataFrame(
            {
                "country": ["USA", "USA", "CHN", "CHN"],
                "product": ["wheat", "electronics", "wheat", "electronics"],
                "exports": [100, 50, 100, 50],
            }
        )

        network = TradeNetwork()
        similarity = network.calculate_export_similarity(product_data, method="cosine")

        # USA and CHN have identical export structure
        assert similarity.loc["USA", "CHN"] == pytest.approx(1.0)
        # Diagonal should be 1
        assert similarity.loc["USA", "USA"] == pytest.approx(1.0)

    def test_export_similarity_correlation(self):
        """Test correlation-based similarity."""
        product_data = pd.DataFrame(
            {
                "country": ["USA", "USA", "CHN", "CHN"],
                "product": ["wheat", "electronics", "wheat", "electronics"],
                "exports": [100, 50, 80, 40],
            }
        )

        network = TradeNetwork()
        similarity = network.calculate_export_similarity(product_data, method="correlation")

        # Should have high correlation (proportional exports)
        assert similarity.loc["USA", "CHN"] > 0.95

    def test_export_similarity_dissimilar(self):
        """Test similarity for dissimilar export structures."""
        product_data = pd.DataFrame(
            {
                "country": ["USA", "USA", "CHN", "CHN"],
                "product": ["wheat", "electronics", "wheat", "electronics"],
                "exports": [100, 0, 0, 100],
            }
        )

        network = TradeNetwork()
        similarity = network.calculate_export_similarity(product_data)

        # USA and CHN specialize in different products
        assert similarity.loc["USA", "CHN"] < 0.5

    def test_export_similarity_symmetric(self):
        """Test that similarity matrix is symmetric."""
        product_data = pd.DataFrame(
            {
                "country": ["A", "A", "B", "B"],
                "product": ["X", "Y", "X", "Y"],
                "exports": [50, 50, 30, 70],
            }
        )

        network = TradeNetwork()
        similarity = network.calculate_export_similarity(product_data)

        assert similarity.loc["A", "B"] == pytest.approx(similarity.loc["B", "A"])


class TestTradeBlocs:
    """Test trade bloc identification."""

    def test_identify_trade_blocs_modularity(self):
        """Test modularity-based bloc identification."""
        network = TradeNetwork()
        # Create two clusters
        network.add_edge("USA", "CAN", weight=100)
        network.add_edge("CAN", "USA", weight=100)
        network.add_edge("USA", "MEX", weight=100)
        network.add_edge("MEX", "USA", weight=100)

        network.add_edge("CHN", "JPN", weight=100)
        network.add_edge("JPN", "CHN", weight=100)
        network.add_edge("CHN", "KOR", weight=100)
        network.add_edge("KOR", "CHN", weight=100)

        blocs = network.identify_trade_blocs(method="modularity")

        # Should identify at least 2 blocs
        assert len(set(blocs.values())) >= 2
        # USA, CAN, MEX should be in same bloc
        assert blocs["USA"] == blocs["CAN"] == blocs["MEX"]
        # CHN, JPN, KOR should be in same bloc
        assert blocs["CHN"] == blocs["JPN"] == blocs["KOR"]

    def test_identify_trade_blocs_threshold(self):
        """Test threshold-based bloc identification."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.add_edge("CHN", "USA", weight=100)
        network.add_edge("MEX", "USA", weight=10)  # Weak link

        blocs = network.identify_trade_blocs(method="threshold", threshold=50)

        # USA and CHN should be connected
        assert blocs["USA"] == blocs["CHN"]
        # MEX might be separate (weak link)
        assert "MEX" in blocs

    def test_trade_blocs_single_country(self):
        """Test bloc identification with isolated country."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.graph.add_node("MEX")  # Isolated

        blocs = network.identify_trade_blocs()

        # Should handle isolated nodes
        assert "MEX" in blocs


class TestTradeDiversification:
    """Test trade diversification measures."""

    def test_calculate_diversification_hhi(self):
        """Test HHI diversification."""
        network = TradeNetwork()
        # USA: concentrated (all to CHN)
        network.add_edge("USA", "CHN", weight=100)
        # MEX: diversified (split between USA and CHN)
        network.add_edge("MEX", "USA", weight=50)
        network.add_edge("MEX", "CHN", weight=50)

        diversification = network.calculate_trade_diversification(measure="hhi")

        # USA HHI = 1.0 (fully concentrated)
        assert diversification["USA"] == pytest.approx(1.0)
        # MEX HHI = 0.5 (50/50 split)
        assert diversification["MEX"] == pytest.approx(0.5)

    def test_diversification_entropy(self):
        """Test entropy-based diversification."""
        network = TradeNetwork()
        # Concentrated: all to one partner
        network.add_edge("USA", "CHN", weight=100)
        # Diversified: three equal partners
        network.add_edge("MEX", "USA", weight=33.33)
        network.add_edge("MEX", "CHN", weight=33.33)
        network.add_edge("MEX", "CAN", weight=33.34)

        diversification = network.calculate_trade_diversification(measure="entropy")

        # MEX should have higher entropy (more diversified)
        assert diversification["MEX"] > diversification["USA"]

    def test_diversification_count(self):
        """Test partner count diversification."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.add_edge("USA", "MEX", weight=50)
        network.add_edge("USA", "CAN", weight=30)

        network.add_edge("CHN", "USA", weight=100)

        diversification = network.calculate_trade_diversification(measure="count")

        # USA has 3 partners, CHN has 1
        assert diversification["USA"] == 3
        assert diversification["CHN"] == 1

    def test_diversification_no_exports(self):
        """Test diversification for country with no exports."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.graph.add_node("MEX")  # No exports

        diversification = network.calculate_trade_diversification()

        assert diversification["MEX"] == 0


class TestTradeEvolution:
    """Test trade network evolution analysis."""

    def test_analyze_trade_evolution_growth(self):
        """Test trade growth calculation."""
        # Previous network
        previous = TradeNetwork()
        previous.add_edge("USA", "CHN", weight=100)
        previous.add_edge("USA", "MEX", weight=50)

        # Current network (grown)
        current = TradeNetwork()
        current.add_edge("USA", "CHN", weight=150)  # 50% growth
        current.add_edge("USA", "MEX", weight=50)  # No growth

        evolution = current.analyze_trade_evolution(previous, metrics=["growth"])

        # USA exports grew from 150 to 200
        assert evolution["growth"]["USA"] == pytest.approx((200 - 150) / 150)

    def test_trade_evolution_stability(self):
        """Test partner stability (Jaccard similarity)."""
        # Previous network
        previous = TradeNetwork()
        previous.add_edge("USA", "CHN", weight=100)
        previous.add_edge("USA", "MEX", weight=50)

        # Current network (lost MEX, added CAN)
        current = TradeNetwork()
        current.add_edge("USA", "CHN", weight=150)
        current.add_edge("USA", "CAN", weight=50)

        evolution = current.analyze_trade_evolution(previous, metrics=["stability"])

        # USA kept 1 partner (CHN), union is 3 (CHN, MEX, CAN)
        # Stability = 1/3
        assert evolution["stability"]["USA"] == pytest.approx(1 / 3)

    def test_trade_evolution_new_partners(self):
        """Test new trading partner identification."""
        # Previous network
        previous = TradeNetwork()
        previous.add_edge("USA", "CHN", weight=100)

        # Current network (added MEX and CAN)
        current = TradeNetwork()
        current.add_edge("USA", "CHN", weight=150)
        current.add_edge("USA", "MEX", weight=50)
        current.add_edge("USA", "CAN", weight=30)

        evolution = current.analyze_trade_evolution(previous, metrics=["new_partners"])

        # USA gained 2 new partners (MEX, CAN)
        assert evolution["new_partners"]["USA"] == 2

    def test_trade_evolution_new_country(self):
        """Test evolution for newly entering country."""
        previous = TradeNetwork()
        previous.add_edge("USA", "CHN", weight=100)

        current = TradeNetwork()
        current.add_edge("USA", "CHN", weight=100)
        current.add_edge("MEX", "USA", weight=50)  # MEX is new

        evolution = current.analyze_trade_evolution(previous, metrics=["growth", "stability"])

        # MEX is new: 100% growth, 0 stability
        assert evolution["growth"]["MEX"] == 1.0
        assert evolution["stability"]["MEX"] == 0.0


class TestTradeAssessment:
    """Test comprehensive trade structure assessment."""

    def test_assess_trade_structure_basic(self):
        """Test basic trade assessment."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.add_edge("CHN", "USA", weight=80)
        network.add_edge("MEX", "USA", weight=50)

        result = network.assess_trade_structure()

        assert result.metrics["num_countries"] == 3
        assert result.metrics["num_trade_flows"] == 3

    def test_assess_trade_structure_with_balance(self):
        """Test assessment with trade balance."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.add_edge("CHN", "USA", weight=80)

        result = network.assess_trade_structure(include_balance=True)

        assert "trade_balance" in result.metadata
        assert "num_surplus_countries" in result.metrics

    def test_assess_trade_structure_with_blocs(self):
        """Test assessment with trade blocs."""
        network = TradeNetwork()
        network.add_edge("USA", "CAN", weight=100)
        network.add_edge("CAN", "USA", weight=100)
        network.add_edge("CHN", "JPN", weight=100)
        network.add_edge("JPN", "CHN", weight=100)

        result = network.assess_trade_structure(include_blocs=True)

        assert "num_trade_blocs" in result.metrics
        assert "trade_blocs" in result.metadata

    def test_assess_trade_structure_with_diversification(self):
        """Test assessment with diversification metrics."""
        network = TradeNetwork()
        network.add_edge("USA", "CHN", weight=100)
        network.add_edge("USA", "MEX", weight=50)

        result = network.assess_trade_structure(include_diversification=True)

        assert "avg_hhi" in result.metrics
        assert "trade_diversification" in result.metadata

    def test_assess_trade_structure_with_year(self):
        """Test that trade year is included."""
        df = pd.DataFrame(
            {"exporter": ["USA"], "importer": ["CHN"], "value": [100], "year": [2020]}
        )

        network = TradeNetwork.from_trade_data(df, year_col="year")
        result = network.assess_trade_structure()

        assert result.metrics["trade_year"] == 2020


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_network(self):
        """Test operations on empty network."""
        network = TradeNetwork()

        balance = network.calculate_trade_balance()
        assert len(balance) == 0

        result = network.assess_trade_structure()
        assert result.metrics["num_countries"] == 0

    def test_single_country(self):
        """Test with single isolated country."""
        network = TradeNetwork()
        network.graph.add_node("USA")

        balance = network.calculate_trade_balance()
        assert balance["USA"] == 0

        openness = network.calculate_trade_openness()
        assert openness["USA"] == 0

    def test_self_trade(self):
        """Test handling of self-trade (re-exports)."""
        network = TradeNetwork()
        network.add_edge("USA", "USA", weight=50)  # Self-loop

        balance = network.calculate_trade_balance()
        # Self-trade cancels out
        assert balance["USA"] == 0


class TestIntegration:
    """Test end-to-end trade workflows."""

    def test_full_trade_analysis_workflow(self):
        """Test complete trade analysis pipeline."""
        # Create bilateral trade data
        trade_data = pd.DataFrame(
            {
                "exporter": ["USA", "USA", "CHN", "CHN", "MEX", "MEX"],
                "importer": ["CHN", "MEX", "USA", "MEX", "USA", "CHN"],
                "value": [100, 50, 80, 60, 40, 30],
                "year": [2020, 2020, 2020, 2020, 2020, 2020],
            }
        )

        # Build network
        network = TradeNetwork.from_trade_data(trade_data, year_col="year")

        # Calculate metrics
        balance = network.calculate_trade_balance()
        openness = network.calculate_trade_openness()
        diversification = network.calculate_trade_diversification()
        blocs = network.identify_trade_blocs()

        # Comprehensive assessment
        result = network.assess_trade_structure(
            include_balance=True, include_blocs=True, include_diversification=True
        )

        # Verify results
        assert len(balance) == 3
        assert len(openness) == 3
        assert len(diversification) == 3
        assert result.metrics["num_countries"] == 3
        assert result.metrics["trade_year"] == 2020

    def test_comparative_advantage_workflow(self):
        """Test RCA and export similarity workflow."""
        # Product-level trade data
        product_data = pd.DataFrame(
            {
                "country": ["USA", "USA", "CHN", "CHN", "MEX", "MEX"],
                "product": ["wheat", "electronics", "wheat", "electronics", "wheat", "electronics"],
                "exports": [100, 200, 50, 300, 80, 50],
            }
        )

        network = TradeNetwork()

        # Calculate RCA
        rca = network.calculate_revealed_comparative_advantage(product_data)

        # Calculate export similarity
        similarity = network.calculate_export_similarity(product_data)

        # Verify results
        assert len(rca) == 6  # 3 countries × 2 products
        assert similarity.shape == (3, 3)  # 3×3 matrix

        # CHN should have advantage in electronics
        chn_elec_rca = rca[(rca["country"] == "CHN") & (rca["product"] == "electronics")][
            "rca"
        ].values[0]
        assert chn_elec_rca > 1

    def test_temporal_analysis_workflow(self):
        """Test trade evolution over time."""
        # Create two time periods
        trade_2019 = pd.DataFrame(
            {
                "exporter": ["USA", "USA", "CHN"],
                "importer": ["CHN", "MEX", "USA"],
                "value": [100, 50, 80],
                "year": [2019, 2019, 2019],
            }
        )

        trade_2020 = pd.DataFrame(
            {
                "exporter": ["USA", "USA", "CHN", "MEX"],
                "importer": ["CHN", "CAN", "USA", "USA"],
                "value": [120, 40, 90, 30],
                "year": [2020, 2020, 2020, 2020],
            }
        )

        # Build networks
        network_2019 = TradeNetwork.from_trade_data(trade_2019, year_col="year")
        network_2020 = TradeNetwork.from_trade_data(trade_2020, year_col="year")

        # Analyze evolution
        evolution = network_2020.analyze_trade_evolution(
            network_2019, metrics=["growth", "stability", "new_partners"]
        )

        # Verify results
        assert "growth" in evolution
        assert "stability" in evolution
        assert "new_partners" in evolution

        # USA should have positive growth
        assert evolution["growth"]["USA"] > 0
        # USA lost MEX, added CAN
        assert evolution["new_partners"]["USA"] == 1
