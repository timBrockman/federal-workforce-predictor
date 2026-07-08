# Contributing to customer-spend-api

Thank you for your interest in contributing!

This is a **reference implementation / educational template**. Contributions that improve clarity, correctness, documentation, tests, or the "how to extend" experience are very welcome.

## Development Setup

```bash
git clone https://github.com/timBrockman/customer-spend-api.git
cd customer-spend-api
uv sync --extra dev
uv run pre-commit install
```

## Running Tests & Verification

```bash
uv run python -m pytest -m "not slow"
uv run python scripts/verify.py
```

Always run the verification script before opening a PR.

## Code Style

- Ruff + ruff-format (enforced via pre-commit)
- mypy (strict)
- Follow existing patterns for ethics, Principal, and source attribution.

## Pull Requests

1. Fork + create feature branch.
2. Make focused changes.
3. Add/update tests and docs.
4. Run full verification.
5. Open PR with clear description (what + why).

## Reporting Issues

Use the GitHub issue templates. Please include:
- Steps to reproduce
- Expected vs actual behavior
- Relevant config / consent_level

## License

By contributing, you agree that your contributions will be licensed under the MIT License (see LICENSE file).
