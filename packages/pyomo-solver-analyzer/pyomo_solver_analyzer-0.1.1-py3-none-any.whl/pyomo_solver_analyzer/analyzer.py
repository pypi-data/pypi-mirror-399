"""
Constraint analyzer module for computing tightness metrics.

Provides high-level analysis of constraint tightness and identification
of binding and nearly-binding constraints.
"""

import logging
import math
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from pyomo.core.base.constraint import ConstraintData  # type: ignore
from pyomo.environ import (  # type: ignore
    ConcreteModel,
    Constraint,
)

from .introspection import ConstraintIntrospector

# Configure module logger
logger = logging.getLogger(__name__)

# Module-level constants
NEARLY_BINDING_THRESHOLD = 0.01
DEFAULT_TOLERANCE = 1e-6


@dataclass
class ConstraintTightness:
    """
    Represents tightness metrics for a single constraint.

    Attributes
    ----------
    constraint : ConstraintData
        The constraint object.
    constraint_name : str
        Name of the constraint.
    slack : float
        Absolute slack value.
    normalized_slack : float
        Slack normalized by RHS.
    lower_util : Optional[float]
        Utilization of lower bound [0, 1].
    upper_util : Optional[float]
        Utilization of upper bound [0, 1].
    tightness_score : float
        Overall tightness score [0, 1] where 1 = tight.
    is_binding : bool
        Whether constraint is binding (at tolerance).
    dual : Optional[float]
        Dual value (shadow price).
    """

    constraint: ConstraintData
    constraint_name: str
    slack: float
    normalized_slack: float
    lower_util: Optional[float]
    upper_util: Optional[float]
    tightness_score: float
    is_binding: bool
    dual: Optional[float] = None

    def __str__(self) -> str:
        """String representation of constraint tightness."""
        return (
            f"{self.constraint_name}: "
            f"tightness={self.tightness_score:.4f}, "
            f"slack={self.slack:.6f}, "
            f"binding={self.is_binding}"
        )

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"ConstraintTightness(name={self.constraint_name}, "
            f"tightness={self.tightness_score:.4f}, "
            f"slack={self.slack:.6f}, "
            f"is_binding={self.is_binding})"
        )


class ConstraintAnalyzer:
    """
    Analyzes constraint tightness in solved Pyomo models.

    Computes various tightness metrics to identify binding and nearly-binding
    constraints without requiring additional model formulation.
    """

    def __init__(
        self,
        model: Any,
        results: Optional[Any] = None,
        tolerance: float = DEFAULT_TOLERANCE,
    ) -> None:
        """
        Initialize the constraint analyzer.

        Parameters
        ----------
        model : ConcreteModel
            The Pyomo model to analyze.
        results : SolverResults, optional
            Solver results object (used for dual values).
        tolerance : float
            Feasibility tolerance for identifying binding constraints.

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

        self.model: Any = model
        self.results: Optional[Any] = results
        self.tolerance: float = tolerance
        self.introspector: ConstraintIntrospector = ConstraintIntrospector(model)
        self._dual_mapping: Dict[str, Optional[float]] = self._extract_dual_values()

    def _extract_dual_values(self) -> Dict[str, Optional[float]]:
        """
        Extract dual values from model suffixes if available.

        Returns
        -------
        Dict[str, Optional[float]]
            Mapping of constraint names to dual values.
        """
        dual_mapping: Dict[str, Optional[float]] = {}

        # Try to get dual suffix from model
        try:
            if hasattr(self.model, "dual") and self.model.dual is not None:
                for constraint in self.model.component_data_objects(
                    Constraint, active=True
                ):
                    try:
                        dual_val = self.model.dual[constraint]
                        dual_mapping[constraint.name] = float(dual_val)
                    except (KeyError, TypeError):
                        dual_mapping[constraint.name] = None
            else:
                # No dual suffix available
                for constraint in self.model.component_data_objects(
                    Constraint, active=True
                ):
                    dual_mapping[constraint.name] = None
        except (AttributeError, TypeError) as e:
            logger.warning(
                "Failed to extract dual values from model: %s. "
                "Proceeding without dual data.",
                str(e),
            )

        return dual_mapping

    def _compute_tightness_score(
        self,
        constraint: ConstraintData,
        slack: float,
        normalized_slack: float,
    ) -> float:
        """
        Compute an overall tightness score for a constraint.

        Combines slack metrics into a single [0, 1] score where 1 = tight.

        Parameters
        ----------
        constraint : ConstraintData
            The constraint.
        slack : float
            Absolute slack value.
        normalized_slack : float
            Slack normalized by RHS.

        Returns
        -------
        float
            Tightness score in [0, 1].
        """
        if math.isnan(slack) or math.isnan(normalized_slack):
            return 0.0

        # Compute tightness using exponential decay of normalized slack.
        # The formula e^(-|normalized_slack|) naturally gives:
        #   - 1.0 when normalized_slack = 0 (binding constraint)
        #   - Values approaching 0 as normalized_slack increases (loose constraint)
        #   - Always in [0, 1] range without artificial capping

        # Use normalized slack if available (more robust across constraint scales)
        if not math.isnan(normalized_slack) and not math.isinf(normalized_slack):
            # Exponential decay based on normalized slack
            score = math.exp(-abs(normalized_slack))
        else:
            # Fall back to absolute slack if normalization fails
            # Use a normalized form: slack / (1 + |slack|) to keep bounded
            normalized = abs(slack) / (1.0 + abs(slack))
            score = math.exp(-normalized)

        # Ensure score stays in [0, 1] range (mathematical guarantee with exp function)
        return max(0.0, min(1.0, score))

    def analyze_constraint(self, constraint: ConstraintData) -> ConstraintTightness:
        """
        Analyze tightness of a single constraint.

        Parameters
        ----------
        constraint : ConstraintData
            The constraint to analyze.

        Returns
        -------
        ConstraintTightness
            Tightness analysis for the constraint.
        """
        slack = self.introspector.compute_slack(constraint)
        normalized_slack = self.introspector.compute_normalized_slack(constraint)
        lower_util, upper_util = self.introspector.compute_bounds_utilization(
            constraint
        )

        # Check if binding
        is_binding = abs(slack) <= self.tolerance if not math.isnan(slack) else False

        # Compute tightness score
        tightness_score = self._compute_tightness_score(
            constraint, slack, normalized_slack
        )

        # Get dual value
        dual = self._dual_mapping.get(constraint.name, None)

        return ConstraintTightness(
            constraint=constraint,
            constraint_name=constraint.name,
            slack=slack,
            normalized_slack=normalized_slack,
            lower_util=lower_util,
            upper_util=upper_util,
            tightness_score=tightness_score,
            is_binding=is_binding,
            dual=dual,
        )

    def analyze_all_constraints(self) -> List[ConstraintTightness]:
        """
        Analyze tightness of all active constraints in the model.

        Returns
        -------
        List[ConstraintTightness]
            List of tightness analyses for all constraints.
        """
        analyses = []
        for constraint in self.model.component_data_objects(Constraint, active=True):
            try:
                analysis = self.analyze_constraint(constraint)
                analyses.append(analysis)
            except (ValueError, TypeError, AttributeError) as e:
                # Log and skip constraints that cannot be analyzed
                logger.debug(
                    "Could not analyze constraint %s: %s",
                    constraint.name,
                    str(e),
                )
                continue

        return analyses

    def get_tight_constraints(
        self,
        top_n: Optional[int] = None,
        threshold: Optional[float] = None,
    ) -> List[ConstraintTightness]:
        """
        Get binding or nearly-binding constraints, ranked by tightness.

        Parameters
        ----------
        top_n : int, optional
            Return only top N constraints by tightness.
        threshold : float, optional
            Return only constraints with tightness >= threshold.

        Returns
        -------
        List[ConstraintTightness]
            Constraints sorted by tightness (descending).
        """
        analyses = self.analyze_all_constraints()

        # Sort by tightness score (descending)
        analyses.sort(key=lambda x: x.tightness_score, reverse=True)

        # Filter by threshold
        if threshold is not None:
            analyses = [a for a in analyses if a.tightness_score >= threshold]

        # Limit to top_n
        if top_n is not None:
            analyses = analyses[:top_n]

        return analyses

    def get_binding_constraints(self) -> List[ConstraintTightness]:
        """
        Get constraints that are binding (at feasibility tolerance).

        Returns
        -------
        List[ConstraintTightness]
            Binding constraints.
        """
        analyses = self.analyze_all_constraints()
        return [a for a in analyses if a.is_binding]

    def get_nearly_binding_constraints(
        self,
        slack_threshold: float = NEARLY_BINDING_THRESHOLD,
    ) -> List[ConstraintTightness]:
        """
        Get constraints that are nearly binding (slack below threshold).

        Parameters
        ----------
        slack_threshold : float
            Slack threshold for "nearly binding" classification.

        Returns
        -------
        List[ConstraintTightness]
            Nearly-binding constraints.
        """
        analyses = self.analyze_all_constraints()
        return [
            a
            for a in analyses
            if not math.isnan(a.slack) and abs(a.slack) <= slack_threshold
        ]

    def summary_statistics(self) -> Dict[str, Any]:
        """
        Compute summary statistics for all constraints.

        Returns
        -------
        Dict[str, Any]
            Dictionary with:
            - 'total_constraints': int
            - 'binding_constraints': int
            - 'nearly_binding_constraints': int
            - 'avg_tightness_score': float
            - 'max_tightness_score': float
            - 'min_tightness_score': float
            - 'avg_slack': float
            - 'constraints_with_dual': int
        """
        analyses = self.analyze_all_constraints()

        if not analyses:
            return {
                "total_constraints": 0,
                "binding_constraints": 0,
                "nearly_binding_constraints": 0,
                "avg_tightness_score": 0.0,
                "max_tightness_score": 0.0,
                "min_tightness_score": 0.0,
                "avg_slack": 0.0,
                "constraints_with_dual": 0,
            }

        tightness_scores = [a.tightness_score for a in analyses]
        slacks = [a.slack for a in analyses if not math.isnan(a.slack)]
        dual_values = [a.dual for a in analyses if a.dual is not None]

        return {
            "total_constraints": len(analyses),
            "binding_constraints": sum(1 for a in analyses if a.is_binding),
            "nearly_binding_constraints": sum(
                1 for a in analyses if abs(a.slack) <= NEARLY_BINDING_THRESHOLD
            ),
            "avg_tightness_score": sum(tightness_scores) / len(tightness_scores),
            "max_tightness_score": max(tightness_scores),
            "min_tightness_score": min(tightness_scores),
            "avg_slack": sum(slacks) / len(slacks) if slacks else 0.0,
            "constraints_with_dual": len(dual_values),
        }
