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

## Commit Policy (Mandatory)

This project uses **small, single-purpose commits and PRs** with a structured message format.

See **[docs/development/commit-conventions.md](docs/development/commit-conventions.md)** for the full policy.

Key points:
- One logical, reviewable change per commit.
- Run relevant tests + `scripts/verify.py` locally before committing.
- Every commit message (after policy introduction) **must** document:
  - Why / Context
  - Design decisions (including what was reused and why)
  - Tradeoffs considered
  - Verification performed
- PRs must also be small and focused.

Violations will be asked to be split before merge.

## Code Style

- Ruff + ruff-format (enforced via pre-commit)
- mypy (strict)
- Follow existing patterns for ethics, Principal, and source attribution.

## Pull Requests

1. Fork + create feature branch (small scope).
2. Make **focused, atomic changes** (one concern per commit).
3. Add/update tests and docs.
4. Run full verification.
5. Open PR with clear description that summarizes the structured commit bodies.

## Reporting Issues

Use the GitHub issue templates. Please include:
- Steps to reproduce
- Expected vs actual behavior
- Relevant config / consent_level

## License

By contributing, you agree that your contributions will be licensed under the MIT License (see LICENSE file).
