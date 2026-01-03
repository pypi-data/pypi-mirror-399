# Development Guide

This document explains how to set up your development environment for PyomoSolverAnalyzer.

## Prerequisites

- Python 3.8 or higher
- Git

## Setting Up Your Environment

### 1. Install uv

`uv` is a fast Python package installer and resolver. Install it using:

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy BypassUser -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or using a package manager:
```bash
# Using Homebrew (macOS/Linux)
brew install uv

# Using Chocolatey (Windows)
choco install uv
```

### 2. Clone the Repository

```bash
git clone <repository-url>
cd PyomoSolverAnalyzer
```

### 3. Create Virtual Environment and Install Dependencies

```bash
# Create virtual environment and install dependencies
uv sync

# Activate the virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 4. Install Pre-commit Hooks

Pre-commit hooks automatically run code quality checks before each commit.

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install

# (Optional) Run hooks on all files
pre-commit run --all-files
```

## Development Workflow

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/pyomo_debugger

# Run specific test file
pytest tests/test_specific.py
```

### Code Quality Checks

```bash
# Format code with ruff
ruff format src/ tests/

# Lint code with ruff
ruff check src/ tests/

# Type check with mypy
mypy src/
```

### Pre-commit Hooks

Pre-commit hooks will run automatically on:
- **ruff format**: Code formatting (auto-fixes)
- **ruff lint**: Code linting with strict rules
- **mypy**: Static type checking with strict mode

You can also manually run hooks:

```bash
# Run hooks on staged files
pre-commit run

# Run hooks on all files
pre-commit run --all-files

# Skip pre-commit for a commit (not recommended)
git commit --no-verify
```

### Adding Dependencies

To add a new dependency:

```bash
# Add a main dependency
uv pip install package_name

# Add a development dependency
uv pip install -d package_name
```

Then update `requirements.txt` and `pyproject.toml` accordingly.

## Project Structure

```
PyomoSolverAnalyzer/
├── src/
│   └── pyomo_debugger/
│       └── __init__.py
├── tests/
│   └── test_basic.py
├── README.md
├── DEVELOPMENT.md
├── pyproject.toml
├── requirements.txt
├── .pre-commit-config.yaml
├── .gitignore
└── .venv/                 # Virtual environment (auto-created by uv)
```

## Common Tasks

### Creating a New Module

1. Create a new file in `src/pyomo_debugger/`
2. Add proper type hints to all functions
3. Add docstrings
4. Write tests in `tests/`

### Running Pre-commit on All Files

```bash
pre-commit run --all-files
```

### Updating Dependencies

```bash
# Update lock file
uv pip compile requirements.txt -o requirements.lock

# Install from lock file
uv sync
```

## Code Style Guidelines

- **Line length**: Maximum 88 characters
- **Type hints**: Strict (all functions and variables must be typed)
- **Formatting**: Enforced by ruff
- **Linting**: Enforced by ruff with strict rules
- **Type checking**: Enforced by mypy in strict mode

## Troubleshooting

### Pre-commit hooks failing

If pre-commit hooks fail:

1. Run the tools manually to see what's wrong:
   ```bash
   ruff format src/
   ruff check src/
   mypy src/
   ```

2. Fix issues reported by the tools

3. Commit again

### Virtual environment issues

If you have issues with the virtual environment:

```bash
# Remove and recreate
rm -rf .venv
uv sync
source .venv/bin/activate
```

### Dependency conflicts

If you encounter dependency conflicts:

```bash
# Clear and reinstall
uv pip sync --clear-cache requirements.txt
```

## Contributing

Before opening a pull request:

1. Ensure all tests pass: `pytest`
2. Ensure all code quality checks pass: `pre-commit run --all-files`
3. Write clear commit messages
4. Add tests for new features

For more information, see the main [README.md](README.md).
