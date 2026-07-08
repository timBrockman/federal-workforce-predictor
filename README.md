# customer-spend-microservice

**Reference implementation** of an ethics-first customer spend intelligence microservice / template.

This project demonstrates real patterns used in production AI systems:
- Consent-aware authentication (Principal model) that flows consistently to GraphQL **and** MCP tools.
- First-class ethics (refusal, source attribution, decision auditing, synthetic data only).
- Deliberately constrained GraphQL to avoid common pitfalls.
- Async SQLAlchemy + Alembic for easy production DB swaps.
- Curated MCP exposure of the same safe, guarded capabilities.
- Offline-first development with realistic Auth0/Keycloak paths.

It is intentionally a **reference implementation and educational template**, not a complete drop-in production application.

## Key Features (Current State)

- **FastAPI + Strawberry GraphQL** — flat schema (`spendSummary`, `recommendations`, `askAgent`, `submitQuestionnaire`) + depth/cost limiting + structured error extensions (e.g. `UNAUTHENTICATED`).
- **MCP Server** (official SDK, stdio) — three curated tools. Tools accept optional `user_id` + `consent_level` so callers can exercise different principals.
- **Async DB** — SQLAlchemy 2.0 + explicit pooling + full Alembic migrations (initial schema included).
- **Ethics as code** — `EthicalPolicy`, consent gating, refusal, source transparency, `persist_decision` to `EthicalDecisionLog`.
- **Auth** — Auth0/Keycloak via JWT + client credentials. Excellent offline support with local RSA test keys + `create_demo_token`. Real exchange helper available.
- **Agent** — Guardrailed but intentionally a rules-based simulation for determinism and zero cost in the template (easy to replace with real Pydantic AI).
- **Recommender** — questionnaire + synthetic social signals with mandatory ethics checks.
- **Production touches** — rate limiting (slowapi), CORS, health/readiness, lifespan seeding, 12-factor config.
- **Testing** — comprehensive (auth matrix, ethics cases, repo isolation, MCP direct + stdio, GraphQL safety).

**Deliberate limits** (by design):
- GraphQL is flat (no deep nesting).
- Social data is always synthetic/mocked.
- Agent is a simulation (see "Extending" docs).
- SQLite default (swap via `DATABASE_URL` + Alembic).

## Quickstart (5 minutes)

```bash
# 1. Setup
uv sync --extra dev

# 2. (Optional but recommended) Seed realistic demo data
uv run python scripts/seed_demo_data.py

# 3. Get a token (demo mode uses local keys — no network)
uv run python scripts/get_demo_token.py --user demo-user-123 --consent 2 > /tmp/token.txt
TOKEN=$(cat /tmp/token.txt)

# 4. Start the server (Terminal 1)
uv run uvicorn app.main:app --reload
```

In another terminal or via curl / GraphiQL:

```bash
# Basic authenticated call (high consent)
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ recommendations { category suggestedMonthlyBudget ethicsNote dataSources } }"}' \
  http://localhost:8000/graphql

# Low-consent variation (different behavior)
LOW_TOKEN=$(uv run python scripts/get_demo_token.py --user low-consent --consent 0)
curl -H "Authorization: Bearer $LOW_TOKEN" ...  # see ethics degradation
```

### Explore the UI
- Swagger: http://localhost:8000/docs
- GraphiQL: http://localhost:8000/graphql
- Minimal explorer: http://localhost:8000/explorer
- Debug token (when DEBUG=true): http://localhost:8000/demo-token

### MCP (separate process)

```bash
uv run python -m app.services.mcp_server
```

Connect any MCP client. Example tool call with explicit principal context:

```json
{"name": "get_budget_recommendations", "arguments": {"user_id": "demo-user-123", "consent_level": 2}}
```

See `docs/usage/mcp.md` for full details.

### One-shot verification (highly recommended)

```bash
uv run python scripts/verify.py
```

This exercises DB, auth, recommender, ethics, GraphQL, and MCP (direct + stdio) end-to-end.

## Documentation

This README gets you running. For depth, see the `docs/` folder:

- [Getting Started](docs/getting-started.md)
- [Configuration Reference](docs/configuration.md) (every env var + ethics impact)
- **Concepts**
  - [Ethics & Consent](docs/concepts/ethics-and-consent.md)
  - [Principal Model (incl. MCP threading)](docs/concepts/principal-model.md)
  - [Limited GraphQL](docs/concepts/limited-graphql.md)
  - [MCP Integration](docs/concepts/mcp-integration.md)
  - [Synthetic Data](docs/concepts/synthetic-data.md)
- **Usage**
  - [GraphQL](docs/usage/graphql.md)
  - [MCP Tools & Principal Args](docs/usage/mcp.md)
  - [Auth & Tokens](docs/usage/auth.md)
- **Deployment & Production**
  - [Docker](docs/deployment/docker.md)
  - [Production](docs/deployment/production.md) (Alembic, Postgres, secrets, uvicorn)
  - [Auth Providers](docs/deployment/auth-providers.md)
- [Use Cases](docs/use-cases.md)
- [Extending the Template](docs/extending/) (recipes)
- [Architecture + ADRs](docs/architecture.md) (and `docs/ADRs/`)
- [Productionizing Checklist](docs/productionizing.md)

## Running the Tests

```bash
uv run pytest -q -m "not slow"
uv run python scripts/verify.py
```

See `docs/usage/scripts.md` and the internal `plan.md` for the full verification story.

## Architecture in One Minute

Every request carries a `Principal` (user_id + scopes + `consent_level`).

Services (recommender, agent, summary) **always** go through `EthicalPolicy`.

Outputs declare `dataSources` and ethical decisions can be persisted.

GraphQL is deliberately flat + guarded. MCP reuses the exact same service + ethics + principal logic (via tool arguments).

See `docs/concepts/` and `docs/architecture.md`.

## Known Limitations (Honest)

- The agent is a simulation (rules + recs) for determinism and zero cost. Real Pydantic AI + tools is straightforward to add (see extending docs).
- SQLite by default (fine for template/dev; use Alembic + Postgres for real load).
- No real social data (synthetic only — this is a deliberate ethics choice).
- JWKS path for production IdP is present but the "cached fetch" is left as a small exercise.

These are documented trade-offs, not oversights.

## License / Use

Intended as a **high-quality reference and starting point**. Copy the patterns (ethics engine, principal threading to MCP, limited GraphQL, consent model, Alembic + async SQLA, offline auth) into your own services.

See the use cases and extending docs for inspiration.

---

**Next step**: Follow the quickstart above, then read [Getting Started](docs/getting-started.md) and [Configuration](docs/configuration.md).