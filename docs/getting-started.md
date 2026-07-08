# Getting Started

This guide gets you from zero to a working, authenticated call that demonstrates the key behaviors (consent, ethics, transparency).

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (strongly recommended)

```bash
uv --version
```

## 1. Install & Verify

```bash
git clone <your-fork-or-clone>
cd customer-spend-api
uv sync --extra dev
```

Run the project's recommended verification commands:

```bash
uv run python -m pytest -m "not slow" -q
uv run python scripts/verify.py
```

You should see green tests and `✅ All verifications passed!`.

## 2. Seed Demo Data (Recommended)

```bash
uv run python scripts/seed_demo_data.py
```

This creates the `demo-user-123` with transactions, a questionnaire, and social consent.

## 3. Local Development Server

```bash
uv run uvicorn app.main:app --reload
```

Visit:
- http://localhost:8000/docs (Swagger)
- http://localhost:8000/graphql (GraphiQL)
- http://localhost:8000/explorer (minimal UI)

## 4. Get a Token & Make Calls

### Demo token (uses local keys — no network)

```bash
uv run python scripts/get_demo_token.py --user demo-user-123 --consent 2
```

Use the token in GraphiQL or curl.

### High-consent vs low-consent example

High consent (`consent=2`):

```bash
TOKEN=$(uv run python scripts/get_demo_token.py --consent 2)
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ recommendations { category suggestedMonthlyBudget ethicsNote dataSources } }"}' \
  http://localhost:8000/graphql
```

Low consent (`consent=0`):

```bash
LOW_TOKEN=$(uv run python scripts/get_demo_token.py --user low-c --consent 0)
# ... same curl with $LOW_TOKEN
```

You will see different `dataSources` and potentially degraded recommendations because of the ethics layer.

## 5. MCP (Optional but very interesting)

In a separate terminal:

```bash
uv run python -m app.services.mcp_server
```

Use any MCP client (Claude Desktop, inspector, or a small Python script) and call tools while passing `user_id` and `consent_level`:

```json
{
  "name": "get_budget_recommendations",
  "arguments": {
    "user_id": "demo-user-123",
    "consent_level": 2
  }
}
```

See [MCP Usage](usage/mcp.md) for details and why this is a notable part of the template.

## 6. One-Shot Verification (Your Friend)

Whenever you change something significant:

```bash
uv run python scripts/verify.py
```

It exercises the DB, auth, recommender + ethics, GraphQL, and both direct + stdio MCP paths.

## Next Steps

- Read the [Configuration Reference](configuration.md)
- Understand the core concepts in [Ethics & Consent](concepts/ethics-and-consent.md) and [Principal Model](concepts/principal-model.md)
- Try the [GraphQL Usage](usage/graphql.md) and [MCP Usage](usage/mcp.md) guides with real examples
- When you're ready to deploy: [Deployment](deployment/docker.md) and [Production](deployment/production.md)

Enjoy exploring the patterns!