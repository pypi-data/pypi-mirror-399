# Mathematical Foundations

## Constraint Representation

Pyomo normalizes all constraints to the form:

$$\text{lower} \leq \text{body} \leq \text{upper}$$

Where:
- `lower`: Lower bound (or None)
- `body`: Expression in variables
- `upper`: Upper bound (or None)

### Constraint Types and Normalization

**Inequality constraint** ($\text{body} \leq \text{rhs}$):
$$\text{lower} = \text{None}, \quad \text{upper} = \text{rhs}$$

**Reverse inequality** ($\text{body} \geq \text{lhs}$):
$$\text{lower} = \text{lhs}, \quad \text{upper} = \text{None}$$

**Equality constraint** ($\text{body} = \text{value}$):
$$\text{lower} = \text{value}, \quad \text{upper} = \text{value}$$

**Ranged constraint** ($\text{lower} \leq \text{body} \leq \text{upper}$):
- Both bounds specified

## Slack and Surplus

At a solution point with variables at values $x^*$:

### Slack (for upper bound constraint)
$$s_{\text{upper}} = \text{upper} - \text{body}(x^*)$$

- **Positive slack**: Constraint is not binding, room for change
- **Zero slack**: Constraint is binding (active)
- **Negative slack**: Constraint is violated

### Surplus (for lower bound constraint)
$$s_{\text{lower}} = \text{body}(x^*) - \text{lower}$$

- **Positive surplus**: Constraint satisfied with room to spare
- **Zero surplus**: Constraint binding from below
- **Negative surplus**: Constraint violated

### Absolute Slack
For a constraint with both bounds, use the minimum absolute value:
$$s = \min(|s_{\text{lower}}|, |s_{\text{upper}}|)$$

## Normalized Slack

To compare constraints of different magnitudes:

$$\text{normalized slack} = \frac{s}{|\text{RHS}|}$$

Where RHS is the active bound magnitude.

**Properties**:
- Dimensionless (in relative terms)
- Comparable across different problem scales
- Robust to constraint rescaling
- Undefined when RHS = 0 (use absolute slack)

**Interpretation**:
- $\text{normalized slack} \approx 0$: Constraint is very tight
- $\text{normalized slack} \approx 1$: Slack equals RHS magnitude
- $\text{normalized slack} > 1$: Very loose constraint

## Tightness Score

Composite metric combining multiple indicators:

$$\text{score} = e^{-|\text{normalized slack}|} \cdot \text{utilization factor}$$

Where:
- **Exponential decay**: Penalizes larger slack values
- **Utilization factor**: Accounts for bound range consumption

**Properties**:
- Range: $[0, 1]$ where 1 = tight, 0 = loose
- Continuous and differentiable
- Scale-invariant (due to normalization)
- Sensitive to small changes near binding

**Interpretation**:
- Score > 0.95: Very tight (essentially binding)
- Score > 0.8: Tight (nearly binding)
- Score > 0.5: Moderately tight
- Score < 0.5: Loose constraint

## Bounds Utilization

For ranged constraints (both lower and upper):

$$u_{\text{lower}} = \frac{\text{body}(x^*) - \text{lower}}{\text{upper} - \text{lower}}$$

$$u_{\text{upper}} = \frac{\text{upper} - \text{body}(x^*)}{\text{upper} - \text{lower}}$$

**Properties**:
- Range: $[0, 1]$ for feasible solutions
- $u_{\text{lower}} + u_{\text{upper}} = 1$
- Close to 0 ⟹ constraint active on that side
- Close to 1 ⟹ constraint far from that bound

**Interpretation**:
- Both utilizations near 0.5: Constraint has symmetric slack
- One utilization near 0: Constraint active on that side
- One utilization >> 0.5: Constraint may be limiting

## Feasibility Violation

For constraint at solution $x^*$:

**Lower bound violation**:
$$v_{\text{lower}} = \max(0, \text{lower} - \text{body}(x^*) - \epsilon)$$

Where $\epsilon$ is feasibility tolerance.

**Upper bound violation**:
$$v_{\text{upper}} = \max(0, \text{body}(x^*) - \text{upper} - \epsilon)$$

**Total violation**:
$$v = \max(v_{\text{lower}}, v_{\text{upper}})$$

**Classification**:
- Feasible: $v \leq 0$
- Nearly-infeasible: $0 < v < $ small threshold
- Infeasible: $v > $ threshold

## Dual Values (Shadow Prices)

For linear constraints at optimality, dual value $\lambda$ represents:

$$\lambda = \frac{\partial z^*}{\partial b}$$

Where:
- $z^*$: Optimal objective value
- $b$: Constraint RHS
- $\lambda$: Marginal change in objective per unit RHS change

**Interpretation**:
- $\lambda > 0$: Increasing RHS improves objective
- $\lambda < 0$: Increasing RHS worsens objective
- $\lambda = 0$: RHS change doesn't affect objective (non-binding)
- Large $|\lambda|$: RHS is "valuable" to problem

**For inequality constraints**:
- Binding constraint: Dual may be non-zero
- Non-binding constraint: Dual must be zero (complementary slackness)

## Complementary Slackness Condition

At optimality of LP:

$$s_i \cdot \lambda_i = 0 \quad \forall i$$

Where:
- $s_i$: Slack of constraint $i$
- $\lambda_i$: Dual value of constraint $i$

**Implications**:
- If constraint is binding ($s_i = 0$): Dual can be non-zero
- If constraint is non-binding ($s_i > 0$): Dual must be zero
- Useful for identifying critical constraints

## Reduced Cost

For variables, the reduced cost indicates:

$$r_j = c_j - \sum_i \lambda_i a_{ij}$$

For variable $x_j$ at its bound:
- Changing bound cost per unit: $r_j$
- $r_j > 0$ at lower bound: Increasing $x_j$ worsens objective
- $r_j < 0$ at upper bound: Decreasing $x_j$ worsens objective

## Expression Decomposition

Constraint body expressions can contain:

### Linear terms
$$\sum_j c_j x_j$$

Where $c_j$ are constants, $x_j$ are variables.

### Quadratic terms
$$\sum_{j,k} Q_{jk} x_j x_k$$

### Nonlinear terms
Any nonlinear function of variables (sin, exp, etc.)

**Decomposition uses Pyomo's StandardRepn**:
- Separates linear from nonlinear components
- Extracts coefficients and variables
- Enables type-specific analysis

## Constraint Interaction

Constraints interact through shared variables:

For two constraints sharing variable $x$:
$$c_1: \text{lower}_1 \leq a_1 x + b_1 \leq \text{upper}_1$$
$$c_2: \text{lower}_2 \leq a_2 x + b_2 \leq \text{upper}_2$$

Tightness of one affects feasibility space for the other.

**Analysis implication**:
- Binding constraints form "active set"
- Changes to active set change feasible region
- Tightness analysis identifies potential bottlenecks

## Tolerance and Numerics

### Feasibility Tolerance
Default: $\epsilon = 10^{-6}$

Used for:
- Defining "binding" constraints: $|s| \leq \epsilon$
- Checking feasibility: violation $> \epsilon$
- Numerical stability in comparisons

### NaN Handling
When expression evaluation fails:
- Return NaN for that constraint
- Skip in aggregate calculations
- Log or note in diagnostics

### Very Large/Small Slack
- Very large slack: Constraint extremely loose
- Very small positive slack: Constraint nearly binding
- Negative slack: Infeasible

## Summary Table

| Metric | Formula | Range | Interpretation |
|--------|---------|-------|-----------------|
| Slack | $s = \text{upper} - \text{body}$ | $(-\infty, \infty)$ | Gap to bound |
| Normalized Slack | $s_n = s / \|b\|$ | $(-\infty, \infty)$ | Relative gap |
| Utilization | $u = s / (\text{upper} - \text{lower})$ | $[0, 1]$ | Fraction used |
| Tightness Score | $\text{exp}(-\|s_n\|)$ | $[0, 1]$ | How tight (1=tight) |
| Violation | $v = \max(0, -s)$ | $[0, \infty)$ | Infeasibility amount |
| Dual Value | $\partial z / \partial b$ | $(-\infty, \infty)$ | Marginal value |
