# Contributing to marketo-rest-api-wrapper

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/marketo-rest-api-wrapper.git
   cd marketo-rest-api-wrapper
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # or: venv\Scripts\activate  # Windows
   ```

3. Install in development mode:
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
pytest
```

With coverage:
```bash
pytest --cov=marketo_api --cov-report=html
```

## Code Quality

We use the following tools — please run them before submitting a PR:

```bash
# Format code
black marketo_api/ tests/

# Lint
ruff check marketo_api/ tests/

# Type check
mypy marketo_api/
```

## Pull Request Guidelines

- Create a feature branch from `main`
- Write tests for new functionality
- Ensure all tests pass
- Update documentation (README, docstrings) if behavior changes
- Keep PRs focused — one feature or fix per PR

## Adding a New API Resource

1. Create a new file in `marketo_api/resources/` (e.g., `emails.py`)
2. Inherit from `BaseResource`
3. Register it in `marketo_api/resources/__init__.py`
4. Add it to the `MarketoClient` in `client.py`
5. Write tests in `tests/`
6. Add usage examples in `examples/`
7. Update the resource table in `README.md`

## Reporting Issues

When reporting bugs, please include:
- Python version
- Package version
- Marketo API endpoint involved
- Error message and traceback
- Minimal reproduction steps
