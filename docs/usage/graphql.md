# GraphQL Usage

## Endpoint

`POST /graphql`

Content-Type: `application/json`

Body:
```json
{ "query": "..." }
```

Authentication: `Authorization: Bearer <token>` header (required for data queries).

## Available Operations

### Queries

- `health` → simple string (no auth)
- `spendSummary { totalSpent topCategories month }`
- `recommendations(incomeBracket: String) { ... }`
- `askAgent(question: String!) { answer sourcesUsed ethicalDecision followUpQuestions }`

### Mutation

- `submitQuestionnaire(input: QuestionnaireInput!) { success message }`

Full type definitions are in the GraphiQL explorer or `app/api/graphql/types.py`.

## Authentication & Errors

Protected fields return structured errors:

```json
{
  "data": null,
  "errors": [{
    "message": "Not authenticated",
    "extensions": { "code": "UNAUTHENTICATED" }
  }]
}
```

See [Auth](auth.md) for how to obtain tokens with different `consent_level` values.

## Limits & Safety

- Max depth: 3 (configurable via `GRAPHQL_MAX_QUERY_DEPTH`)
- Custom cost limiter (see `QueryLimitExtension`)
- Queries that are too deep or expensive are rejected before resolvers.

Example rejection:
```json
{ "errors": [{ "message": "Query too deep (max depth 3)" }] }
```

## Example Queries

### Spend summary (high consent token)

```graphql
{
  spendSummary {
    totalSpent
    topCategories
    month
  }
}
```

### Recommendations with consent variation

Low consent produces different `dataSources` and may have fewer/ different recommendations.

See the quickstart in README or [Getting Started](../getting-started.md).

## Using from Code (Python example)

```python
import httpx

query = "{ recommendations { category suggestedMonthlyBudget ethicsNote dataSources } }"

r = httpx.post(
    "http://localhost:8000/graphql",
    json={"query": query},
    headers={"Authorization": f"Bearer {token}"}
)
print(r.json())
```

## GraphiQL

Available at `/graphql`. Paste token in the "Authorization" header section if needed.

## Error Extensions

customer-spend-microservice uses `extensions.code` for machine-readable error types (e.g. `UNAUTHENTICATED`).

Clients should check `errors[].extensions.code` rather than string matching messages.

## Related

- [Limited GraphQL](../concepts/limited-graphql.md)
- [Configuration](../configuration.md) for limit settings
- Tests: `tests/test_graphql.py`