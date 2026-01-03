"""
Unfeasibility detection and diagnosis module.

Provides tools for detecting and diagnosing infeasible or nearly-infeasible
solutions in Pyomo models.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pyomo.core.base.constraint import ConstraintData  # type: ignore
from pyomo.environ import ConcreteModel, Constraint  # type: ignore

from .introspection import ConstraintIntrospector

# Configure module logger
logger = logging.getLogger(__name__)

# Module-level constants for severity thresholds
DEFAULT_SEVERITY_LEVELS = {
    "critical": 1e-2,  # violation > 0.01
    "high": 1e-4,  # violation > 0.0001
    "medium": 1e-6,  # violation > 0.000001
    "low": 0.0,  # any positive violation
}
SEVERITY_ORDER = ["critical", "high", "medium", "low"]


@dataclass
class ConstraintViolation:
    """
    Represents a constraint violation.

    Attributes
    ----------
    constraint : ConstraintData
        The violating constraint.
    constraint_name : str
        Name of the constraint.
    violation_amount : float
        Amount by which constraint is violated (positive = infeasible).
    violation_type : str
        Type of violation: 'lower_bound', 'upper_bound', 'equality'.
    severity : str
        Severity level: 'critical', 'high', 'medium', 'low'.
    """

    constraint: ConstraintData
    constraint_name: str
    violation_amount: float
    violation_type: str
    severity: str

    def __str__(self) -> str:
        """String representation."""
        return (
            f"{self.constraint_name}: {self.violation_type} "
            f"violated by {self.violation_amount:.6e} ({self.severity})"
        )


class UnfeasibilityDetector:
    """
    Detects and diagnoses infeasibility and near-infeasibility in solutions.

    Identifies constraints that are violated or nearly violated, and provides
    severity classification.
    """

    def __init__(
        self,
        model: Any,
        tolerance: float = 1e-6,
        severity_levels: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Initialize the unfeasibility detector.

        Parameters
        ----------
        model : ConcreteModel
            The Pyomo model to analyze.
        tolerance : float
            Feasibility tolerance (default 1e-6).
        severity_levels : Dict[str, float], optional
            Custom severity thresholds mapping severity label to violation amount.

        Raises
        ------
        TypeError
            If model is not a valid Pyomo ConcreteModel or severity_levels is malformed.
        ValueError
            If tolerance is negative.
        """
        if not isinstance(model, ConcreteModel):
            raise TypeError(f"Expected ConcreteModel, got {type(model).__name__}")
        if tolerance < 0:
            raise ValueError(f"Tolerance must be non-negative, got {tolerance}")

        self.model: Any = model
        self.tolerance: float = tolerance

        # Validate and set severity levels
        if severity_levels is not None:
            # Ensure all required keys are present
            required_keys = set(SEVERITY_ORDER)
            provided_keys = set(severity_levels.keys())
            if not required_keys.issubset(provided_keys):
                logger.warning(
                    "severity_levels missing keys: %s. "
                    "Using defaults for missing keys.",
                    required_keys - provided_keys,
                )
                # Fill in missing keys from defaults
                combined = DEFAULT_SEVERITY_LEVELS.copy()
                combined.update(severity_levels)
                self.severity_levels = combined
            else:
                self.severity_levels = severity_levels
        else:
            self.severity_levels = DEFAULT_SEVERITY_LEVELS.copy()

        self.introspector: ConstraintIntrospector = ConstraintIntrospector(model)

    def _classify_severity(self, violation_amount: float) -> str:
        """
        Classify violation severity based on amount.

        Classifies in descending order: critical > high > medium > low.

        Parameters
        ----------
        violation_amount : float
            The violation amount.

        Returns
        -------
        str
            Severity level: 'critical', 'high', 'medium', or 'low'.
        """
        # Iterate through severity levels in order
        for severity in SEVERITY_ORDER:
            if violation_amount >= self.severity_levels.get(severity, 0):
                return severity
        return "low"

    def check_constraint_feasibility(
        self,
        constraint: ConstraintData,
    ) -> Optional[ConstraintViolation]:
        """
        Check if a single constraint is feasible.

        Parameters
        ----------
        constraint : ConstraintData
            The constraint to check.

        Returns
        -------
        Optional[ConstraintViolation]
            Violation object if infeasible, None if feasible.
        """
        result = self.introspector.evaluate_constraint_feasibility(
            constraint, self.tolerance
        )

        if not result["feasible"]:
            violation = result["violation"]
            violation_type = result["violation_type"]
            severity = self._classify_severity(violation)

            return ConstraintViolation(
                constraint=constraint,
                constraint_name=constraint.name,
                violation_amount=violation,
                violation_type=violation_type,
                severity=severity,
            )

        return None

    def find_infeasible_constraints(
        self,
        severity: Optional[str] = None,
    ) -> List[ConstraintViolation]:
        """
        Find all infeasible constraints in the model.

        Parameters
        ----------
        severity : str, optional
            Only return violations of specified severity or worse.
            Options: 'critical', 'high', 'medium', 'low'.

        Returns
        -------
        List[ConstraintViolation]
            List of violations, sorted by amount (descending).
        """
        violations = []

        for constraint in self.model.component_data_objects(Constraint, active=True):
            violation = self.check_constraint_feasibility(constraint)
            if violation is not None:
                violations.append(violation)

        # Sort by violation amount (descending)
        violations.sort(key=lambda v: v.violation_amount, reverse=True)

        # Filter by severity
        if severity is not None:
            if severity in SEVERITY_ORDER:
                min_index = SEVERITY_ORDER.index(severity)
                violations = [
                    v
                    for v in violations
                    if SEVERITY_ORDER.index(v.severity) <= min_index
                ]
            else:
                logger.warning(
                    "Invalid severity level: %s. Valid levels: %s",
                    severity,
                    ", ".join(SEVERITY_ORDER),
                )

        return violations

    def feasibility_report(self) -> Dict[str, Any]:
        """
        Generate a comprehensive feasibility report.

        Returns
        -------
        Dict[str, Any]
            Report with keys:
            - 'is_feasible': bool
            - 'total_constraints': int
            - 'infeasible_constraints': int
            - 'violations_by_severity': Dict[str, int]
            - 'max_violation': float
            - 'constraint_violations': List[ConstraintViolation]
            - 'total_violation': float
        """
        violations = self.find_infeasible_constraints()

        # Count violations by severity
        violations_by_severity = {
            "critical": sum(1 for v in violations if v.severity == "critical"),
            "high": sum(1 for v in violations if v.severity == "high"),
            "medium": sum(1 for v in violations if v.severity == "medium"),
            "low": sum(1 for v in violations if v.severity == "low"),
        }

        # Total violation amount
        total_violation = sum(v.violation_amount for v in violations)
        max_violation = max([v.violation_amount for v in violations], default=0.0)

        # Count total constraints
        total_constraints = len(
            list(self.model.component_data_objects(Constraint, active=True))
        )

        return {
            "is_feasible": len(violations) == 0,
            "total_constraints": total_constraints,
            "infeasible_constraints": len(violations),
            "violations_by_severity": violations_by_severity,
            "max_violation": max_violation,
            "total_violation": total_violation,
            "constraint_violations": violations,
        }

    def get_most_violated_constraints(
        self, top_n: int = 10
    ) -> List[ConstraintViolation]:
        """
        Get the most violated constraints.

        Parameters
        ----------
        top_n : int
            Number of constraints to return.

        Returns
        -------
        List[ConstraintViolation]
            Top N most violated constraints.
        """
        violations = self.find_infeasible_constraints()
        return violations[:top_n]
