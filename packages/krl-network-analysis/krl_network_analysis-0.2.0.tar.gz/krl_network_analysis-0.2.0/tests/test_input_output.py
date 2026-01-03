"""
Tests for input-output network functionality.

Tests cover:
- Network construction from I-O tables
- Technical coefficient calculation
- Leontief inverse computation
- Output multipliers
- Backward and forward linkages
- Key sector identification
- Employment and value-added multipliers
- Production chain tracing
- Import dependency
- Comprehensive I-O assessment
"""

import numpy as np
import pandas as pd
import pytest

from krl_network.core.exceptions import ComputationError, DataError
from krl_network.networks.input_output import InputOutputNetwork


class TestIONetworkCreation:
    """Test input-output network creation."""

    def test_from_io_table_basic(self):
        """Test basic I-O table import."""
        # Create simple I-O table (3 sectors)
        io_table = pd.DataFrame(
            {
                "sector": ["Agriculture", "Manufacturing", "Services"],
                "Agriculture": [50, 30, 10],
                "Manufacturing": [20, 100, 30],
                "Services": [10, 20, 60],
            }
        )

        network = InputOutputNetwork.from_io_table(
            io_table, sector_row="sector", sector_col=["Agriculture", "Manufacturing", "Services"]
        )

        assert network.graph.number_of_nodes() == 3
        assert "Agriculture" in network.graph.nodes()
        assert "Manufacturing" in network.graph.nodes()
        assert "Services" in network.graph.nodes()

    def test_from_io_table_with_total_output(self):
        """Test I-O table import with total output."""
        io_table = pd.DataFrame({"sector": ["A", "B"], "A": [10, 5], "B": [5, 10]})
        total_output = pd.Series({"A": 100, "B": 100})

        network = InputOutputNetwork.from_io_table(
            io_table, sector_row="sector", sector_col=["A", "B"], total_output=total_output
        )

        assert network.total_output is not None
        assert network.total_output["A"] == 100
        assert network.total_output["B"] == 100

    def test_from_io_table_with_metadata(self):
        """Test I-O table import with metadata."""
        io_table = pd.DataFrame({"sector": ["A"], "A": [10]})

        network = InputOutputNetwork.from_io_table(
            io_table,
            sector_row="sector",
            sector_col=["A"],
            metadata={"year": 2020, "country": "USA"},
        )

        assert network.metadata["year"] == 2020
        assert network.metadata["country"] == "USA"

    def test_from_dataframe(self):
        """Test generic DataFrame construction."""
        df = pd.DataFrame(
            {
                "from_sector": ["A", "A", "B"],
                "to_sector": ["B", "C", "C"],
                "intermediate_input": [10, 5, 15],
            }
        )

        network = InputOutputNetwork()
        network.from_dataframe(
            df, source_col="from_sector", target_col="to_sector", weight_col="intermediate_input"
        )

        assert network.graph.number_of_nodes() == 3
        assert network.graph.number_of_edges() == 3
        assert network.graph["A"]["B"]["weight"] == 10

    def test_from_io_table_missing_column(self):
        """Test error handling for missing columns."""
        io_table = pd.DataFrame({"wrong_name": ["A"], "A": [10]})

        with pytest.raises(DataError):
            InputOutputNetwork.from_io_table(
                io_table, sector_row="sector", sector_col=["A"]  # Column doesn't exist
            )

    def test_empty_io_table(self):
        """Test handling of empty I-O table."""
        io_table = pd.DataFrame({"sector": []})

        network = InputOutputNetwork.from_io_table(io_table, sector_row="sector", sector_col=[])

        assert network.graph.number_of_nodes() == 0

    def test_from_io_table_zero_flows(self):
        """Test I-O table with zero flows."""
        io_table = pd.DataFrame({"sector": ["A", "B"], "A": [0, 0], "B": [0, 0]})

        network = InputOutputNetwork.from_io_table(
            io_table, sector_row="sector", sector_col=["A", "B"]
        )

        # Should create nodes but no edges
        assert network.graph.number_of_nodes() == 2
        assert network.graph.number_of_edges() == 0


class TestTechnicalCoefficients:
    """Test technical coefficient calculation."""

    def test_calculate_technical_coefficients_basic(self):
        """Test basic A matrix calculation."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=20)
        network.add_edge("A", "C", weight=10)
        network.add_edge("B", "C", weight=30)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100})

        A = network.calculate_technical_coefficients(total_output)

        assert A.loc["A", "B"] == 0.2  # 20 / 100
        assert A.loc["A", "C"] == 0.1  # 10 / 100
        assert A.loc["B", "C"] == 0.3  # 30 / 100

    def test_technical_coefficients_zero_output(self):
        """Test handling of zero total output."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)

        total_output = pd.Series({"A": 100, "B": 0})  # B has zero output

        A = network.calculate_technical_coefficients(total_output)

        # Coefficient should be 0 when output is 0
        assert A.loc["A", "B"] == 0.0

    def test_technical_coefficients_stored(self):
        """Test that coefficients are stored in network."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=20)

        total_output = pd.Series({"A": 100, "B": 100})
        A = network.calculate_technical_coefficients(total_output)

        assert network.technical_coefficients is not None
        pd.testing.assert_frame_equal(network.technical_coefficients, A)

    def test_technical_coefficients_self_loop(self):
        """Test coefficient for self-loop (same sector)."""
        network = InputOutputNetwork()
        network.add_edge("A", "A", weight=10)

        total_output = pd.Series({"A": 100})
        A = network.calculate_technical_coefficients(total_output)

        assert A.loc["A", "A"] == 0.1


class TestLeontiefInverse:
    """Test Leontief inverse computation."""

    def test_calculate_leontief_inverse_basic(self):
        """Test basic (I-A)^-1 calculation."""
        A = pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.1]}, index=["A", "B"])

        network = InputOutputNetwork()
        L = network.calculate_leontief_inverse(A)

        # Verify it's a valid inverse
        I_minus_A = np.eye(2) - A.values
        product = np.dot(I_minus_A, L.values)

        # Product should be identity matrix
        np.testing.assert_array_almost_equal(product, np.eye(2), decimal=10)

    def test_leontief_inverse_stored(self):
        """Test that Leontief inverse is stored."""
        A = pd.DataFrame({"A": [0.1, 0.2], "B": [0.3, 0.1]}, index=["A", "B"])

        network = InputOutputNetwork()
        L = network.calculate_leontief_inverse(A)

        assert network.leontief_inverse is not None
        pd.testing.assert_frame_equal(network.leontief_inverse, L)

    def test_leontief_inverse_identity(self):
        """Test with A = 0 (identity case)."""
        A = pd.DataFrame({"A": [0, 0], "B": [0, 0]}, index=["A", "B"])

        network = InputOutputNetwork()
        L = network.calculate_leontief_inverse(A)

        # Should equal identity matrix
        np.testing.assert_array_almost_equal(L.values, np.eye(2))

    def test_leontief_inverse_singular_matrix(self):
        """Test error handling for singular matrix."""
        # Create singular matrix (determinant = 0)
        A = pd.DataFrame({"A": [0.5, 0.5], "B": [0.5, 0.5]}, index=["A", "B"])

        network = InputOutputNetwork()

        with pytest.raises(ComputationError):
            network.calculate_leontief_inverse(A)

    def test_leontief_inverse_three_sectors(self):
        """Test with 3x3 matrix."""
        A = pd.DataFrame(
            {"A": [0.1, 0.1, 0.1], "B": [0.1, 0.1, 0.1], "C": [0.1, 0.1, 0.1]},
            index=["A", "B", "C"],
        )

        network = InputOutputNetwork()
        L = network.calculate_leontief_inverse(A)

        assert L.shape == (3, 3)


class TestOutputMultipliers:
    """Test output multiplier calculation."""

    def test_calculate_output_multipliers_basic(self):
        """Test basic multiplier calculation."""
        L = pd.DataFrame({"A": [1.2, 0.3], "B": [0.4, 1.1]}, index=["A", "B"])

        network = InputOutputNetwork()
        multipliers = network.calculate_output_multipliers(L)

        # Multiplier = column sum
        assert multipliers["A"] == pytest.approx(1.5)  # 1.2 + 0.3
        assert multipliers["B"] == pytest.approx(1.5)  # 0.4 + 1.1

    def test_output_multipliers_interpretation(self):
        """Test that multipliers > 1."""
        # Leontief inverse should always have diagonal >= 1
        L = pd.DataFrame({"A": [1.5, 0.2], "B": [0.3, 1.4]}, index=["A", "B"])

        network = InputOutputNetwork()
        multipliers = network.calculate_output_multipliers(L)

        # All multipliers should be >= 1
        assert all(m >= 1.0 for m in multipliers.values())

    def test_output_multipliers_identity(self):
        """Test multipliers for identity matrix (no linkages)."""
        L = pd.DataFrame(np.eye(2), index=["A", "B"], columns=["A", "B"])

        network = InputOutputNetwork()
        multipliers = network.calculate_output_multipliers(L)

        # With no linkages, multipliers = 1
        assert multipliers["A"] == pytest.approx(1.0)
        assert multipliers["B"] == pytest.approx(1.0)


class TestLinkages:
    """Test backward and forward linkage analysis."""

    def test_calculate_backward_linkages(self):
        """Test backward linkage calculation."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)
        network.add_edge("C", "B", weight=20)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100})
        network.calculate_technical_coefficients(total_output)

        linkages = network.calculate_backward_linkages()

        # B purchases from A and C
        assert linkages["B"] > linkages["A"]
        assert linkages["B"] > linkages["C"]

    def test_calculate_forward_linkages(self):
        """Test forward linkage calculation."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)
        network.add_edge("A", "C", weight=20)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100})
        network.calculate_technical_coefficients(total_output)

        linkages = network.calculate_forward_linkages()

        # A sells to B and C
        assert linkages["A"] > linkages["B"]
        assert linkages["A"] > linkages["C"]

    def test_linkages_normalization(self):
        """Test that linkages are normalized (mean = 1)."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)
        network.add_edge("B", "C", weight=10)
        network.add_edge("C", "A", weight=10)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100})
        network.calculate_technical_coefficients(total_output)

        backward = network.calculate_backward_linkages()
        forward = network.calculate_forward_linkages()

        # Mean should be 1.0
        assert np.mean(list(backward.values())) == pytest.approx(1.0)
        assert np.mean(list(forward.values())) == pytest.approx(1.0)

    def test_linkages_no_technical_coefficients(self):
        """Test error when technical coefficients not calculated."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)

        with pytest.raises(ComputationError):
            network.calculate_backward_linkages()

        with pytest.raises(ComputationError):
            network.calculate_forward_linkages()


class TestKeySectors:
    """Test key sector identification."""

    def test_identify_key_sectors_basic(self):
        """Test basic key sector identification."""
        network = InputOutputNetwork()
        # Create a star network: B is central
        network.add_edge("A", "B", weight=10)
        network.add_edge("C", "B", weight=10)
        network.add_edge("B", "D", weight=10)
        network.add_edge("B", "E", weight=10)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100, "D": 100, "E": 100})
        network.calculate_technical_coefficients(total_output)

        sectors = network.identify_key_sectors(threshold=1.0)

        # B should be a key sector (high backward and forward)
        assert "B" in sectors["key_sectors"]

    def test_key_sectors_classification(self):
        """Test 4-way sector classification."""
        network = InputOutputNetwork()
        # A: High backward (purchases from B, C)
        network.add_edge("B", "A", weight=30)
        network.add_edge("C", "A", weight=30)
        # D: High forward (sells to B, C)
        network.add_edge("D", "B", weight=30)
        network.add_edge("D", "C", weight=30)
        # E: Weak linkage
        network.add_edge("E", "B", weight=5)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100, "D": 100, "E": 100})
        network.calculate_technical_coefficients(total_output)

        sectors = network.identify_key_sectors(threshold=1.0)

        # Check classifications exist
        assert "key_sectors" in sectors
        assert "backward_oriented" in sectors
        assert "forward_oriented" in sectors
        assert "weak_linkage" in sectors

    def test_key_sectors_with_linkages(self):
        """Test that linkages are included in result."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)
        network.add_edge("B", "C", weight=10)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100})
        network.calculate_technical_coefficients(total_output)

        sectors = network.identify_key_sectors(threshold=1.0)

        assert "backward_linkages" in sectors
        assert "forward_linkages" in sectors
        assert len(sectors["backward_linkages"]) == 3
        assert len(sectors["forward_linkages"]) == 3

    def test_key_sectors_threshold_effect(self):
        """Test effect of threshold on classification."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)
        network.add_edge("B", "C", weight=10)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100})
        network.calculate_technical_coefficients(total_output)

        # Higher threshold = fewer key sectors
        sectors_strict = network.identify_key_sectors(threshold=1.5)
        sectors_loose = network.identify_key_sectors(threshold=0.5)

        total_strict = len(sectors_strict["key_sectors"])
        total_loose = len(sectors_loose["key_sectors"])

        assert total_strict <= total_loose


class TestMultipliers:
    """Test employment and value-added multipliers."""

    def test_calculate_employment_multipliers(self):
        """Test employment multiplier calculation."""
        L = pd.DataFrame({"A": [1.2, 0.3], "B": [0.4, 1.1]}, index=["A", "B"])

        employment_coef = pd.Series({"A": 0.1, "B": 0.2})  # Jobs per unit output

        network = InputOutputNetwork()
        multipliers = network.calculate_employment_multipliers(employment_coef, L)

        # Multiplier = e' × L
        assert multipliers["A"] == pytest.approx(0.1 * 1.2 + 0.2 * 0.4)
        assert multipliers["B"] == pytest.approx(0.1 * 0.3 + 0.2 * 1.1)

    def test_calculate_value_added_multipliers(self):
        """Test value-added multiplier calculation."""
        L = pd.DataFrame({"A": [1.2, 0.3], "B": [0.4, 1.1]}, index=["A", "B"])

        va_coef = pd.Series({"A": 0.3, "B": 0.4})  # Value added per unit output

        network = InputOutputNetwork()
        multipliers = network.calculate_value_added_multipliers(va_coef, L)

        # Multiplier = v' × L
        assert multipliers["A"] == pytest.approx(0.3 * 1.2 + 0.4 * 0.4)
        assert multipliers["B"] == pytest.approx(0.3 * 0.3 + 0.4 * 1.1)

    def test_multipliers_missing_sector(self):
        """Test handling of missing sectors in coefficient vectors."""
        L = pd.DataFrame({"A": [1.2, 0.3], "B": [0.4, 1.1]}, index=["A", "B"])

        # Missing sector B
        employment_coef = pd.Series({"A": 0.1})

        network = InputOutputNetwork()
        multipliers = network.calculate_employment_multipliers(employment_coef, L)

        # Should handle gracefully (treat missing as 0)
        assert "A" in multipliers
        assert "B" in multipliers


class TestProductionChain:
    """Test production chain tracing."""

    def test_trace_production_chain_basic(self):
        """Test basic chain tracing."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=20)
        network.add_edge("B", "C", weight=15)
        network.add_edge("C", "D", weight=10)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100, "D": 100})
        network.calculate_technical_coefficients(total_output)

        chain = network.trace_production_chain("D", max_hops=3, min_share=0.05)

        # D's supply chain: tier 1 = C, tier 2 = B, tier 3 = A
        assert 1 in chain  # Tier 1 suppliers
        assert ("C", 0.1) in chain[1]  # C supplies 10% to D

    def test_trace_production_chain_min_share(self):
        """Test minimum share filtering."""
        network = InputOutputNetwork()
        network.add_edge("A", "C", weight=5)  # Small share
        network.add_edge("B", "C", weight=45)  # Large share

        total_output = pd.Series({"A": 100, "B": 100, "C": 100})
        network.calculate_technical_coefficients(total_output)

        # High threshold filters out A
        chain = network.trace_production_chain("C", max_hops=1, min_share=0.1)

        tier1_suppliers = [s for s, _ in chain.get(1, [])]
        assert "B" in tier1_suppliers
        assert "A" not in tier1_suppliers

    def test_trace_production_chain_max_hops(self):
        """Test max hops limit."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)
        network.add_edge("B", "C", weight=10)
        network.add_edge("C", "D", weight=10)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100, "D": 100})
        network.calculate_technical_coefficients(total_output)

        chain = network.trace_production_chain("D", max_hops=1, min_share=0.01)

        # Should only include tier 1
        assert 1 in chain
        assert 2 not in chain

    def test_trace_production_chain_no_suppliers(self):
        """Test sector with no suppliers."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)

        total_output = pd.Series({"A": 100, "B": 100})
        network.calculate_technical_coefficients(total_output)

        chain = network.trace_production_chain("A", max_hops=2, min_share=0.01)

        # A has no suppliers
        assert len(chain) == 0


class TestImportDependency:
    """Test import dependency calculation."""

    def test_calculate_import_dependency_basic(self):
        """Test basic import dependency."""
        L = pd.DataFrame({"A": [1.2, 0.3], "B": [0.4, 1.1]}, index=["A", "B"])

        import_shares = pd.Series({"A": 0.1, "B": 0.2})

        network = InputOutputNetwork()
        dependency = network.calculate_import_dependency(import_shares, L)

        # Total import content = m' × L
        assert dependency["A"] == pytest.approx(0.1 * 1.2 + 0.2 * 0.4)
        assert dependency["B"] == pytest.approx(0.1 * 0.3 + 0.2 * 1.1)

    def test_import_dependency_no_imports(self):
        """Test with no imports."""
        L = pd.DataFrame({"A": [1.2, 0.3], "B": [0.4, 1.1]}, index=["A", "B"])

        import_shares = pd.Series({"A": 0.0, "B": 0.0})

        network = InputOutputNetwork()
        dependency = network.calculate_import_dependency(import_shares, L)

        assert dependency["A"] == pytest.approx(0.0)
        assert dependency["B"] == pytest.approx(0.0)

    def test_import_dependency_interpretation(self):
        """Test that dependency reflects supply chain imports."""
        L = pd.DataFrame(
            {
                "A": [1.0, 0.0],  # Row A: producing for A uses inputs from [A, B]
                "B": [0.5, 1.0],  # Row B: producing for B uses inputs from [A, B]
            },
            index=["A", "B"],
        )  # Rows are output sectors, columns are input sectors

        import_shares = pd.Series({"A": 0.0, "B": 0.3})  # Only B imports

        network = InputOutputNetwork()
        dependency = network.calculate_import_dependency(import_shares, L)

        # A has indirect imports through B (A uses B as input, formula: L @ m)
        assert dependency["A"] > 0  # Indirect: L[A,B] × m[B] = 0.5 × 0.3 = 0.15
        assert dependency["B"] == pytest.approx(0.3)  # Direct: L[B,B] × m[B] = 1.0 × 0.3


class TestIOAssessment:
    """Test comprehensive I-O structure assessment."""

    def test_assess_io_structure_basic(self):
        """Test basic I-O assessment."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)
        network.add_edge("B", "C", weight=10)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100})
        network.calculate_technical_coefficients(total_output)
        network.calculate_leontief_inverse(network.technical_coefficients)

        result = network.assess_io_structure()

        assert result.metrics["num_sectors"] == 3
        assert "num_transactions" in result.metrics

    def test_assess_io_structure_with_multipliers(self):
        """Test assessment with multiplier calculations."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)

        total_output = pd.Series({"A": 100, "B": 100})
        network.calculate_technical_coefficients(total_output)
        network.calculate_leontief_inverse(network.technical_coefficients)

        result = network.assess_io_structure(include_multipliers=True)

        assert "avg_output_multiplier" in result.metrics
        assert "max_output_multiplier" in result.metrics

    def test_assess_io_structure_with_linkages(self):
        """Test assessment with linkage analysis."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)
        network.add_edge("C", "B", weight=10)
        network.add_edge("B", "D", weight=10)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100, "D": 100})
        network.calculate_technical_coefficients(total_output)

        result = network.assess_io_structure(include_linkages=True)

        assert "num_key_sectors" in result.metrics
        assert "key_sectors" in result.metadata


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_network(self):
        """Test operations on empty network."""
        network = InputOutputNetwork()

        result = network.assess_io_structure()
        assert result.metrics["num_sectors"] == 0

    def test_single_sector(self):
        """Test single-sector economy."""
        network = InputOutputNetwork()
        network.add_edge("A", "A", weight=10)  # Self-loop

        total_output = pd.Series({"A": 100})
        A = network.calculate_technical_coefficients(total_output)

        assert A.shape == (1, 1)
        assert A.loc["A", "A"] == 0.1

    def test_disconnected_sectors(self):
        """Test with disconnected sectors."""
        network = InputOutputNetwork()
        network.add_edge("A", "B", weight=10)
        network.add_edge("C", "D", weight=10)

        total_output = pd.Series({"A": 100, "B": 100, "C": 100, "D": 100})
        network.calculate_technical_coefficients(total_output)

        linkages = network.calculate_backward_linkages()

        # Should handle disconnected components
        assert len(linkages) == 4


class TestIntegration:
    """Test end-to-end I-O workflows."""

    def test_full_io_analysis_workflow(self):
        """Test complete I-O analysis pipeline."""
        # Create I-O table
        io_table = pd.DataFrame(
            {
                "sector": ["Ag", "Mfg", "Svc"],
                "Ag": [10, 20, 5],
                "Mfg": [15, 30, 10],
                "Svc": [5, 10, 20],
            }
        )
        total_output = pd.Series({"Ag": 100, "Mfg": 150, "Svc": 120})

        # Build network
        network = InputOutputNetwork.from_io_table(
            io_table,
            sector_row="sector",
            sector_col=["Ag", "Mfg", "Svc"],
            total_output=total_output,
        )

        # Calculate coefficients and inverse
        A = network.calculate_technical_coefficients(total_output)
        L = network.calculate_leontief_inverse(A)

        # Calculate multipliers and linkages
        multipliers = network.calculate_output_multipliers(L)
        backward = network.calculate_backward_linkages()
        forward = network.calculate_forward_linkages()
        sectors = network.identify_key_sectors()

        # Comprehensive assessment
        result = network.assess_io_structure(include_multipliers=True, include_linkages=True)

        # Verify results
        assert len(multipliers) == 3
        assert len(backward) == 3
        assert len(forward) == 3
        assert "key_sectors" in sectors
        assert result.metrics["num_sectors"] == 3

    def test_multiplier_consistency(self):
        """Test consistency between different multiplier calculations."""
        io_table = pd.DataFrame({"sector": ["A", "B"], "A": [5, 10], "B": [10, 5]})
        total_output = pd.Series({"A": 100, "B": 100})

        network = InputOutputNetwork.from_io_table(
            io_table, sector_row="sector", sector_col=["A", "B"], total_output=total_output
        )

        A = network.calculate_technical_coefficients(total_output)
        L = network.calculate_leontief_inverse(A)

        # Output multipliers from column sums
        output_mult = network.calculate_output_multipliers(L)

        # All multipliers should be >= 1
        assert all(m >= 1.0 for m in output_mult.values())

    def test_large_io_table(self):
        """Test with larger I-O table (10 sectors)."""
        n_sectors = 10
        sectors = [f"S{i}" for i in range(n_sectors)]

        # Create random I-O table
        np.random.seed(42)
        io_data = {"sector": sectors}
        for s in sectors:
            io_data[s] = np.random.rand(n_sectors) * 100

        io_table = pd.DataFrame(io_data)
        total_output = pd.Series({s: 1000 for s in sectors})

        network = InputOutputNetwork.from_io_table(
            io_table, sector_row="sector", sector_col=sectors, total_output=total_output
        )

        A = network.calculate_technical_coefficients(total_output)
        L = network.calculate_leontief_inverse(A)
        multipliers = network.calculate_output_multipliers(L)

        assert A.shape == (n_sectors, n_sectors)
        assert L.shape == (n_sectors, n_sectors)
        assert len(multipliers) == n_sectors
