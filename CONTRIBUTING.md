# Contributing

## Setup for local development

1. Clone and install in dev mode:
   ```bash
   git clone https://github.com/vyoma/crabpol.git
   cd crabpol
   pip install -e .
   pip install -r requirements-dev.txt
   ```

2. Install pre-commit hooks (runs linters/formatters on `git commit`):
   ```bash
   pre-commit install
   ```

## Code quality

The project uses:
- **black** — code formatting
- **isort** — import sorting
- **flake8** — linting
- **mypy** — type checking (optional, errors ignored in CI)
- **pytest** — unit testing

### Running checks locally

```bash
# Format code
black crabpol

# Sort imports
isort crabpol

# Lint
flake8 crabpol

# Type check
mypy crabpol --ignore-missing-imports

# Run tests
pytest -v
```

Or run all at once:
```bash
make lint  # if you add a Makefile
```

## CI/CD

On push or PR to `main`/`develop`:
- Tests run on Python 3.9, 3.10, 3.11
- Linting, formatting, and type checks are verified
- Coverage is uploaded to Codecov
- All checks must pass before merge

## Pull requests

1. Fork and create a feature branch: `git checkout -b feat/xxx`
2. Make changes, commit with clear messages
3. Run tests locally: `pytest`
4. Push and open a PR against `main` or `develop`
5. Ensure CI passes and request review
