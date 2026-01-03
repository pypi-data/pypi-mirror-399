"""
Test suite for pyomo-solver-analyzer

Comprehensive tests for constraint analysis, tightness metrics, and
unfeasibility detection.
"""


import pytest
from pyomo.environ import (
    ConcreteModel,
    Constraint,
    Objective,
    SolverFactory,
    Var,
)

from pyomo_solver_analyzer.analyzer import ConstraintAnalyzer, ConstraintTightness
from pyomo_solver_analyzer.diagnostics import SolverDiagnostics
from pyomo_solver_analyzer.introspection import ConstraintIntrospector
from pyomo_solver_analyzer.unfeasibility import (
    ConstraintViolation,
    UnfeasibilityDetector,
)


def require_solver(solver_name: str) -> None:
    """Require a solver to be available, raise error if not."""
    try:
        solver = SolverFactory(solver_name)
        # Increase timeout for solvers that may be slow to initialize
        try:
            available = solver.available()
        except Exception as availability_error:
            # Handle timeout or other errors during availability check
            raise Exception(
                f"Solver {solver_name} availability check failed: {availability_error}"
            ) from availability_error

        if not available:
            raise Exception(f"Solver {solver_name} is not available")
    except Exception as e:
        pytest.fail(f"Required solver '{solver_name}' is not installed/available: {e}")


def optional_solver(solver_name: str) -> bool:
    """Check if a solver is available (returns True/False without raising)."""
    try:
        import shutil

        # For SCIP, just check if executable exists due to slow version check
        if solver_name == "scip":
            return shutil.which("scip") is not None

        # For other solvers, use Pyomo's availability check
        solver = SolverFactory(solver_name)
        return solver.available()
    except Exception:
        return False


class TestConstraintIntrospector:
    """Tests for ConstraintIntrospector."""

    @pytest.fixture
    def simple_model(self):
        """Create a simple test model."""
        model = ConcreteModel()
        model.x = Var(bounds=(0, 10))
        model.y = Var(bounds=(0, 10))
        model.c1 = Constraint(expr=model.x + model.y >= 5)
        model.c2 = Constraint(expr=2 * model.x + model.y <= 15)
        model.obj = Objective(expr=model.x + model.y)

        # Set variable values for testing
        model.x.set_value(5)
        model.y.set_value(3)

        return model

    def test_constraint_body_value(self, simple_model):
        """Test constraint body evaluation."""
        introspector = ConstraintIntrospector(simple_model)

        body_val = introspector.get_constraint_body_value(simple_model.c1)
        assert abs(body_val - 8.0) < 1e-6  # 5 + 3 = 8

    def test_constraint_bounds(self, simple_model):
        """Test constraint bounds extraction."""
        introspector = ConstraintIntrospector(simple_model)

        lower, upper = introspector.get_constraint_bounds(simple_model.c1)
        assert lower == 5.0  # x + y >= 5
        assert upper is None

        lower, upper = introspector.get_constraint_bounds(simple_model.c2)
        assert lower is None
        assert upper == 15.0  # 2x + y <= 15

    def test_compute_slack(self, simple_model):
        """Test slack computation."""
        introspector = ConstraintIntrospector(simple_model)

        # For c1: x + y >= 5, slack = body - lower = 8 - 5 = 3
        slack1 = introspector.compute_slack(simple_model.c1)
        assert abs(slack1 - 3.0) < 1e-6

        # For c2: 2x + y <= 15, slack = upper - body = 15 - 13 = 2
        slack2 = introspector.compute_slack(simple_model.c2)
        assert abs(slack2 - 2.0) < 1e-6

    def test_compute_normalized_slack(self, simple_model):
        """Test normalized slack computation."""
        introspector = ConstraintIntrospector(simple_model)

        norm_slack = introspector.compute_normalized_slack(simple_model.c1)
        # slack = 3, RHS = 5, normalized = 3/5 = 0.6
        assert abs(norm_slack - 0.6) < 1e-6

    def test_bounds_utilization(self, simple_model):
        """Test bounds utilization computation."""
        introspector = ConstraintIntrospector(simple_model)

        lower_util, upper_util = introspector.compute_bounds_utilization(
            simple_model.c1
        )
        # c1: x + y >= 5, body = 8
        # No upper bound, so upper_util should be None
        assert lower_util is not None
        assert upper_util is None

    def test_decompose_constraint_expression(self, simple_model):
        """Test constraint expression decomposition."""
        introspector = ConstraintIntrospector(simple_model)

        decomp = introspector.decompose_constraint_expression(simple_model.c1)
        assert decomp["is_linear"] is True
        assert "x" in decomp["variables"]
        assert "y" in decomp["variables"]
        assert len(decomp["linear_terms"]) >= 1

    def test_evaluate_constraint_feasibility(self, simple_model):
        """Test feasibility evaluation."""
        introspector = ConstraintIntrospector(simple_model)

        feas = introspector.evaluate_constraint_feasibility(simple_model.c1)
        assert feas["feasible"] is True
        assert feas["violation"] <= 0.0


class TestConstraintAnalyzer:
    """Tests for ConstraintAnalyzer."""

    @pytest.fixture
    def tight_model(self):
        """Create a model with tight constraints."""
        model = ConcreteModel()
        model.x = Var(bounds=(0, 10))
        model.y = Var(bounds=(0, 10))
        model.c1 = Constraint(expr=model.x + model.y >= 9.99)  # Very tight
        model.c2 = Constraint(expr=2 * model.x + model.y <= 15)
        model.obj = Objective(expr=model.x + model.y)

        model.x.set_value(5)
        model.y.set_value(5)

        return model

    @pytest.fixture
    def loose_model(self):
        """Create a model with loose constraints."""
        model = ConcreteModel()
        model.x = Var(bounds=(0, 100))
        model.y = Var(bounds=(0, 100))
        model.c1 = Constraint(expr=model.x + model.y >= 1)  # Very loose
        model.c2 = Constraint(expr=2 * model.x + model.y <= 500)
        model.obj = Objective(expr=model.x + model.y)

        model.x.set_value(50)
        model.y.set_value(50)

        return model

    def test_analyze_constraint_tight(self, tight_model):
        """Test analysis of tight constraints."""
        analyzer = ConstraintAnalyzer(tight_model)

        analysis = analyzer.analyze_constraint(tight_model.c1)
        assert isinstance(analysis, ConstraintTightness)
        assert analysis.is_binding or analysis.slack < 0.01
        assert analysis.tightness_score > 0.8

    def test_analyze_constraint_loose(self, loose_model):
        """Test analysis of loose constraints."""
        analyzer = ConstraintAnalyzer(loose_model)

        analysis = analyzer.analyze_constraint(loose_model.c1)
        assert isinstance(analysis, ConstraintTightness)
        assert not analysis.is_binding
        assert analysis.slack > 0

    def test_analyze_all_constraints(self, tight_model):
        """Test batch constraint analysis."""
        analyzer = ConstraintAnalyzer(tight_model)

        analyses = analyzer.analyze_all_constraints()
        assert len(analyses) >= 2
        assert all(isinstance(a, ConstraintTightness) for a in analyses)

    def test_get_tight_constraints(self, tight_model):
        """Test retrieval of tight constraints."""
        analyzer = ConstraintAnalyzer(tight_model)

        tight = analyzer.get_tight_constraints(top_n=1)
        assert len(tight) == 1
        # c2 has zero slack (2*5 + 5 = 15, exactly at bound) so it's tighter than c1
        assert tight[0].constraint_name == "c2"

    def test_get_binding_constraints(self, tight_model):
        """Test retrieval of binding constraints."""
        analyzer = ConstraintAnalyzer(tight_model)

        # c1 should be binding or very tight
        binding = analyzer.get_binding_constraints()
        assert len(binding) >= 1

    def test_summary_statistics(self, tight_model):
        """Test summary statistics."""
        analyzer = ConstraintAnalyzer(tight_model)

        stats = analyzer.summary_statistics()
        assert stats["total_constraints"] == 2
        assert stats["binding_constraints"] >= 1
        assert 0 <= stats["avg_tightness_score"] <= 1
        assert stats["max_tightness_score"] >= stats["min_tightness_score"]

    def test_tightness_score_range(self, tight_model, loose_model):
        """Test that tightness scores are in valid range."""
        tight_analyzer = ConstraintAnalyzer(tight_model)
        loose_analyzer = ConstraintAnalyzer(loose_model)

        tight_analysis = tight_analyzer.analyze_constraint(tight_model.c1)
        loose_analysis = loose_analyzer.analyze_constraint(loose_model.c1)

        assert 0 <= tight_analysis.tightness_score <= 1
        assert 0 <= loose_analysis.tightness_score <= 1
        assert tight_analysis.tightness_score > loose_analysis.tightness_score


class TestUnfeasibilityDetector:
    """Tests for UnfeasibilityDetector."""

    @pytest.fixture
    def feasible_model(self):
        """Create a feasible model."""
        model = ConcreteModel()
        model.x = Var(bounds=(0, 10))
        model.y = Var(bounds=(0, 10))
        model.c1 = Constraint(expr=model.x + model.y >= 5)
        model.c2 = Constraint(expr=2 * model.x + model.y <= 15)
        model.obj = Objective(expr=model.x + model.y)

        model.x.set_value(5)
        model.y.set_value(3)

        return model

    @pytest.fixture
    def infeasible_model(self):
        """Create an infeasible model."""
        model = ConcreteModel()
        model.x = Var(bounds=(0, 10))
        model.y = Var(bounds=(0, 10))
        model.c1 = Constraint(expr=model.x + model.y >= 100)  # Impossible
        model.obj = Objective(expr=model.x + model.y)

        model.x.set_value(5)
        model.y.set_value(3)

        return model

    def test_check_feasible_constraint(self, feasible_model):
        """Test feasibility check on feasible constraint."""
        detector = UnfeasibilityDetector(feasible_model)

        violation = detector.check_constraint_feasibility(feasible_model.c1)
        assert violation is None  # Should not violate

    def test_check_infeasible_constraint(self, infeasible_model):
        """Test feasibility check on infeasible constraint."""
        detector = UnfeasibilityDetector(infeasible_model)

        violation = detector.check_constraint_feasibility(infeasible_model.c1)
        assert violation is not None
        assert violation.violation_amount > 0
        assert isinstance(violation, ConstraintViolation)

    def test_find_infeasible_constraints(self, infeasible_model):
        """Test finding all infeasible constraints."""
        detector = UnfeasibilityDetector(infeasible_model)

        violations = detector.find_infeasible_constraints()
        assert len(violations) >= 1
        assert all(isinstance(v, ConstraintViolation) for v in violations)

    def test_feasibility_report_feasible(self, feasible_model):
        """Test feasibility report for feasible model."""
        detector = UnfeasibilityDetector(feasible_model)

        report = detector.feasibility_report()
        assert report["is_feasible"] is True
        assert report["infeasible_constraints"] == 0

    def test_feasibility_report_infeasible(self, infeasible_model):
        """Test feasibility report for infeasible model."""
        detector = UnfeasibilityDetector(infeasible_model)

        report = detector.feasibility_report()
        assert report["is_feasible"] is False
        assert report["infeasible_constraints"] >= 1
        assert report["max_violation"] > 0

    def test_severity_classification(self, infeasible_model):
        """Test violation severity classification."""
        detector = UnfeasibilityDetector(infeasible_model)

        violations = detector.find_infeasible_constraints()
        assert len(violations) >= 1
        assert violations[0].severity in ["critical", "high", "medium", "low"]


class TestSolverDiagnostics:
    """Tests for SolverDiagnostics."""

    @pytest.fixture
    def test_model(self):
        """Create a test model."""
        model = ConcreteModel()
        model.x = Var(bounds=(0, 10))
        model.y = Var(bounds=(0, 10))
        model.c1 = Constraint(expr=model.x + model.y >= 5)
        model.c2 = Constraint(expr=2 * model.x + model.y <= 15)
        model.obj = Objective(expr=model.x + model.y)

        model.x.set_value(5)
        model.y.set_value(3)

        return model

    def test_diagnostics_initialization(self, test_model):
        """Test diagnostics initialization."""
        diag = SolverDiagnostics(test_model)
        assert diag.model == test_model
        assert diag.analyzer is not None
        assert diag.unfeasibility_detector is not None

    def test_get_tight_constraints(self, test_model):
        """Test getting tight constraints."""
        diag = SolverDiagnostics(test_model)

        tight = diag.get_tight_constraints(top_n=1)
        assert isinstance(tight, list)
        assert len(tight) <= 1

    def test_diagnose_feasibility(self, test_model):
        """Test feasibility diagnostics."""
        diag = SolverDiagnostics(test_model)

        report = diag.diagnose_feasibility()
        assert "is_feasible" in report
        assert "infeasible_constraints" in report

    def test_constraint_statistics(self, test_model):
        """Test constraint statistics."""
        diag = SolverDiagnostics(test_model)

        stats = diag.constraint_statistics()
        assert "total_constraints" in stats
        assert stats["total_constraints"] >= 2

    def test_generate_report(self, test_model):
        """Test report generation."""
        diag = SolverDiagnostics(test_model)

        report = diag.generate_report()
        assert report.is_feasible is not None
        assert isinstance(report.tight_constraints, list)
        assert isinstance(report.constraint_statistics, dict)

    def test_print_report(self, test_model, capsys):
        """Test report printing."""
        diag = SolverDiagnostics(test_model)

        diag.print_report()
        captured = capsys.readouterr()
        assert "DIAGNOSTICS REPORT" in captured.out


class TestIntegration:
    """Integration tests with actual solvers."""

    def test_with_glpk_solver(self):
        """Test with GLPK solver (required)."""
        require_solver("glpk")

        model = ConcreteModel()
        model.x = Var(bounds=(0, 10))
        model.y = Var(bounds=(0, 10))
        model.c1 = Constraint(expr=model.x + model.y >= 5)
        model.c2 = Constraint(expr=2 * model.x + model.y <= 15)
        model.obj = Objective(expr=model.x + model.y)

        solver = SolverFactory("glpk")
        results = solver.solve(model)

        diag = SolverDiagnostics(model, results)
        tight = diag.get_tight_constraints()

        assert isinstance(tight, list)
        assert len(tight) >= 0

    @pytest.mark.skipif(not optional_solver("scip"), reason="SCIP solver not available")
    def test_with_scip_solver(self):
        """Test with SCIP solver (required)."""
        require_solver("scip")

        model = ConcreteModel()
        model.x = Var(bounds=(0, 10))
        model.y = Var(bounds=(0, 10))
        model.c1 = Constraint(expr=model.x + model.y >= 5)
        model.c2 = Constraint(expr=2 * model.x + model.y <= 15)
        model.obj = Objective(expr=model.x + model.y)

        solver = SolverFactory("scip")
        results = solver.solve(model, tee=False)

        diag = SolverDiagnostics(model, results)
        report = diag.generate_report()

        assert report is not None
        assert hasattr(report, "tight_constraints")
        assert hasattr(report, "constraint_statistics")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
