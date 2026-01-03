# Contributing to prlyn

Thank you for your interest in contributing to prlyn! We welcome contributions of all forms, from bug reports to new features.

## How to Contribute

### 1. Reporting Bugs
- Use GitHub Issues to report bugs.
- Provide a clear description and steps to reproduce.

### 2. Feature Requests
- Open an issue to discuss new features before implementation.

### 3. Development Setup
- Clone the repository.
- Use `uv` for dependency management: `uv sync`.
- Run tests: `uv run pytest`.

### 4. Pull Requests
- Fork the repository and create a branch using the following conventions:
  - `feature/` for new features and enhancements.
  - `bugfix/` for bug fixes.
  - `patch/` for small fixes or documentation updates.
  - `refactor/` for code refactoring with no functional changes.
- Ensure all tests pass.
- Write clear commit messages.
- Provide a detailed PR description.

### 5. Release Process (Maintainers Only)
To publish a new version to PyPI:
1.  Update `version` in `pyproject.toml`.
2.  Commit the change: `git commit -am "chore: bump version to X.Y.Z"`
3.  Push the commit: `git push`
4.  Create and push a tag:
    ```bash
    git tag vX.Y.Z
    git push origin vX.Y.Z
    ```
The `publish.yml` workflow will automatically build and upload the package to PyPI using Trusted Publishing.

## Code of Conduct
Please be respectful and professional in all interactions.
