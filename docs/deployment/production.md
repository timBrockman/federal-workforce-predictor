# Production Deployment

## Database

### Recommended: PostgreSQL

Change `DATABASE_URL` and run migrations:

```bash
# In your production environment
DATABASE_URL=postgresql+asyncpg://... uv run alembic upgrade head
```

The app will continue to use `create_all` on startup for convenience (dev/CI), but you should use Alembic for real deploys.

**Important gotcha for first migration:**
- If tables were previously created by `create_all` or `seed_demo_data.py`, `alembic upgrade head` may fail with "table already exists".
- Solutions:
  1. Delete the DB file and run `alembic upgrade head` (recommended for clean start).
  2. Or run `uv run alembic stamp head` to mark the current state as up-to-date, then future upgrades will work.

See `alembic/env.py` — it automatically strips `+asyncpg` / `+aiosqlite` for migration connections.

Always run migrations as a separate step in production deploys before starting the app.

### Connection Pooling

Settings are exposed and used even for SQLite. Tune via `DB_*` variables.

For Postgres in high load:
- Increase pool size
- Use a connection pooler (PgBouncer) in front if needed
- Enable `pool_pre_ping`

## Running the Server

Use uvicorn with production settings:

```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --proxy-headers \
  --forwarded-allow-ips='*'
```

Or use the Dockerfile (multi-stage, non-root).

## Environment

- Set `DEBUG=false`
- Set `USE_LOCAL_TEST_KEYS=false`
- Provide real `AUTH_JWKS_URL`, `AUTH_ISSUER`, `AUTH_AUDIENCE`
- Provide secrets via platform (never commit)
- Consider `LOG_LEVEL=WARNING`

## Health & Readiness

- `/health` — basic liveness
- `/ready` — currently same; extend if you add external dependencies (DB ping, etc.)

## Rate Limiting

Tune `RATE_LIMIT_PER_MINUTE` and `RATE_LIMIT_BURST`.

In high-traffic scenarios consider:
- Per-principal limits (already possible via the limiter)
- Distributed rate limiting (Redis backend for slowapi)

## Observability

The app uses structlog (if configured) and standard logging.

Add:
- Prometheus via `prometheus-fastapi-instrumentator`
- Tracing (OpenTelemetry)
- Structured logs with request id

## Secrets

- Auth client secrets
- LLM API keys
- Database credentials

Use your platform's secret manager. The `get_token_via_client_credentials` helper only runs when explicitly called with real credentials.

## Migrations in CI/CD

Typical flow:
1. Build image
2. Run migration job: `uv run alembic upgrade head` against prod DB
3. Deploy app containers

Never rely only on `init_db()` in production.

## Monitoring Ethics

If you enabled persistence, query the `ethical_decision_logs` table for audit and compliance.

Add alerts on high refusal rates or unexpected decision patterns.

## Related

- [Docker](docker.md)
- [Auth Providers](auth-providers.md)
- [Productionizing](../productionizing.md)