"""
Constraint introspection module for Pyomo models.

Provides tools for extracting constraint bodies, evaluating constraints,
and decomposing expressions into linear/nonlinear components.
"""

import logging
import math
from typing import Any, Dict, Optional, Set, Tuple

from pyomo.core.base.constraint import ConstraintData  # type: ignore
from pyomo.environ import (  # type: ignore
    ConcreteModel,
    value,
)

# Configure module logger
logger = logging.getLogger(__name__)


class ConstraintIntrospector:
    """
    Provides introspection capabilities for Pyomo constraints.

    Allows evaluation of constraint bodies, slack/surplus computation,
    bounds extraction, and expression decomposition.
    """

    def __init__(self, model: Any) -> None:
        """
        Initialize the constraint introspector.

        Parameters
        ----------
        model : ConcreteModel
            The Pyomo model to introspect.

        Raises
        ------
        TypeError
            If model is not a valid Pyomo ConcreteModel.
        """
        if not isinstance(model, ConcreteModel):
            raise TypeError(f"Expected ConcreteModel, got {type(model).__name__}")
        self.model: Any = model

    def get_constraint_body_value(self, constraint: ConstraintData) -> float:
        """
        Evaluate the constraint body at current variable values.

        Parameters
        ----------
        constraint : ConstraintData
            The constraint to evaluate.

        Returns
        -------
        float
            The value of the constraint body.
        """
        try:
            return float(value(constraint.body))
        except (ValueError, TypeError):
            return float("nan")

    def get_constraint_bounds(
        self, constraint: ConstraintData
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Extract lower and upper bounds from a constraint.

        Normalizes constraint expressions to (lower, body, upper) form.

        Parameters
        ----------
        constraint : ConstraintData
            The constraint to analyze.

        Returns
        -------
        Tuple[Optional[float], Optional[float]]
            (lower_bound, upper_bound)
        """
        try:
            lower, body, upper = constraint.to_bounded_expression()
            lower_val = None if lower is None else float(value(lower))
            upper_val = None if upper is None else float(value(upper))
            return lower_val, upper_val
        except Exception:
            return None, None

    def compute_slack(self, constraint: ConstraintData) -> float:
        """
        Compute constraint slack/surplus at current solution.

        For constraint form (lower <= body <= upper):
        - Slack to lower = body - lower (positive means constraint satisfied)
        - Slack to upper = upper - body (positive means constraint satisfied)

        This method returns the slack to the binding side.

        Parameters
        ----------
        constraint : ConstraintData
            The constraint to analyze.

        Returns
        -------
        float
            The slack value (positive = constraint not tight).
        """
        lower, upper = self.get_constraint_bounds(constraint)
        body_val = self.get_constraint_body_value(constraint)

        if math.isnan(body_val):
            return float("nan")

        slacks = []
        if lower is not None and not math.isnan(lower):
            slacks.append(body_val - lower)
        if upper is not None and not math.isnan(upper):
            slacks.append(upper - body_val)

        if not slacks:
            return float("nan")

        # Return the minimum slack (the binding constraint)
        return min(slacks)

    def compute_normalized_slack(self, constraint: ConstraintData) -> float:
        """
        Compute normalized slack relative to RHS.

        Slack divided by magnitude of relevant bound (for relative tightness).
        Uses the bound that determines the slack (the closest one).

        Parameters
        ----------
        constraint : ConstraintData
            The constraint to analyze.

        Returns
        -------
        float
            Normalized slack (0 = tight, large positive = loose).
        """
        slack = self.compute_slack(constraint)
        lower, upper = self.get_constraint_bounds(constraint)
        body_val = self.get_constraint_body_value(constraint)

        if math.isnan(slack) or math.isnan(body_val):
            return float("nan")
        if slack == 0:
            return 0.0

        # Determine which bound is "active" or closest, corresponding to the slack
        # Slack is min(body - lower, upper - body)
        rhs_magnitude: float = 0.0

        # Calculate distances to bounds
        dist_lower = float("inf")
        dist_upper = float("inf")

        if lower is not None and not math.isnan(lower):
            dist_lower = body_val - lower
        if upper is not None and not math.isnan(upper):
            dist_upper = upper - body_val

        # Identify closest bound
        if dist_lower < dist_upper:
            # Closer to lower bound
            rhs_magnitude = abs(lower) if lower is not None else 0.0
        else:
            # Closer to upper bound
            rhs_magnitude = abs(upper) if upper is not None else 0.0

        if rhs_magnitude == 0:
            return abs(slack)  # Return absolute slack if RHS is zero

        return abs(slack / rhs_magnitude)

    def compute_bounds_utilization(
        self, constraint: ConstraintData
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Compute what fraction of available bounds are used.

        For lower bound: (body - lower) / (upper - lower)
        For upper bound: (upper - body) / (upper - lower)

        Returns
        -------
        Tuple[Optional[float], Optional[float]]
            (lower_utilization, upper_utilization) in [0, 1] range.
            None if bound not applicable.
        """
        lower, upper = self.get_constraint_bounds(constraint)
        body_val = self.get_constraint_body_value(constraint)

        if math.isnan(body_val):
            return None, None

        lower_util = None
        upper_util = None

        if (
            lower is not None
            and upper is not None
            and not (math.isnan(lower) or math.isnan(upper))
        ):
            range_val = upper - lower
            if range_val != 0:
                lower_util = (body_val - lower) / range_val
                upper_util = (upper - body_val) / range_val
        elif lower is not None and not math.isnan(lower):
            lower_util = body_val - lower
        elif upper is not None and not math.isnan(upper):
            upper_util = upper - body_val

        return lower_util, upper_util

    def decompose_constraint_expression(
        self, constraint: ConstraintData
    ) -> Dict[str, Any]:
        """
        Decompose constraint expression into linear and nonlinear components.

        Uses Pyomo's StandardRepn for expression analysis.

        Parameters
        ----------
        constraint : ConstraintData
            The constraint to decompose.

        Returns
        -------
        Dict[str, Any]
            Dictionary with keys:
            - 'is_linear': bool
            - 'constant': float
            - 'linear_terms': Dict[var_name → coefficient]
            - 'quadratic_terms': List[(var1_name, var2_name, coefficient)]
            - 'nonlinear_expr': str representation or None
            - 'variables': List of variable names
        """
        try:
            from pyomo.repn import generate_standard_repn  # type: ignore

            repn = generate_standard_repn(constraint.body)

            is_linear = repn.nonlinear_expr is None

            # Extract linear terms
            linear_terms = {}
            if repn.linear_vars:
                for var, coef in zip(repn.linear_vars, repn.linear_coefs):
                    linear_terms[var.name] = float(coef)

            # Extract quadratic terms
            quadratic_terms = []
            if repn.quadratic_vars:
                for (var1, var2), coef in zip(
                    repn.quadratic_vars, repn.quadratic_coefs
                ):
                    quadratic_terms.append((var1.name, var2.name, float(coef)))

            # Get all variables
            all_vars: Set[str] = set()
            if repn.linear_vars:
                all_vars.update(v.name for v in repn.linear_vars)
            if repn.quadratic_vars:
                for v1, v2 in repn.quadratic_vars:
                    all_vars.add(v1.name)
                    all_vars.add(v2.name)

            return {
                "is_linear": is_linear,
                "constant": float(repn.constant) if repn.constant else 0.0,
                "linear_terms": linear_terms,
                "quadratic_terms": quadratic_terms,
                "nonlinear_expr": str(repn.nonlinear_expr)
                if repn.nonlinear_expr
                else None,
                "variables": sorted(all_vars),
            }
        except (ImportError, AttributeError) as e:
            # Fallback: try to determine linearity by checking expression structure
            logger.debug(
                "Could not decompose expression for %s with standard repn: %s. "
                "Using string fallback.",
                constraint.name,
                str(e),
            )
            is_linear = True
            try:
                # Simple heuristic: check if expression contains nonlinear operators
                expr_str = str(constraint.body)
                nonlinear_ops = ["sin", "cos", "tan", "exp", "log", "**", "^"]
                is_linear = not any(op in expr_str for op in nonlinear_ops)
            except (TypeError, AttributeError) as e2:
                logger.debug(
                    "Could not determine linearity for constraint %s: %s",
                    constraint.name,
                    str(e2),
                )

            return {
                "is_linear": is_linear,
                "constant": None,
                "linear_terms": {},
                "quadratic_terms": [],
                "nonlinear_expr": str(constraint.body),
                "variables": [],
            }

    def evaluate_constraint_feasibility(
        self, constraint: ConstraintData, tolerance: float = 1e-6
    ) -> Dict[str, Any]:
        """
        Evaluate constraint feasibility at current solution.

        Parameters
        ----------
        constraint : ConstraintData
            The constraint to check.
        tolerance : float
            Feasibility tolerance (default 1e-6).

        Returns
        -------
        Dict[str, Any]
            Dictionary with keys:
            - 'feasible': bool
            - 'violation': float (positive = infeasible)
            - 'violation_type': str ('lower_bound', 'upper_bound', 'none')
            - 'violation_margin': float
            - 'active': bool (binding at tolerance)
        """
        lower, upper = self.get_constraint_bounds(constraint)
        body_val = self.get_constraint_body_value(constraint)

        if math.isnan(body_val):
            return {
                "feasible": False,
                "violation": float("nan"),
                "violation_type": "error",
                "violation_margin": float("nan"),
                "active": False,
                "error": "Cannot evaluate constraint body",
            }

        violation = 0.0
        violation_type = "none"
        violation_margin = float("inf")

        # Check lower bound
        if lower is not None and not math.isnan(lower):
            diff = lower - body_val
            if diff > tolerance:
                if diff > violation:
                    violation = diff
                    violation_type = "lower_bound"
            violation_margin = min(violation_margin, body_val - lower)

        # Check upper bound
        if upper is not None and not math.isnan(upper):
            diff = body_val - upper
            if diff > tolerance:
                if diff > violation:
                    violation = diff
                    violation_type = "upper_bound"
            violation_margin = min(violation_margin, upper - body_val)

        is_feasible = violation <= 0.0
        is_active = abs(violation_margin) <= tolerance

        return {
            "feasible": is_feasible,
            "violation": violation,
            "violation_type": violation_type,
            "violation_margin": violation_margin,
            "active": is_active,
        }
