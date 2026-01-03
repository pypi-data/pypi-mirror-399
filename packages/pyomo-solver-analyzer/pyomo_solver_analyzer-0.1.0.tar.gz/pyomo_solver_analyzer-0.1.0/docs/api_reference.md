# API Reference

## Core Classes

### SolverDiagnostics

Main high-level interface for constraint analysis.

```python
class SolverDiagnostics:
    def __init__(
        self,
        model: ConcreteModel,
        results: Optional[Dict] = None,
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
        """
```

#### Methods

**get_tight_constraints**
```python
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
        Ranked list of tight constraints (descending tightness).
    """
```

**get_binding_constraints**
```python
def get_binding_constraints(self) -> List[ConstraintTightness]:
    """
    Get constraints that are binding (at feasibility tolerance).
    
    Returns
    -------
    List[ConstraintTightness]
        Binding constraints.
    """
```

**get_nearly_binding_constraints**
```python
def get_nearly_binding_constraints(
    self,
    slack_threshold: float = 0.01,
) -> List[ConstraintTightness]:
    """
    Get nearly-binding constraints (small slack).
    
    Parameters
    ----------
    slack_threshold : float
        Slack threshold for "nearly binding" (default 0.01).
        
    Returns
    -------
    List[ConstraintTightness]
        Nearly-binding constraints.
    """
```

**diagnose_feasibility**
```python
def diagnose_feasibility(self) -> Dict[str, Any]:
    """
    Diagnose feasibility of current solution.
    
    Returns
    -------
    Dict[str, Any]
        Feasibility report with keys:
        - 'is_feasible': bool
        - 'total_constraints': int
        - 'infeasible_constraints': int
        - 'violations_by_severity': Dict[str, int]
        - 'max_violation': float
        - 'constraint_violations': List[ConstraintViolation]
    """
```

**get_infeasible_constraints**
```python
def get_infeasible_constraints(self) -> List[ConstraintViolation]:
    """
    Get infeasible constraints (if any).
    
    Returns
    -------
    List[ConstraintViolation]
        List of infeasible constraints, sorted by violation amount.
    """
```

**constraint_statistics**
```python
def constraint_statistics(self) -> Dict[str, Any]:
    """
    Get summary statistics for all constraints.
    
    Returns
    -------
    Dict[str, Any]
        Statistics with keys:
        - 'total_constraints': int
        - 'binding_constraints': int
        - 'nearly_binding_constraints': int
        - 'avg_tightness_score': float
        - 'max_tightness_score': float
        - 'min_tightness_score': float
        - 'avg_slack': float
        - 'constraints_with_dual': int
    """
```

**generate_report**
```python
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
        Comprehensive report object.
    """
```

**print_report**
```python
def print_report(
    self,
    top_n_tight: int = 10,
    include_violations: bool = True,
) -> None:
    """
    Print a formatted diagnostics report to console.
    
    Parameters
    ----------
    top_n_tight : int
        Number of top tight constraints to include.
    include_violations : bool
        Whether to include feasibility violations.
    """
```

---

### ConstraintAnalyzer

Analyzes constraint tightness metrics.

```python
class ConstraintAnalyzer:
    def __init__(
        self,
        model,
        results=None,
        tolerance: float = 1e-6,
    ) -> None:
        """
        Initialize constraint analyzer.
        
        Parameters
        ----------
        model : ConcreteModel
            The Pyomo model.
        results : SolverResults, optional
            Solver results (for dual values).
        tolerance : float
            Feasibility tolerance (default 1e-6).
        """
```

#### Key Methods

**analyze_constraint**
```python
def analyze_constraint(
    self,
    constraint: ComponentData,
) -> ConstraintTightness:
    """
    Analyze tightness of a single constraint.
    
    Parameters
    ----------
    constraint : ConstraintData
        The constraint to analyze.
        
    Returns
    -------
    ConstraintTightness
        Tightness analysis results.
    """
```

**analyze_all_constraints**
```python
def analyze_all_constraints(self) -> List[ConstraintTightness]:
    """
    Analyze tightness of all active constraints.
    
    Returns
    -------
    List[ConstraintTightness]
        Analyses for all constraints.
    """
```

**get_tight_constraints**
```python
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
        Return only top N.
    threshold : float, optional
        Return only constraints with tightness >= threshold.
        
    Returns
    -------
    List[ConstraintTightness]
        Ranked constraints (descending tightness).
    """
```

**summary_statistics**
```python
def summary_statistics(self) -> Dict[str, Any]:
    """
    Compute summary statistics for all constraints.
    
    Returns
    -------
    Dict[str, Any]
        Statistics dictionary with aggregate metrics.
    """
```

---

### UnfeasibilityDetector

Detects and diagnoses constraint violations.

```python
class UnfeasibilityDetector:
    def __init__(
        self,
        model,
        tolerance: float = 1e-6,
        severity_levels: Optional[Dict[str, float]] = None,
    ) -> None:
        """
        Initialize unfeasibility detector.
        
        Parameters
        ----------
        model : ConcreteModel
            The Pyomo model.
        tolerance : float
            Feasibility tolerance (default 1e-6).
        severity_levels : Dict[str, float], optional
            Custom severity thresholds.
        """
```

#### Key Methods

**check_constraint_feasibility**
```python
def check_constraint_feasibility(
    self,
    constraint: ComponentData,
) -> Optional[ConstraintViolation]:
    """
    Check if a constraint is feasible.
    
    Parameters
    ----------
    constraint : ConstraintData
        The constraint to check.
        
    Returns
    -------
    Optional[ConstraintViolation]
        Violation object if infeasible, None if feasible.
    """
```

**find_infeasible_constraints**
```python
def find_infeasible_constraints(
    self,
    severity: Optional[str] = None,
) -> List[ConstraintViolation]:
    """
    Find all infeasible constraints.
    
    Parameters
    ----------
    severity : str, optional
        Only return violations of specified severity or worse.
        Options: 'critical', 'high', 'medium', 'low'.
        
    Returns
    -------
    List[ConstraintViolation]
        Violations sorted by amount (descending).
    """
```

**feasibility_report**
```python
def feasibility_report(self) -> Dict[str, Any]:
    """
    Generate comprehensive feasibility report.
    
    Returns
    -------
    Dict[str, Any]
        Report with feasibility summary and violation details.
    """
```

---

### ConstraintIntrospector

Low-level constraint evaluation and decomposition.

```python
class ConstraintIntrospector:
    def __init__(self, model) -> None:
        """
        Initialize introspector.
        
        Parameters
        ----------
        model : ConcreteModel
            The Pyomo model.
        """
```

#### Key Methods

**get_constraint_body_value**
```python
def get_constraint_body_value(self, constraint: ComponentData) -> float:
    """
    Evaluate constraint body at current variable values.
    
    Parameters
    ----------
    constraint : ConstraintData
        The constraint.
        
    Returns
    -------
    float
        Evaluated body value.
    """
```

**get_constraint_bounds**
```python
def get_constraint_bounds(
    self,
    constraint: ComponentData,
) -> Tuple[Optional[float], Optional[float]]:
    """
    Extract lower and upper bounds from constraint.
    
    Parameters
    ----------
    constraint : ConstraintData
        The constraint.
        
    Returns
    -------
    Tuple[Optional[float], Optional[float]]
        (lower_bound, upper_bound)
    """
```

**compute_slack**
```python
def compute_slack(self, constraint: ComponentData) -> float:
    """
    Compute constraint slack at current solution.
    
    Parameters
    ----------
    constraint : ConstraintData
        The constraint.
        
    Returns
    -------
    float
        Slack value (positive = not tight).
    """
```

**compute_normalized_slack**
```python
def compute_normalized_slack(
    self,
    constraint: ComponentData,
) -> float:
    """
    Compute slack normalized by RHS.
    
    Parameters
    ----------
    constraint : ConstraintData
        The constraint.
        
    Returns
    -------
    float
        Normalized slack (0 = tight, large = loose).
    """
```

**decompose_constraint_expression**
```python
def decompose_constraint_expression(
    self,
    constraint: ComponentData,
) -> Dict[str, Any]:
    """
    Decompose expression into linear/nonlinear components.
    
    Parameters
    ----------
    constraint : ConstraintData
        The constraint.
        
    Returns
    -------
    Dict[str, Any]
        Expression decomposition with:
        - 'is_linear': bool
        - 'constant': float
        - 'linear_terms': Dict[var_name → coef]
        - 'quadratic_terms': List[(var1, var2, coef)]
        - 'nonlinear_expr': str or None
        - 'variables': List[var_names]
    """
```

---

## Data Classes

### ConstraintTightness

```python
@dataclass
class ConstraintTightness:
    """Tightness metrics for a single constraint."""
    constraint: ComponentData        # The constraint object
    constraint_name: str             # Name of constraint
    slack: float                     # Absolute slack
    normalized_slack: float          # Slack / RHS
    lower_util: Optional[float]      # Lower bound utilization [0,1]
    upper_util: Optional[float]      # Upper bound utilization [0,1]
    tightness_score: float           # Overall score [0,1]
    is_binding: bool                 # Binding at tolerance
    dual: Optional[float] = None     # Dual value if available
```

### ConstraintViolation

```python
@dataclass
class ConstraintViolation:
    """Violation metrics for infeasible constraint."""
    constraint: ComponentData        # The constraint object
    constraint_name: str             # Name of constraint
    violation_amount: float          # How much violated
    violation_type: str              # 'lower_bound' or 'upper_bound'
    severity: str                    # 'critical', 'high', 'medium', 'low'
```

### DiagnosticsReport

```python
@dataclass
class DiagnosticsReport:
    """Comprehensive diagnostics report."""
    model_name: str                      # Model name
    solver_status: str                   # Solver status
    termination_condition: str           # Termination reason
    is_feasible: bool                    # Feasible solution
    tight_constraints: List[ConstraintTightness]  # Top tight
    infeasible_constraints: List[ConstraintViolation]  # Violations
    constraint_statistics: Dict[str, Any]  # Aggregate stats
    feasibility_summary: Dict[str, Any]    # Feasibility report
```

---

## Usage Examples

### Basic Usage

```python
from pyomo.environ import *
from pyomo_solver_analyzer import SolverDiagnostics

# Create and solve model
model = ConcreteModel()
model.x = Var(bounds=(0, 10))
model.y = Var(bounds=(0, 10))
model.obj = Objective(expr=model.x + model.y)
model.c1 = Constraint(expr=model.x + model.y >= 5)
model.c2 = Constraint(expr=2*model.x + model.y <= 15)

solver = SolverFactory('ipopt')
results = solver.solve(model)

# Analyze
diag = SolverDiagnostics(model, results)

# Get tight constraints
tight = diag.get_tight_constraints(top_n=5)
for t in tight:
    print(f"{t.constraint_name}: tightness={t.tightness_score:.4f}")

# Check feasibility
feas_report = diag.diagnose_feasibility()
print(f"Feasible: {feas_report['is_feasible']}")

# Print full report
diag.print_report()
```

### Accessing Dual Values

```python
# Request dual values
model.dual = Suffix(direction=Suffix.IMPORT)

# After solve and analysis
tight = diag.get_tight_constraints(top_n=5)
for t in tight:
    if t.dual is not None:
        print(f"Dual of {t.constraint_name}: {t.dual}")
```

### Custom Severity Levels

```python
from pyomo_solver_analyzer import UnfeasibilityDetector

detector = UnfeasibilityDetector(
    model,
    severity_levels={
        'critical': 1.0,
        'high': 0.1,
        'medium': 0.01,
        'low': 0.0,
    }
)

violations = detector.find_infeasible_constraints(severity='high')
```

### Filtering by Tightness

```python
# Get only very tight constraints
very_tight = diag.get_tight_constraints(threshold=0.9)

# Get nearly-binding constraints
nearly_binding = diag.get_nearly_binding_constraints(slack_threshold=0.001)
```

### Statistics and Reporting

```python
stats = diag.constraint_statistics()
print(f"Total constraints: {stats['total_constraints']}")
print(f"Binding constraints: {stats['binding_constraints']}")
print(f"Average tightness: {stats['avg_tightness_score']:.4f}")
```
