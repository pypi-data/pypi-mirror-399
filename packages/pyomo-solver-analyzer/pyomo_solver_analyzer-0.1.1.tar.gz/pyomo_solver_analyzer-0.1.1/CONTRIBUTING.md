# Contributing to PyomoSolverAnalyzer

Thank you for your interest in contributing to PyomoSolverAnalyzer! We welcome contributions from the community and appreciate your help in improving this project. This guide explains the standards and workflow we follow.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/yourusername/PyomoSolverAnalyzer.git
   cd PyomoSolverAnalyzer
   ```
3. Set up the development environment:
   ```bash
   uv sync
   source .venv/bin/activate
   pre-commit install
   ```
4. Create a feature branch from `main` using conventional naming

## Development Workflow

### 1. Creating a Branch

Create a new branch with a descriptive, conventional name before making changes:

```bash
git checkout -b type/description
```

**Branch naming convention:**
- `feature/add-model-validation` - New features
- `fix/connection-timeout-issue` - Bug fixes
- `docs/update-api-reference` - Documentation updates
- `refactor/simplify-parser` - Code refactoring
- `test/improve-coverage` - Test improvements
- `chore/update-dependencies` - Maintenance tasks

Use lowercase letters, hyphens to separate words, and be descriptive about the change.

### 2. Making Changes

- Follow the code style guidelines in [DEVELOPMENT.md](DEVELOPMENT.md)
- Write clear, well-documented code with type hints
- Add tests for new features
- Ensure all pre-commit checks pass:
  ```bash
  pre-commit run --all-files
  ```

### 3. Committing Changes

Use **conventional commit messages** for all commits:

```
type(scope): short description

Optional detailed explanation of the change and why it was made.

Closes #123
```

**Commit types:**
- `feat:` - A new feature
- `fix:` - A bug fix
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, missing semicolons, etc.)
- `refactor:` - Code refactoring without feature changes
- `perf:` - Performance improvements
- `test:` - Adding or updating tests
- `chore:` - Build, dependency, or tooling changes

**Commit message examples:**
```
feat(debugger): add model variable inspection

Implement a new feature to inspect model variables and their current values.
This allows users to better understand model state during debugging.

Closes #42
```

```
fix(parser): handle empty model declarations

Previously, parsing an empty model would raise an exception. Now it
correctly returns an empty model object.

Closes #89
```

### 4. Creating a Pull Request

Push your branch and create a pull request on GitHub:

```bash
git push origin feature/your-feature-name
```

**In the pull request description:**
- Reference any related issues using `Closes #123`
- Provide a clear summary of changes
- Explain the motivation and context
- Mention if there are any breaking changes

Example PR description:
```
## Description
Adds support for real-time model monitoring during optimization.

## Related Issues
Closes #156

## Changes
- Implement real-time variable tracking
- Add performance metrics collection
- Update documentation with examples

## Testing
- Added 5 new test cases
- All existing tests pass
- Tested with sample models in docs/examples
```

### 5. Code Review Process

- At least one maintainer review is required before merging
- Address feedback and push additional commits to the same branch
- Ensure all CI checks pass (linting, type checking, tests)
- Your branch will be squashed and merged with a clear commit message

## Code Quality Standards

All code contributions must meet these standards:

- **Tests:** New features must include tests with adequate coverage
- **Type Hints:** All functions and variables must have type hints (enforced by mypy)
- **Formatting:** Code must be formatted according to ruff standards
- **Linting:** No linting errors or warnings
- **Documentation:** Public APIs must have docstrings

Run checks locally before submitting:
```bash
# Format code
ruff format src/ tests/

# Check for linting issues
ruff check src/ tests/

# Type check
mypy src/

# Run tests
pytest

# Run all pre-commit checks
pre-commit run --all-files
```

## Commit and Branch Best Practices

### Keep Commits Atomic
Each commit should represent one logical change. This makes history easier to understand and enables better `git bisect` capability.

### Keep Branches Focused
Each branch should address a single issue or feature. If you find yourself working on multiple unrelated things, create separate branches.

### Rebase Before Submitting
If `main` has changed since you created your branch, rebase your changes:

```bash
git fetch origin
git rebase origin/main
git push origin your-branch-name --force-with-lease
```

## Pull Request Guidelines

- Keep PRs reasonably sized (aim for <400 lines of changes)
- Write a clear, descriptive title
- Reference related issues in the description
- Ensure your branch is up to date with `main`
- All CI checks must pass
- Request review from relevant team members

## Reporting Issues

When reporting bugs, please include:
- A clear, descriptive title
- Steps to reproduce the issue
- Expected vs. actual behavior
- Your environment (Python version, OS, etc.)
- Any relevant error messages or logs

## Questions or Need Help?

- Check existing issues and discussions
- Open a GitHub discussion for questions
- Review [DEVELOPMENT.md](DEVELOPMENT.md) for more technical details

## License

By contributing to PyomoSolverAnalyzer, you agree that your contributions will be licensed under the project's license.

---

Thank you for contributing to PyomoSolverAnalyzer! Your efforts help make debugging Pyomo models easier and more accessible for everyone.
