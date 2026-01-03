"""
Main diagnostics module providing unified interface for constraint analysis.

High-level API for analyzing Pyomo solver results.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from pyomo.environ import ConcreteModel  # type: ignore

from .analyzer import ConstraintAnalyzer, ConstraintTightness
from .introspection import ConstraintIntrospector
from .unfeasibility import ConstraintViolation, UnfeasibilityDetector

# Configure module logger
logger = logging.getLogger(__name__)


@dataclass
class DiagnosticsReport:
    """
    Comprehensive diagnostics report for a solved model.

    Attributes
    ----------
    model_name : str
        Name of the model.
    solver_status : str
        Solver status (ok, error, etc.).
    termination_condition : str
        Termination condition (optimal, infeasible, etc.).
    is_feasible : bool
        Whether solution is feasible.
    tight_constraints : List[ConstraintTightness]
        Top binding/nearly-binding constraints.
    infeasible_constraints : List[ConstraintViolation]
        Infeasible constraints (if any).
    constraint_statistics : Dict[str, Any]
        Summary statistics.
    feasibility_summary : Dict[str, Any]
        Feasibility analysis summary.
    """

    model_name: str
    solver_status: str
    termination_condition: str
    is_feasible: bool
    tight_constraints: List[ConstraintTightness]
    infeasible_constraints: List[ConstraintViolation]
    constraint_statistics: Dict[str, Any]
    feasibility_summary: Dict[str, Any]


class SolverDiagnostics:
    """
    Main diagnostics interface for analyzing Pyomo solver results.

    Provides high-level API for constraint tightness analysis, feasibility
    diagnostics, and sensitivity information.

    Example
    -------
    >>> from pyomo.environ import *
    >>> from pyomo_solver_analyzer import SolverDiagnostics
    >>>
    >>> # Create and solve model
    >>> model = ConcreteModel()
    >>> model.x = Var(bounds=(0, 10))
    >>> model.obj = Objective(expr=model.x)
    >>> model.c1 = Constraint(expr=model.x >= 5)
    >>>
    >>> solver = SolverFactory('ipopt')
    >>> results = solver.solve(model)
    >>>
    >>> # Analyze
    >>> diag = SolverDiagnostics(model, results)
    >>> tight = diag.get_tight_constraints(top_n=5)
    >>> print(f"Top constraint: {tight[0]}")
    """

    def __init__(
        self,
        model: ConcreteModel,
        results: Optional[Dict[str, Any]] = None,
        tolerance: float = 1e-6,
    ) -> None:
        """
        Initialize solver diagnostics.

        Parameters
        ----------
        model : ConcreteModel
            The solved Pyomo model.
        results : SolverResults, optional
            Solver results object (for status/termination info).
        tolerance : float
            Feasibility tolerance (default 1e-6).

        Raises
        ------
        TypeError
            If model is not a valid Pyomo ConcreteModel.
        ValueError
            If tolerance is negative.
        """
        if not isinstance(model, ConcreteModel):
            raise TypeError(f"Expected ConcreteModel, got {type(model).__name__}")
        if tolerance < 0:
            raise ValueError(f"Tolerance must be non-negative, got {tolerance}")

        self.model: ConcreteModel = model
        self.results: Optional[Dict[str, Any]] = results
        self.tolerance: float = tolerance

        # Initialize sub-analyzers
        self.analyzer: ConstraintAnalyzer = ConstraintAnalyzer(
            model,
            results,
            tolerance,
        )
        self.unfeasibility_detector: UnfeasibilityDetector = UnfeasibilityDetector(
            model, tolerance
        )
        self.introspector: ConstraintIntrospector = ConstraintIntrospector(model)

    def _get_solver_status(self) -> Tuple[str, str]:
        """
        Extract solver status from results if available.

        Returns
        -------
        Tuple[str, str]
            (status, termination_condition)
        """
        if self.results is None:
            return "unknown", "unknown"

        status: str = "unknown"
        termination: str = "unknown"

        try:
            if hasattr(self.results, "solver"):
                status = str(self.results.solver.status)
                termination = str(self.results.solver.termination_condition)
        except Exception:
            pass

        return status, termination

    def get_tight_constraints(
        self,
        top_n: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> List[ConstraintTightness]:
        """
        Get binding/nearly-binding constraints ranked by tightness.

        Parameters
        ----------
        top_n : int, optional
            Return only top N constraints by tightness.
        threshold : float, optional
            Return only constraints with tightness >= threshold.

        Returns
        -------
        List[ConstraintTightness]
            Ranked list of tight constraints.
        """
        return self.analyzer.get_tight_constraints(top_n=top_n, threshold=threshold)

    def get_binding_constraints(self) -> List[ConstraintTightness]:
        """
        Get constraints that are binding (at feasibility tolerance).

        Returns
        -------
        List[ConstraintTightness]
            Binding constraints.
        """
        return self.analyzer.get_binding_constraints()

    def get_nearly_binding_constraints(
        self,
        slack_threshold: float = 0.01,
    ) -> List[ConstraintTightness]:
        """
        Get nearly-binding constraints.

        Parameters
        ----------
        slack_threshold : float
            Slack threshold for "nearly binding".

        Returns
        -------
        List[ConstraintTightness]
            Nearly-binding constraints.
        """
        return self.analyzer.get_nearly_binding_constraints(slack_threshold)

    def diagnose_feasibility(self) -> Dict[str, Any]:
        """
        Diagnose feasibility of current solution.

        Returns
        -------
        Dict[str, Any]
            Feasibility report with violations (if any).
        """
        return self.unfeasibility_detector.feasibility_report()

    def get_infeasible_constraints(self) -> List[ConstraintViolation]:
        """
        Get infeasible constraints (if any).

        Returns
        -------
        List[ConstraintViolation]
            List of infeasible constraints.
        """
        return self.unfeasibility_detector.find_infeasible_constraints()

    def constraint_statistics(self) -> Dict[str, Any]:
        """
        Get summary statistics for all constraints.

        Returns
        -------
        Dict[str, Any]
            Statistics including averages, counts, etc.
        """
        return self.analyzer.summary_statistics()

    def generate_report(
        self,
        top_n_tight: int = 10,
        include_violations: bool = True,
    ) -> DiagnosticsReport:
        """
        Generate comprehensive diagnostics report.

        Parameters
        ----------
        top_n_tight : int
            Number of top tight constraints to include.
        include_violations : bool
            Whether to include feasibility violations.

        Returns
        -------
        DiagnosticsReport
            Comprehensive diagnostics report.
        """
        status, termination = self._get_solver_status()
        feasibility = self.diagnose_feasibility()

        return DiagnosticsReport(
            model_name=self.model.name if hasattr(self.model, "name") else "unknown",
            solver_status=status,
            termination_condition=termination,
            is_feasible=feasibility["is_feasible"],
            tight_constraints=self.get_tight_constraints(top_n=top_n_tight),
            infeasible_constraints=(
                self.get_infeasible_constraints() if include_violations else []
            ),
            constraint_statistics=self.constraint_statistics(),
            feasibility_summary=feasibility,
        )

    def print_report(
        self,
        top_n_tight: int = 10,
        include_violations: bool = True,
    ) -> None:
        """
        Print a formatted diagnostics report.

        Parameters
        ----------
        top_n_tight : int
            Number of top tight constraints to include.
        include_violations : bool
            Whether to include feasibility violations.
        """
        report = self.generate_report(top_n_tight, include_violations)

        print("\n" + "=" * 80)
        print("SOLVER DIAGNOSTICS REPORT")
        print("=" * 80)

        print(f"\nModel: {report.model_name}")
        print(f"Solver Status: {report.solver_status}")
        print(f"Termination: {report.termination_condition}")
        print(f"Feasible: {report.is_feasible}")

        # Constraint statistics
        stats = report.constraint_statistics
        print("\n" + "-" * 80)
        print("CONSTRAINT STATISTICS")
        print("-" * 80)
        print(f"Total Constraints: {stats['total_constraints']}")
        print(f"Binding Constraints: {stats['binding_constraints']}")
        print(f"Nearly-Binding Constraints: {stats['nearly_binding_constraints']}")
        print(f"Average Tightness Score: {stats['avg_tightness_score']:.4f}")
        print(f"Max Tightness Score: {stats['max_tightness_score']:.4f}")
        print(f"Min Tightness Score: {stats['min_tightness_score']:.4f}")
        print(f"Constraints with Dual Values: {stats['constraints_with_dual']}")

        # Tight constraints
        print("\n" + "-" * 80)
        print(f"TOP {len(report.tight_constraints)} TIGHT CONSTRAINTS")
        print("-" * 80)
        for i, tc in enumerate(report.tight_constraints, 1):
            print(
                f"{i}. {tc.constraint_name:40s} | "
                f"Tightness: {tc.tightness_score:.4f} | "
                f"Slack: {tc.slack:.6e} | "
                f"Binding: {tc.is_binding}"
            )
            if tc.dual is not None:
                print(f"   Dual: {tc.dual:.6e}")

        # Feasibility
        feas = report.feasibility_summary
        if not report.is_feasible or feas["infeasible_constraints"] > 0:
            print("\n" + "-" * 80)
            print("FEASIBILITY ISSUES")
            print("-" * 80)
            print(f"Infeasible Constraints: {feas['infeasible_constraints']}")
            print(f"  Critical: {feas['violations_by_severity']['critical']}")
            print(f"  High: {feas['violations_by_severity']['high']}")
            print(f"  Medium: {feas['violations_by_severity']['medium']}")
            print(f"  Low: {feas['violations_by_severity']['low']}")
            print(f"Max Violation: {feas['max_violation']:.6e}")
            print(f"Total Violation: {feas['total_violation']:.6e}")

            if report.infeasible_constraints:
                print("\nTop Infeasible Constraints:")
                for i, viol in enumerate(report.infeasible_constraints[:5], 1):
                    print(
                        f"{i}. {viol.constraint_name:40s} | "
                        f"Violation: {viol.violation_amount:.6e} | "
                        f"Type: {viol.violation_type} | "
                        f"Severity: {viol.severity}"
                    )

        print("\n" + "=" * 80 + "\n")
