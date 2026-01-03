# Contributing to Beacon

Thank you for your interest in contributing to Beacon!

## How to Contribute

1. **Report bugs** - Open an issue describing the problem
2. **Suggest features** - Open an issue with your proposal
3. **Submit fixes** - Fork, create a branch, and open a pull request

## Development Setup

```bash
git clone https://github.com/en-yao/beacon-eval
cd beacon-eval
pip install -e ".[dev]"
pre-commit install
```

## Running Tests

```bash
pytest
ruff check src/
mypy src/
```

## Pull Request Guidelines

- Keep changes focused and atomic
- Add tests for new functionality
- Ensure all tests pass before submitting
- Follow existing code style
- Update documentation as needed

## Code of Conduct

Be respectful and constructive in all interactions.
