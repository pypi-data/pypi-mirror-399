"""
Unit tests for edge cases and error handling.
"""

import math

import pytest
from pyomo.environ import ConcreteModel, Constraint, Var

from pyomo_solver_analyzer.analyzer import ConstraintAnalyzer
from pyomo_solver_analyzer.introspection import ConstraintIntrospector
from pyomo_solver_analyzer.unfeasibility import UnfeasibilityDetector


class TestConstraintIntrospectorEdgeCases:
    """Test edge cases and error handling."""

    def test_nan_handling(self):
        """Test handling of NaN values."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x >= 0)

        # Don't set value - should get NaN
        introspector = ConstraintIntrospector(model)
        body_val = introspector.get_constraint_body_value(model.c)

        assert isinstance(body_val, float)

    def test_unbounded_constraints(self):
        """Test constraints without bounds."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x == 5)
        model.x.set_value(5)

        introspector = ConstraintIntrospector(model)
        lower, upper = introspector.get_constraint_bounds(model.c)

        assert lower == 0.0 or lower is not None
        assert upper == 0.0 or upper is not None

    def test_equality_constraint(self):
        """Test equality constraint handling."""
        model = ConcreteModel()
        model.x = Var()
        model.y = Var()
        model.c = Constraint(expr=model.x + model.y == 10)
        model.x.set_value(5)
        model.y.set_value(5)

        introspector = ConstraintIntrospector(model)
        slack = introspector.compute_slack(model.c)

        # Equality constraint should have slack near 0
        assert abs(slack) < 1e-5

    def test_slack_zero(self):
        """Test constraint with exactly zero slack."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x >= 5)
        model.x.set_value(5)

        introspector = ConstraintIntrospector(model)
        slack = introspector.compute_slack(model.c)

        assert abs(slack) < 1e-10

    def test_large_slack(self):
        """Test constraint with very large slack."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x >= 0)
        model.x.set_value(1000)

        introspector = ConstraintIntrospector(model)
        slack = introspector.compute_slack(model.c)

        assert slack >= 1000

    def test_ranged_constraint_normalization(self):
        """Test normalization for ranged (two-sided) constraints."""
        model = ConcreteModel()
        model.x = Var()
        # Ranged constraint: 5 <= x <= 15
        model.c = Constraint(expr=(5, model.x, 15))
        model.x.set_value(10)  # Exactly in the middle

        introspector = ConstraintIntrospector(model)
        normalized = introspector.compute_normalized_slack(model.c)

        # When in middle of range, slack should be 5 to either side
        # Normalized by the closer bound magnitude
        assert not math.isnan(normalized)
        assert normalized >= 0

    def test_negative_rhs_normalization(self):
        """Test normalization with negative RHS."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x >= -100)
        model.x.set_value(-50)

        introspector = ConstraintIntrospector(model)
        normalized = introspector.compute_normalized_slack(model.c)

        # Should handle negative RHS correctly
        assert not math.isnan(normalized)

    def test_zero_rhs_normalization(self):
        """Test normalization when RHS is zero."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x >= 0)
        model.x.set_value(5)

        introspector = ConstraintIntrospector(model)
        normalized = introspector.compute_normalized_slack(model.c)

        # When RHS is 0, should return absolute slack
        assert normalized == 5.0

    def test_invalid_model_type(self):
        """Test that invalid model type raises TypeError."""
        with pytest.raises(TypeError):
            ConstraintIntrospector("not a model")

    def test_large_coefficient_constraint(self):
        """Test constraint with very large coefficients."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=1e10 * model.x >= 1e10)
        model.x.set_value(2)

        introspector = ConstraintIntrospector(model)
        slack = introspector.compute_slack(model.c)

        assert slack >= 0

    def test_small_coefficient_constraint(self):
        """Test constraint with very small coefficients."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=1e-10 * model.x >= 1e-10)
        model.x.set_value(2)

        introspector = ConstraintIntrospector(model)
        slack = introspector.compute_slack(model.c)

        assert not math.isnan(slack)


class TestConstraintAnalyzerEdgeCases:
    """Test edge cases for constraint analyzer."""

    def test_empty_model(self):
        """Test analyzer with model containing no constraints."""
        model = ConcreteModel()
        model.x = Var()

        analyzer = ConstraintAnalyzer(model)
        analyses = analyzer.analyze_all_constraints()

        assert analyses == []

    def test_single_constraint(self):
        """Test analyzer with single constraint."""
        model = ConcreteModel()
        model.x = Var(bounds=(0, 10))
        model.c = Constraint(expr=model.x >= 5)
        model.x.set_value(7)

        analyzer = ConstraintAnalyzer(model)
        analyses = analyzer.analyze_all_constraints()

        assert len(analyses) == 1

    def test_dual_value_handling(self):
        """Test handling of missing dual values."""
        model = ConcreteModel()
        model.x = Var(bounds=(0, 10))
        model.c = Constraint(expr=model.x >= 5)
        model.x.set_value(7)

        # No dual suffix defined
        analyzer = ConstraintAnalyzer(model)
        analysis = analyzer.analyze_constraint(model.c)

        assert analysis.dual is None

    def test_invalid_model_initialization(self):
        """Test that invalid model type raises TypeError."""
        with pytest.raises(TypeError):
            ConstraintAnalyzer("not a model")

    def test_negative_tolerance_initialization(self):
        """Test that negative tolerance raises ValueError."""
        model = ConcreteModel()
        model.x = Var()

        with pytest.raises(ValueError):
            ConstraintAnalyzer(model, tolerance=-0.01)

    def test_tightness_score_nan_handling(self):
        """Test that NaN slack values result in zero tightness."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x >= 0)
        # Don't set value - will result in NaN slack

        analyzer = ConstraintAnalyzer(model)
        analysis = analyzer.analyze_constraint(model.c)

        # NaN slack should result in low tightness score
        assert 0 <= analysis.tightness_score <= 1

    def test_nearly_binding_threshold(self):
        """Test nearly binding constraint identification."""
        model = ConcreteModel()
        model.x = Var()
        model.c1 = Constraint(expr=model.x >= 5)
        model.x.set_value(5.005)

        analyzer = ConstraintAnalyzer(model)
        nearly_binding = analyzer.get_nearly_binding_constraints()

        # With threshold 0.01, constraint should be identified as nearly binding
        assert len(nearly_binding) >= 1

    def test_summary_statistics_empty_model(self):
        """Test summary statistics for empty model."""
        model = ConcreteModel()
        model.x = Var()

        analyzer = ConstraintAnalyzer(model)
        stats = analyzer.summary_statistics()

        assert stats["total_constraints"] == 0
        assert stats["binding_constraints"] == 0
        assert stats["avg_tightness_score"] == 0.0


class TestUnfeasibilityDetectorEdgeCases:
    """Test edge cases for unfeasibility detector."""

    def test_marginally_feasible(self):
        """Test constraint that is feasible but very tight."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x >= 5.0)
        model.x.set_value(5.0 + 1e-7)  # Just barely feasible

        detector = UnfeasibilityDetector(model, tolerance=1e-6)
        violation = detector.check_constraint_feasibility(model.c)

        assert violation is None

    def test_marginally_infeasible(self):
        """Test constraint that is infeasible by tiny amount."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x >= 5.0)
        model.x.set_value(5.0 - 1e-5)  # Barely infeasible

        detector = UnfeasibilityDetector(model, tolerance=1e-6)
        violation = detector.check_constraint_feasibility(model.c)

        assert violation is not None
        assert violation.violation_amount > 0

    def test_custom_severity_levels(self):
        """Test custom severity level configuration."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x >= 10)
        model.x.set_value(0)

        custom_levels = {
            "critical": 1.0,
            "high": 0.1,
            "medium": 0.01,
            "low": 0.0,
        }
        detector = UnfeasibilityDetector(model, severity_levels=custom_levels)

        violations = detector.find_infeasible_constraints()
        assert len(violations) >= 1

    def test_invalid_model_initialization(self):
        """Test that invalid model type raises TypeError."""
        with pytest.raises(TypeError):
            UnfeasibilityDetector("not a model")

    def test_negative_tolerance_initialization(self):
        """Test that negative tolerance raises ValueError."""
        model = ConcreteModel()
        model.x = Var()

        with pytest.raises(ValueError):
            UnfeasibilityDetector(model, tolerance=-0.01)

    def test_incomplete_severity_levels(self):
        """Test handling of incomplete severity level specification."""
        model = ConcreteModel()
        model.x = Var()

        # Provide only some severity levels
        incomplete_levels = {"critical": 1.0, "high": 0.1}
        detector = UnfeasibilityDetector(model, severity_levels=incomplete_levels)

        # Should use defaults for missing levels
        assert "medium" in detector.severity_levels
        assert "low" in detector.severity_levels

    def test_invalid_severity_filter(self):
        """Test filtering by invalid severity level."""
        model = ConcreteModel()
        model.x = Var()
        model.c = Constraint(expr=model.x >= 10)
        model.x.set_value(0)

        detector = UnfeasibilityDetector(model)

        # Should handle invalid severity gracefully (with warning)
        violations = detector.find_infeasible_constraints(severity="invalid_level")

        # Should still return all violations since invalid level is ignored
        assert isinstance(violations, list)

    def test_severity_classification_ordering(self):
        """Test that severity classification follows correct ordering."""
        model = ConcreteModel()
        model.x = Var()

        detector = UnfeasibilityDetector(model)

        # Test classification at different violation amounts
        # critical: >= 1e-2 (0.01)
        # high: >= 1e-4 (0.0001)
        # medium: >= 1e-6 (0.000001)
        # low: >= 0.0
        assert detector._classify_severity(0.05) == "critical"
        assert detector._classify_severity(0.001) == "high"
        assert detector._classify_severity(0.00001) == "medium"
        assert detector._classify_severity(0.0) == "low"

    def test_feasibility_report_empty_model(self):
        """Test feasibility report for model with no constraints."""
        model = ConcreteModel()
        model.x = Var()

        detector = UnfeasibilityDetector(model)
        report = detector.feasibility_report()

        assert report["is_feasible"] is True
        assert report["total_constraints"] == 0
        assert report["infeasible_constraints"] == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
