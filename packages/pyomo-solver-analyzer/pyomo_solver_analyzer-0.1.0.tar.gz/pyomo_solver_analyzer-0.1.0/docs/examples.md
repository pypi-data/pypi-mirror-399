# Examples and Usage Guide

## Quick Start Example

The simplest way to analyze a Pyomo model:

```python
from pyomo.environ import *
from pyomo_solver_analyzer import SolverDiagnostics

# Step 1: Create your model
model = ConcreteModel()
model.x = Var(bounds=(0, 10), within=NonNegativeReals)
model.y = Var(bounds=(0, 10), within=NonNegativeReals)

model.obj = Objective(expr=model.x + model.y, sense=minimize)
model.capacity = Constraint(expr=model.x + model.y <= 15)
model.min_prod = Constraint(expr=model.x + model.y >= 5)

# Step 2: Solve it
solver = SolverFactory('ipopt')
results = solver.solve(model)

# Step 3: Analyze constraints
diag = SolverDiagnostics(model, results)
diag.print_report()
```

Output:
```
================================================================================
SOLVER DIAGNOSTICS REPORT
================================================================================

Model: unknown
Solver Status: ok
Termination: optimal
Feasible: True

--------------------------------------------------------------------------------
CONSTRAINT STATISTICS
--------------------------------------------------------------------------------
Total Constraints: 2
Binding Constraints: 0
Nearly-Binding Constraints: 1
Average Tightness Score: 0.7823
Max Tightness Score: 0.9456
Min Tightness Score: 0.6190
Constraints with Dual Values: 2

--------------------------------------------------------------------------------
TOP 2 TIGHT CONSTRAINTS
--------------------------------------------------------------------------------
1. min_prod                       | Tightness: 0.9456 | Slack: 0.000123 | Binding: False
2. capacity                       | Tightness: 0.6190 | Slack: 0.004567 | Binding: False

================================================================================
```

---

## Example 1: Production Planning Problem

A manufacturer must decide production levels for multiple products given resource constraints.

```python
from pyomo.environ import *
from pyomo_solver_analyzer import SolverDiagnostics

# Create model
model = ConcreteModel()

# Products: A, B, C
products = ['A', 'B', 'C']

# Decision variables: production quantity for each product
model.production = Var(products, bounds=(0, 100), within=NonNegativeReals)

# Objective: maximize profit
profit = {'A': 10, 'B': 15, 'C': 12}
model.profit = Objective(
    expr=sum(profit[p] * model.production[p] for p in products),
    sense=maximize
)

# Constraints
# Machine hours constraint (max 500 hours)
machine_hours = {'A': 2, 'B': 3, 'C': 2.5}
model.machine_hours = Constraint(
    expr=sum(machine_hours[p] * model.production[p] for p in products) <= 500
)

# Raw material constraint (max 1000 units)
material = {'A': 1, 'B': 2, 'C': 1.5}
model.raw_material = Constraint(
    expr=sum(material[p] * model.production[p] for p in products) <= 1000
)

# Quality requirement: product A at least 20 units
model.quality = Constraint(expr=model.production['A'] >= 20)

# Solve
solver = SolverFactory('glpk')
results = solver.solve(model)

# Analyze
diag = SolverDiagnostics(model, results)

print("\n=== CONSTRAINT TIGHTNESS ANALYSIS ===")
tight = diag.get_tight_constraints(top_n=5)
for i, t in enumerate(tight, 1):
    print(f"{i}. {t.constraint_name}")
    print(f"   Tightness: {t.tightness_score:.4f}")
    print(f"   Slack: {t.slack:.2f}")
    print(f"   Binding: {t.is_binding}")
    print()

print("\n=== BINDING CONSTRAINTS ===")
binding = diag.get_binding_constraints()
if binding:
    for b in binding:
        print(f"- {b.constraint_name} (slack={b.slack:.6f})")
else:
    print("No binding constraints found")

print("\n=== STATISTICS ===")
stats = diag.constraint_statistics()
print(f"Average tightness: {stats['avg_tightness_score']:.4f}")
print(f"Constraints with duals: {stats['constraints_with_dual']}")
```

**Analysis Insights**:
- Machine hours constraint will be the bottleneck (highest tightness)
- Raw material constraint has slack (less restrictive)
- Quality constraint is easily satisfied

---

## Example 2: Portfolio Optimization with Risk

Optimize a financial portfolio subject to diversification constraints.

```python
from pyomo.environ import *
from pyomo_solver_analyzer import SolverDiagnostics

# Data
assets = ['Stock_A', 'Stock_B', 'Bond_A', 'Bond_B', 'Cash']
expected_return = {'Stock_A': 0.12, 'Stock_B': 0.10, 'Bond_A': 0.05, 'Bond_B': 0.04, 'Cash': 0.01}
risk = {'Stock_A': 0.20, 'Stock_B': 0.18, 'Bond_A': 0.03, 'Bond_B': 0.02, 'Cash': 0.0}

model = ConcreteModel()

# Portfolio weights
model.weight = Var(assets, bounds=(0, 1), within=NonNegativeReals)

# Objective: maximize return (for given risk level)
model.return_obj = Objective(
    expr=sum(expected_return[a] * model.weight[a] for a in assets),
    sense=maximize
)

# Constraints
# All weights sum to 1
model.budget = Constraint(
    expr=sum(model.weight[a] for a in assets) == 1
)

# Maximum 30% in any single stock
model.max_stock = ConstraintList()
for stock in ['Stock_A', 'Stock_B']:
    model.max_stock.add(model.weight[stock] <= 0.30)

# Minimum 20% in bonds for stability
model.min_bonds = Constraint(
    expr=model.weight['Bond_A'] + model.weight['Bond_B'] >= 0.20
)

# Maximum 50% total stocks
model.max_total_stocks = Constraint(
    expr=model.weight['Stock_A'] + model.weight['Stock_B'] <= 0.50
)

# Minimum 10% cash for liquidity
model.min_cash = Constraint(expr=model.weight['Cash'] >= 0.10)

# Solve
solver = SolverFactory('ipopt')
results = solver.solve(model)

# Analyze
diag = SolverDiagnostics(model, results)

print("\n=== PORTFOLIO CONSTRAINT ANALYSIS ===")
print(f"Solution Status: {results.solver.status}")
print(f"Termination: {results.solver.termination_condition}")

print("\n=== BINDING CONSTRAINTS (Limiting Factors) ===")
binding = diag.get_binding_constraints()
for b in binding:
    print(f"- {b.constraint_name}")
    print(f"  Slack: {b.slack:.6f}")
    if b.dual is not None:
        print(f"  Shadow price: {b.dual:.6f}")

print("\n=== NEARLY BINDING CONSTRAINTS (Risk Zones) ===")
nearly = diag.get_nearly_binding_constraints(slack_threshold=0.05)
for n in nearly:
    print(f"- {n.constraint_name}")
    print(f"  Slack: {n.slack:.6f}")
    print(f"  Tightness: {n.tightness_score:.4f}")

# Interpretation
print("\n=== INTERPRETATION ===")
if binding:
    print("The following constraints are limiting portfolio diversification:")
    for b in binding:
        print(f"  • {b.constraint_name}")
    print("\nTo improve returns, these constraints should be relaxed if possible.")
else:
    print("Portfolio has significant slack in most constraints.")
    print("Consider increasing risk/return if objectives allow.")
```

---

## Example 3: Feasibility Diagnosis

Detect and diagnose why a problem is infeasible.

```python
from pyomo.environ import *
from pyomo_solver_analyzer import SolverDiagnostics

# Create an infeasible problem
model = ConcreteModel()
model.x = Var(bounds=(0, 10))
model.y = Var(bounds=(0, 10))

model.obj = Objective(expr=model.x + model.y)

# Conflicting constraints
model.c1 = Constraint(expr=model.x + model.y >= 15)  # Min 15
model.c2 = Constraint(expr=model.x + model.y <= 10)  # Max 10

# Try to solve (will be infeasible or fail)
solver = SolverFactory('ipopt')
results = solver.solve(model)

# Analyze
diag = SolverDiagnostics(model, results)

print("\n=== FEASIBILITY DIAGNOSIS ===")
report = diag.diagnose_feasibility()
print(f"Feasible: {report['is_feasible']}")
print(f"Total constraints: {report['total_constraints']}")
print(f"Infeasible constraints: {report['infeasible_constraints']}")
print(f"Max violation: {report['max_violation']:.6e}")

if report['infeasible_constraints'] > 0:
    print("\n=== VIOLATION DETAILS ===")
    for violation in report['constraint_violations']:
        print(f"Constraint: {violation.constraint_name}")
        print(f"  Type: {violation.violation_type}")
        print(f"  Amount: {violation.violation_amount:.6e}")
        print(f"  Severity: {violation.severity}")

# Find conflicts
print("\n=== CONFLICT ANALYSIS ===")
print("Constraints in conflict:")
for v in report['constraint_violations'][:5]:
    print(f"  - {v.constraint_name}: {v.violation_type}")
```

---

## Example 4: Sensitivity Analysis - What If?

Analyze how constraint tightness changes with parameter variations.

```python
from pyomo.environ import *
import pandas as pd
from pyomo_solver_analyzer import SolverDiagnostics

def create_and_analyze_model(capacity):
    """Create model with given capacity and return tightness scores."""
    model = ConcreteModel()
    model.x = Var(bounds=(0, 100))
    model.y = Var(bounds=(0, 100))
    
    model.obj = Objective(expr=model.x + 2*model.y)
    model.capacity = Constraint(expr=model.x + model.y <= capacity)
    model.demand = Constraint(expr=model.x + model.y >= 50)
    
    solver = SolverFactory('ipopt')
    results = solver.solve(model, tee=False)
    
    diag = SolverDiagnostics(model, results)
    stats = diag.constraint_statistics()
    
    return {
        'capacity': capacity,
        'avg_tightness': stats['avg_tightness_score'],
        'binding_constraints': stats['binding_constraints'],
        'max_tightness': stats['max_tightness_score'],
    }

# Test different capacity levels
results_list = []
for cap in [50, 75, 100, 150, 200]:
    results_list.append(create_and_analyze_model(cap))

# Display results
df = pd.DataFrame(results_list)
print(df)
print("\nInsight: As capacity increases, average tightness decreases")
print("(Constraints become looser, less limiting)")
```

---

## Example 5: Custom Tightness Metrics

Extend the analyzer with custom metrics.

```python
from pyomo.environ import *
from pyomo_solver_analyzer import ConstraintAnalyzer, ConstraintTightness

class CustomAnalyzer(ConstraintAnalyzer):
    """Extended analyzer with custom metrics."""
    
    def _compute_tightness_score(self, constraint, slack, normalized_slack, 
                                 lower_util, upper_util):
        """Custom tightness score emphasizing bound utilization."""
        import math
        
        if math.isnan(normalized_slack):
            return 0.0
        
        # Original exponential decay score
        base_score = math.exp(-abs(normalized_slack))
        
        # Bonus for high utilization
        if lower_util is not None or upper_util is not None:
            utils = [u for u in [lower_util, upper_util] 
                    if u is not None and not math.isnan(u)]
            if utils:
                max_util = max(abs(u) for u in utils)
                utilization_bonus = 0.3 * min(1.0, max(max_util - 0.3, 0))
                return min(1.0, base_score + utilization_bonus)
        
        return base_score

# Use custom analyzer
model = ConcreteModel()
model.x = Var(bounds=(0, 10))
model.y = Var(bounds=(0, 10))
model.c1 = Constraint(expr=model.x + model.y >= 5)
model.c2 = Constraint(expr=model.x + model.y <= 15)
model.obj = Objective(expr=model.x + model.y)

model.x.set_value(7)
model.y.set_value(6)

# Standard analyzer
std_analyzer = ConstraintAnalyzer(model)
std_scores = std_analyzer.analyze_all_constraints()

# Custom analyzer
custom_analyzer = CustomAnalyzer(model)
custom_scores = custom_analyzer.analyze_all_constraints()

print("Tightness Scores Comparison:")
print(f"{'Constraint':<20} {'Standard':<15} {'Custom':<15}")
for std, custom in zip(std_scores, custom_scores):
    print(f"{std.constraint_name:<20} {std.tightness_score:<15.4f} {custom.tightness_score:<15.4f}")
```

---

## Best Practices

### 1. Always Request Relevant Suffixes

```python
# Request duals for LP/QP problems
model.dual = Suffix(direction=Suffix.IMPORT)
model.slack = Suffix(direction=Suffix.IMPORT)

# Then analyze
solver.solve(model)
diag = SolverDiagnostics(model)
tight = diag.get_tight_constraints()
```

### 2. Use Appropriate Tolerances

```python
# For well-scaled problems
diag = SolverDiagnostics(model, tolerance=1e-6)

# For poorly-scaled problems
diag = SolverDiagnostics(model, tolerance=1e-4)
```

### 3. Filter Meaningfully

```python
# Get only very tight constraints
very_tight = diag.get_tight_constraints(threshold=0.95)

# Get only critical violations
critical = diag.get_infeasible_constraints(severity='critical')
```

### 4. Combine Multiple Analyses

```python
# Check both tightness and feasibility
tight = diag.get_binding_constraints()
feasible = diag.diagnose_feasibility()

if not feasible['is_feasible']:
    print("Problem is infeasible!")
elif tight:
    print(f"Problem has {len(tight)} binding constraints")
```

### 5. Generate Actionable Reports

```python
# Full diagnostic report
diag.print_report(top_n_tight=10)

# Or use generated report for further processing
report = diag.generate_report()
for constraint in report.tight_constraints:
    # Take action based on constraint properties
    if constraint.dual is not None and constraint.dual > 1000:
        print(f"Critical bottleneck: {constraint.constraint_name}")
```
