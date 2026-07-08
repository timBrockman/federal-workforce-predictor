# Scripts

## scripts/verify.py

**The single most important command for this template.**

```bash
uv run python scripts/verify.py
```

It exercises end-to-end:
- DB + repositories
- Auth + demo tokens
- Recommender + ethics policy
- GraphQL (via TestClient with overrides)
- MCP (direct calls + full stdio client spawn)

Always run this after changes. It should end with `✅ All verifications passed!`

## scripts/seed_demo_data.py

Populates the demo user with transactions, questionnaire, and consent record.

```bash
uv run python scripts/seed_demo_data.py
```

Idempotent-ish (checks for existing data in some places). Useful before manual exploration or when the DB has been reset.

## scripts/get_demo_token.py

Mint a local test JWT.

```bash
uv run python scripts/get_demo_token.py --user demo-user-123 --consent 2
```

Flags:
- `--user` (default: demo-user-123)
- `--consent` (default: 2)

Output is the raw JWT (useful for piping to files or curl).

## When to Use Each

- Developing / changing code → `verify.py`
- Wanting realistic data for manual testing → `seed_demo_data.py`
- Need a token for curl / GraphiQL / Postman → `get_demo_token.py`
- Testing different consent levels → vary the `--consent` flag

## Running with Custom DB

```bash
DATABASE_URL=sqlite+aiosqlite:///./data/test.db uv run python scripts/verify.py
```

## Integration in CI

These scripts are designed to be fast and deterministic. You can add them directly to your CI pipeline after `uv sync --extra dev`.

See the root `plan.md` "Verification Requirements" section for the full list of checks that should stay green.