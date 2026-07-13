# Getting Started

This guide gets you from zero to a working, authenticated call that demonstrates the key behaviors (consent, ethics, transparency) using the primary federal workforce paths (submit assessment → career recommendations).

> **Warning**: This is a reference implementation for educational purposes. Do not use with real sensitive data or in any production/federal environment without your own security review and authorizations.

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (strongly recommended)

```bash
uv --version
```

## 1. Install & Verify

```bash
git clone <your-fork-or-clone>
cd federal-workforce-predictor
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

This creates the `demo-user-123` with an EmployeeAssessment (skills, goals, consent), synthetic career signals, plus legacy transactions/questionnaire for reference.

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

### High-consent vs low-consent example (primary federal path)

High consent (`consent=2`):

```bash
TOKEN=$(uv run python scripts/get_demo_token.py --consent 2)
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"{ careerRecommendations { recommendationType targetRole confidence rationale dataSources ethicsNote } }"}' \
  http://localhost:8000/graphql
```

Submit an assessment (updates recommendations for the user):

```bash
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"query":"mutation { submitAssessment(input: {skillsInventory: \"python,cloud,cyber\", performanceLevel: \"high\", careerGoals: \"lead critical cyber mission\", consentForCareerModeling: true}) { success message } }"}' \
  http://localhost:8000/graphql
```

Low consent (`consent=0`):

```bash
LOW_TOKEN=$(uv run python scripts/get_demo_token.py --user low-c --consent 0)
# ... same careerRecommendations query with $LOW_TOKEN (sources degraded or limited)
```

You will see different `dataSources` and potentially degraded (or refused) career recommendations because of the ethics/consent layer. Legacy spend queries still work for reference.

## 5. MCP (Optional but very interesting)

In a separate terminal:

```bash
uv run python -m app.services.mcp_server
```

Use any MCP client (Claude Desktop, inspector, or a small Python script) and call tools while passing `user_id` and `consent_level`:

Primary federal example:

```json
{
  "name": "get_career_recommendations",
  "arguments": {
    "user_id": "demo-user-123",
    "consent_level": 2
  }
}
```

Or submit first:

```json
{
  "name": "submit_assessment",
  "arguments": {
    "skills_inventory": "python,cloud,cyber",
    "performance_level": "high",
    "career_goals": "lead critical cyber mission",
    "consent_for_career_modeling": true,
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