# PyomoSolverAnalyzer

A constraint analysis and debugging toolkit for [Pyomo](http://www.pyomo.org/), an open-source optimization modeling language in Python. This library provides tools for analyzing solver outputs, diagnosing infeasibility, and identifying binding constraints in linear optimization models.

## Features

Three core capabilities designed to help you understand and improve optimization models:

- **Find Bottlenecks**: Identify tight constraints limiting your solution (via `ConstraintAnalyzer`)
- **Diagnose Infeasibility**: When models fail to solve, diagnose constraint violations and their severity (via `UnfeasibilityDetector`)
- **Extract Insights**: Unified interface extracting dual values, slack analysis, and sensitivity metrics (via `SolverDiagnostics`)

## Installation

Install from PyPI:
```bash
pip install pyomo-solver-analyzer
```

Or install from source with development dependencies:
```bash
git clone https://github.com/jaimeam/Pyomo-Solver-Analyzer.git
cd PyomoSolverAnalyzer
pip install -e ".[dev]"
```

## Quick Start

The simplest approach is to use `SolverDiagnostics` for complete analysis:

```python
from pyomo_solver_analyzer import SolverDiagnostics
import pyomo.environ as pyo

model = pyo.ConcreteModel()
# ... define and solve your model ...
solver = pyo.SolverFactory('glpk')
results = solver.solve(model)

# One-line diagnostics report
diagnostics = SolverDiagnostics(model, results)
diagnostics.print_report()
```

For specialized analyses or detailed examples, see the [Examples Guide](docs/examples.md).

## Documentation

- [API Reference](docs/api_reference.md)
- [Architecture Guide](docs/architecture.md)
- [Examples](docs/examples.md)
- [Mathematical Background](docs/mathematics.md)

## Development

For detailed development setup instructions, see [DEVELOPMENT.md](DEVELOPMENT.md).

### Project Structure

```
PyomoSolverAnalyzer/
├── src/
│   └── pyomo_solver_analyzer/       # Main package
│       ├── __init__.py
│       ├── analyzer.py
│       ├── diagnostics.py
│       ├── introspection.py
│       └── unfeasibility.py
├── tests/                           # Test suite
├── docs/                            # Documentation
├── README.md
├── LICENSE
├── pyproject.toml                   # Project configuration
└── DEVELOPMENT.md
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Before committing, ensure:
1. Code passes `ruff` linting: `ruff check src/`
2. Code passes `mypy` type checking: `mypy src/`
3. Tests pass: `pytest tests/`
4. Pre-commit hooks pass: `pre-commit run --all-files`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For issues, questions, or feature requests, please open an issue on [GitHub](https://github.com/jaimeam/Pyomo-Solver-Analyzer/issues).

## Citation

If you use this library in your research, please cite:

```bibtex
@software{pyomo_solver_analyzer,
  title={Pyomo Solver Analyzer},
  author={Adroher, Jaime},
  year={2025},
  url={https://github.com/jaimeam/Pyomo-Solver-Analyzer}
}
```
