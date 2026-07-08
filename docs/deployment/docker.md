# Docker & Container Deployment

## Dockerfile

The included `Dockerfile` is a standard multi-stage, non-root production image:

- Builder stage uses `uv` to install dependencies (no dev deps).
- Final stage runs as a non-root user.
- Exposes 8000.

Build:

```bash
docker build -t customer-spend-api .
```

Run:

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL=sqlite+aiosqlite:///./data/spend.db \
  -v $(pwd)/data:/app/data \
  customer-spend-api
```

## docker-compose.yml

A basic compose file is provided.

**Current limitation (as of this writing):**

The `keycloak-optional` service references `./docker/keycloak-realm.json`, but the `docker/` directory does not exist in the repository.

### Quick workaround (local testing)

1. Create the directory:
   ```bash
   mkdir -p docker
   ```

2. Either:
   - Remove or comment out the Keycloak service from `docker-compose.yml` for basic use, **or**
   - Provide a minimal realm file if you want the Keycloak profile.

Basic app only (recommended for first try):

```yaml
# docker-compose.override.yml or edit temporarily
services:
  app:
    build: .
    ports: ["8000:8000"]
    environment:
      - DEBUG=false
      - USE_LOCAL_TEST_KEYS=true
      - DATABASE_URL=sqlite+aiosqlite:///./data/spend.db
    volumes:
      - ./data:/app/data
```

Then:

```bash
docker compose up --build
```

## Volumes & Data

The container expects a writable `./data` directory for SQLite (or mount your Postgres volume).

For production, prefer a managed database and do **not** rely on the container's local SQLite.

## Health Checks

The image exposes:
- `GET /health`
- `GET /ready`

Use these in your orchestrator.

## Next Steps

See [Production](production.md) for running Alembic migrations inside or alongside the container, connecting to real Postgres, and proper secret handling.