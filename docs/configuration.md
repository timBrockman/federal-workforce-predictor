# Configuration Reference

federal-workforce-predictor uses `pydantic-settings` (12-factor style). All settings can be provided via environment variables or a `.env` file (case-insensitive).

Copy `.env.example` and adjust.

## Core Application

| Variable          | Default          | Description                                      | Production Notes |
|-------------------|------------------|--------------------------------------------------|------------------|
| `APP_NAME`        | `federal-workforce-predictor` | Service name used in health responses and logs   | - |
| `DEBUG`           | `false`          | Enables `/demo-token` endpoint and debug logging | **Never** true in prod |
| `LOG_LEVEL`       | `INFO`           | Logging level                                    | Use `INFO` or `WARNING` in prod |

## Database

Designed for easy swap (see [Production](deployment/production.md)).

| Variable              | Default                              | Description |
|-----------------------|--------------------------------------|-----------|
| `DATABASE_URL`        | `sqlite+aiosqlite:///./data/spend.db` | Full async SQLAlchemy URL. Use `postgresql+asyncpg://...` for Postgres. |
| `DB_POOL_SIZE`        | 5 | Base pool size |
| `DB_MAX_OVERFLOW`     | 10 | Extra connections allowed |
| `DB_POOL_TIMEOUT`     | 30 | Seconds to wait for a connection |
| `DB_POOL_RECYCLE`     | 1800 | Recycle connections after N seconds |
| `DB_POOL_PRE_PING`    | true | Test connections before use (highly recommended) |

**Alembic note**: Use `uv run alembic upgrade head` for production migrations. `init_db()` (create_all) is only for zero-config dev/CI.

See `alembic/env.py` for how async driver prefixes are stripped for migrations.

## Authentication & Authorization

Hybrid model: excellent offline experience + real IdP support.

| Variable                | Default | Description |
|-------------------------|---------|-----------|
| `USE_LOCAL_TEST_KEYS`   | `true` | Use generated RSA keys (never hits network). Set `false` for real JWKS. |
| `AUTH_JWKS_URL`         | (none) | Real JWKS endpoint when not using local keys |
| `AUTH_ISSUER`           | `https://example.auth0.com/` | Expected `iss` claim |
| `AUTH_AUDIENCE`         | `https://api.federal-workforce-predictor.example.com` | Expected `aud` claim |
| `AUTH0_CLIENT_ID`       | (none) | For `/demo-token?client_id=...` real exchange |
| `AUTH0_CLIENT_SECRET`   | (none) | |
| `AUTH0_TOKEN_URL`       | (none) | e.g. `https://your-tenant.auth0.com/oauth/token` |

**Principal model** (what your code receives):
- `user_id`
- `scopes`
- `consent_level` (0 = none, 1 = basic, 2+ = social allowed)
- `has_consent_for_social()`

See [Principal Model](concepts/principal-model.md) and [Auth](usage/auth.md).

## LLM / Agent

| Variable               | Default            | Description |
|------------------------|--------------------|-----------|
| `LLM_MODEL`            | `ollama/llama3.2`  | LiteLLM-compatible string. Change to `gpt-4o-mini`, `anthropic/...`, etc. |
| `LLM_TIMEOUT_SECONDS`  | 30 | |
| `LLM_MAX_TOKENS`       | 800 | |

The current agent is a **deterministic simulation** for the template (see code comment in `agent.py`). Real Pydantic AI + LiteLLM tools is the intended replacement path.

## Rate Limiting

| Variable                 | Default | Notes |
|--------------------------|---------|-------|
| `RATE_LIMIT_PER_MINUTE`  | 60 | |
| `RATE_LIMIT_BURST`       | 10 | |

Implemented via `slowapi`.

## Ethics & Domain Flags

| Variable                        | Default | Ethics / Behavior Impact |
|---------------------------------|---------|--------------------------|
| `REQUIRE_CONSENT_FOR_SOCIAL`    | `true` | When true, `consent_level < 2` causes synthetic social signals to be excluded and may degrade recommendations. |
| `ENABLE_SYNTHETIC_SOCIAL`       | `true` | Master switch for the synthetic social provider. |
| `MAX_RECOMMENDATION_CATEGORIES` | 8 | Safety bound |

All outputs from recommender and agent **must** declare `data_sources` and go through `EthicalPolicy`.

See [Ethics & Consent](concepts/ethics-and-consent.md).

## GraphQL Safety

| Variable                     | Default | Purpose |
|------------------------------|---------|---------|
| `GRAPHQL_MAX_QUERY_DEPTH`    | 3 | Hard limit on nesting (flat schema makes this very effective) |
| `GRAPHQL_MAX_QUERY_COST`     | 50 | Simple cost calculation in `QueryLimitExtension` |

Queries that exceed limits are rejected **before** resolvers run.

## MCP

| Variable      | Default | Notes |
|---------------|---------|-------|
| `MCP_ENABLED` | `true` | Currently only controls whether the module is importable in some paths. The stdio server is run separately. |

MCP tools accept `user_id` and `consent_level` in their `arguments` so that different principals can be exercised from MCP clients.

## Paths

| Variable   | Default     | Notes |
|------------|-------------|-------|
| `DATA_DIR` | `./data` | Created automatically. Used for SQLite and any future artifacts. |

## Environment Loading Order

1. Environment variables (highest priority)
2. `.env` file (in project root)
3. Defaults in `Settings`

Use `ENV_FILE=.env.production uv run ...` or just set variables in your platform (Docker, Kubernetes, etc.).

## Example Minimal Production-ish .env

```env
DEBUG=false
USE_LOCAL_TEST_KEYS=false
AUTH_JWKS_URL=https://your-tenant.auth0.com/.well-known/jwks.json
AUTH_ISSUER=https://your-tenant.auth0.com/
AUTH_AUDIENCE=https://api.federal-workforce-predictor.example.com
AUTH0_CLIENT_ID=...
AUTH0_CLIENT_SECRET=...
AUTH0_TOKEN_URL=https://your-tenant.auth0.com/oauth/token

DATABASE_URL=postgresql+asyncpg://user:pass@db:5432/spend
LLM_MODEL=gpt-4o-mini

RATE_LIMIT_PER_MINUTE=120
```

See the deployment guides for full production setup.

## Verification Tip

After changing config, always run:

```bash
uv run python scripts/verify.py
```

This is the fastest way to see the effect of consent flags, DB URL, etc. on the whole system.