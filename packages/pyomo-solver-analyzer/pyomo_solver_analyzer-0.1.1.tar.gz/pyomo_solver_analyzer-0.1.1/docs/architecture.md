# Architecture Overview

## System Design

The Pyomo Solver Analyzer is organized into modular layers:

```
┌─────────────────────────────────────────────────────────────┐
│         SolverDiagnostics (User-Facing API)                 │
│   - Unified interface for constraint analysis               │
│   - Report generation & pretty printing                     │
│   - START HERE for most analyses                            │
└──────────┬──────────────────────┬───────────────────────────┘
           │                      │
           ▼                      ▼
    ┌───────────────────┐  ┌─────────────────────┐
    │ConstraintAnalyzer │  │UnfeasibilityDetector│
    │                   │  │                     │
    │- Tightness        │  │- Violation detect   │
    │  metrics          │  │- Severity levels    │
    │- Binding detect   │  │- Infeasibility      │
    │- Dual values      │  │  diagnosis          │
    └────────┬──────────┘  └────────┬────────────┘
             │                      │
             └──────────────┬───────┘
                            │
                            ▼
            ┌────────────────────────────────────┐
            │  ConstraintIntrospector            │
            │  (Internal Infrastructure)         │
            │                                    │
            │  - Body evaluation                 │
            │  - Bounds extraction               │
            │  - Slack computation               │
            │  - Expression decomposition        │
            └────────────────┬───────────────────┘
                             │
                             ▼
                      ┌──────────────┐
                      │ Pyomo Model  │
                      └──────────────┘
```

## When to Use Each Module

### SolverDiagnostics (Recommended starting point)
Use this for **complete analysis** of a solved model:
- Want overall diagnostics report
- Need tight constraints + feasibility status together
- Don't need to customize individual analyses

```python
diag = SolverDiagnostics(model, results)
diag.print_report()  # One-liner analysis
```

### ConstraintAnalyzer (Specialized: Tightness Analysis)
Use this when you **only care about constraint tightness**:
- Finding bottleneck constraints
- Ranking by binding status
- Sensitivity to constraint relaxation
- Custom tightness thresholds

```python
analyzer = ConstraintAnalyzer(model)
tight = analyzer.get_tight_constraints(top_n=10)
```

### UnfeasibilityDetector (Specialized: Feasibility Diagnosis)
Use this when you **only care about infeasibility**:
- Model failed to solve or is infeasible
- Diagnosing constraint violations
- Severity classification of violations
- Custom violation thresholds

```python
detector = UnfeasibilityDetector(model, tolerance=1e-5)
violations = detector.find_infeasible_constraints()
```

### ConstraintIntrospector (Internal Use Only)
This is **not intended for direct use**. It's used internally by other modules. Exposed here for documentation and advanced extension only.

## Core Modules

### 1. ConstraintIntrospector (`introspection.py`)

**Purpose**: Extract and evaluate constraint properties from a Pyomo model.

**Key Responsibilities**:
- Evaluate constraint bodies at current variable values
- Extract constraint bounds (lower, upper)
- Compute constraint slack/surplus
- Decompose expressions (linear/nonlinear components)
- Check feasibility at specified tolerances

**Key Methods**:
- `get_constraint_body_value()`: Evaluate body expression
- `get_constraint_bounds()`: Extract (lower, upper)
- `compute_slack()`: Calculate constraint slack
- `compute_normalized_slack()`: Slack relative to RHS
- `compute_bounds_utilization()`: Fraction of bounds used
- `decompose_constraint_expression()`: Linear/nonlinear analysis
- `evaluate_constraint_feasibility()`: Feasibility check

**Design Pattern**: 
- Pure evaluation/extraction, no state mutation
- All methods work with constraint data at current solution point
- Graceful degradation on evaluation errors

### 2. ConstraintAnalyzer (`analyzer.py`)

**Purpose**: Analyze constraint tightness and identify binding constraints.

**Key Responsibilities**:
- Compute tightness scores for all constraints
- Identify binding and nearly-binding constraints
- Extract and use dual values from Suffixes
- Provide constraint ranking by tightness
- Generate summary statistics

**Key Concepts**:

**Tightness Score**: A composite metric combining:
- Normalized slack (slack / RHS): Lower is tighter
- Bound utilization: How much of available range is used
- Exponential decay: Score approaches 1 as slack approaches 0

Formula: `score = exp(-|normalized_slack|)` adjusted by utilization

**Binding Constraint**: Constraint with slack ≤ tolerance (default 1e-6)

**Nearly-Binding Constraint**: Constraint with 0 < slack ≤ threshold

**Key Methods**:
- `analyze_constraint()`: Single constraint analysis → `ConstraintTightness`
- `analyze_all_constraints()`: Batch analysis
- `get_tight_constraints()`: Top N by tightness
- `get_binding_constraints()`: All binding constraints
- `get_nearly_binding_constraints()`: Nearly-binding with threshold
- `summary_statistics()`: Aggregate statistics

**Data Class**: `ConstraintTightness` encapsulates:
- `slack`: Absolute slack value
- `normalized_slack`: Slack / RHS
- `tightness_score`: [0, 1] where 1 = tight
- `is_binding`: Boolean flag
- `dual`: Dual value if available

### 3. UnfeasibilityDetector (`unfeasibility.py`)

**Purpose**: Detect and diagnose infeasible or nearly-infeasible constraints.

**Key Responsibilities**:
- Identify constraint violations
- Classify violations by severity
- Detect near-infeasible constraints
- Aggregate feasibility statistics

**Severity Classification**:
- `critical`: violation > 1e-2
- `high`: violation > 1e-4
- `medium`: violation > 1e-6
- `low`: any positive violation

**Key Methods**:
- `check_constraint_feasibility()`: Single constraint → Optional[Violation]
- `find_infeasible_constraints()`: All violations with severity filtering
- `find_near_infeasible_constraints()`: Constraints with small slack
- `feasibility_report()`: Comprehensive report
- `get_most_violated_constraints()`: Top N violations

**Data Class**: `ConstraintViolation` encapsulates:
- `constraint_name`: Constraint identifier
- `violation_amount`: How much constraint is violated
- `violation_type`: 'lower_bound', 'upper_bound'
- `severity`: Severity classification

### 4. SolverDiagnostics (`diagnostics.py`)

**Purpose**: High-level unified interface for all analyses.

**Key Responsibilities**:
- Orchestrate all sub-analyzers
- Generate comprehensive reports
- Provide pretty-print formatting
- Extract solver status information

**Key Methods**:
- `get_tight_constraints()`: Delegate to analyzer
- `get_binding_constraints()`: Delegate to analyzer
- `diagnose_feasibility()`: Delegate to detector
- `get_infeasible_constraints()`: Delegate to detector
- `constraint_statistics()`: Delegate to analyzer
- `generate_report()`: Create `DiagnosticsReport` object
- `print_report()`: Pretty-print report to console

**Data Class**: `DiagnosticsReport` aggregates:
- Solver status and termination condition
- Top tight constraints
- Any feasibility violations
- Aggregate statistics
- Feasibility summary

## Data Flow

### Typical Analysis Workflow

```python
# 1. Create and solve model
model = ConcreteModel()
# ... model construction ...
solver.solve(model)

# 2. Initialize diagnostics
diag = SolverDiagnostics(model, results)

# 3. Access analyses
tight = diag.get_tight_constraints(top_n=10)
infeas = diag.get_infeasible_constraints()
stats = diag.constraint_statistics()

# 4. Generate report
report = diag.generate_report()
diag.print_report()
```

### Internal Data Flow

1. **Introspection Layer** (ConstraintIntrospector)
   - Input: Pyomo constraint, current variable values
   - Output: Constraint body value, bounds, slack, decomposition
   - Processing: Evaluate expressions, normalize bounds

2. **Analysis Layer** (ConstraintAnalyzer)
   - Input: Pyomo model, introspection results, dual values
   - Output: Tightness scores, ranking, statistics
   - Processing: Compute metrics, extract duals from Suffixes

3. **Validation Layer** (UnfeasibilityDetector)
   - Input: Pyomo constraint, tolerance, severity levels
   - Output: Violations, classifications, report
   - Processing: Check bounds, classify by amount

4. **Presentation Layer** (SolverDiagnostics)
   - Input: All sub-analyzer results
   - Output: Formatted reports, statistics
   - Processing: Aggregate, format, present

## Extension Points

### Adding Custom Tightness Metrics

Extend `ConstraintAnalyzer._compute_tightness_score()`:

```python
class CustomAnalyzer(ConstraintAnalyzer):
    def _compute_tightness_score(self, constraint, slack, ...):
        # Custom metric computation
        custom_score = my_metric(slack, normalized_slack, ...)
        return custom_score
```

### Adding Custom Severity Levels

Pass custom thresholds to `UnfeasibilityDetector`:

```python
custom_levels = {
    'critical': 1.0,
    'high': 0.1,
    'medium': 0.01,
    'low': 0.0,
}
detector = UnfeasibilityDetector(model, severity_levels=custom_levels)
```

### Supporting Solver-Specific Data

Extract solver-specific information through Suffixes:

```python
# Before solve
model.solver_specific = Suffix(direction=Suffix.IMPORT)

# After solve, use in custom analyzer
dual_val = model.solver_specific[constraint]
```

## Mathematical Foundation

### Slack Computation

For constraint: `lower ≤ body ≤ upper`

- **Slack to lower**: `slack_lower = body - lower` (positive = satisfied)
- **Slack to upper**: `slack_upper = upper - body` (positive = satisfied)
- **Binding slack**: `min(slack_lower, slack_upper)` (active constraint)

### Normalized Slack

`normalized_slack = slack / |RHS|`

Ranges from:
- 0: Binding constraint
- ~1: Slack equals RHS magnitude
- >1: Slack much larger than RHS

### Tightness Score

`score = exp(-|normalized_slack|)` with utilization adjustment

- Approaches 1 as slack → 0 (tight)
- Approaches 0 as slack → ∞ (loose)
- Adjusted by bound utilization for robustness

### Feasibility Violation

For constraint violation:
- **Lower bound**: `violation = lower - body` (if body < lower - tol)
- **Upper bound**: `violation = body - upper` (if body > upper + tol)
- **Positive** violation = infeasible

## Error Handling Strategy

1. **Graceful Degradation**: When expression evaluation fails, return NaN
2. **Filtering**: Skip constraints that cannot be analyzed
3. **Tolerance Safety**: All comparisons include feasibility tolerance
4. **Type Safety**: Explicit type conversions with try-except blocks

## Performance Considerations

- **Lazy Evaluation**: Duals only extracted if Suffix present
- **Single Pass**: All constraints analyzed in single iteration
- **No Refactoring**: Original model never modified
- **Optional Caching**: Results not cached (recompute on demand)

## Limitations and Design Choices

1. **No IIS Detection**: Irreducible Infeasible Sets require solver-specific APIs
2. **Linear Assumption for Duals**: Dual values meaningless for nonlinear problems
3. **No Sensitivity Analysis**: Coefficient ranges not extracted (solver-specific)
4. **Tolerance Global**: Single tolerance for all feasibility checks
5. **No Variable Analysis**: Focus on constraints, not variable bounds
