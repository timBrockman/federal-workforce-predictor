# Architecture Overview

federal-workforce-predictor is deliberately layered so that ethics, consent, and identity are impossible to bypass.

## High-Level Flow (User submits assessment → gets career recommendations)

```
Client (GraphQL or MCP)
    │
    ▼
Auth → Principal (user_id + consent_level + scopes)
    │
    ▼
GraphQL Resolver / MCP Tool Handler
    │
    ▼
Service Layer (recommender / agent / summary)
    │
    ├─► EthicalPolicy.check_*
    │       │
    │       ▼
    │   Decision (allowed / reason / sources)
    │       │
    │       ▼
    │   persist_decision (best effort to DB)
    │
    ▼
Repositories (async SQLAlchemy)
    │
    ▼
Response with declared dataSources + ethicsNote
```

## Key Components

- **Principal** (`app/core/security.py`): The single source of truth for who is calling and what they consented to.
- **EthicalPolicy** (`app/core/ethics.py`): Pure decision logic. Easy to test, easy to audit.
- **Services** (`app/services/`): Recommender, Agent (simulated), thin wrappers.
- **GraphQL** (`app/api/graphql/`): Very flat schema + guard extensions.
- **MCP** (`app/services/mcp_server.py`): Reuses the identical services. Accepts principal context via arguments.
- **DB** (`app/db/`): Models + repositories + Alembic.
- **Config** (`app/core/config.py`): Everything 12-factor.

## Cross-Cutting Concerns

- Consent travels with the request, not inferred from user history.
- All outputs declare sources.
- Refusals are explicit and logged.
- Limits and rate limiting are applied early.

See the individual concept docs and ADRs for the "why" behind each major decision.
