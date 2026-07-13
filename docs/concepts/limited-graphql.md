# Limited GraphQL Schema

## Rationale

GraphQL is powerful but can be dangerous if the schema allows arbitrary nesting or expensive queries. Clients (or malicious actors) can easily craft queries that cause deep recursion, N+1 problems, or massive data fetches.

federal-workforce-predictor deliberately uses a **flat schema** with strict guardrails (career_recommendations, submit_assessment first).

## Design Decisions

- Only top-level fields (new primary first): `health`, `careerRecommendations`, `submitAssessment`, `askAgent` (+ legacy spend fields).
- Mutation: `submitQuestionnaire`.
- No deep nesting of related objects.
- Types are simple value objects (see `app/api/graphql/types.py`).

## Safety Mechanisms

1. **QueryDepthLimiter** (from Strawberry) + custom `QueryLimitExtension` in `schema.py`.
   - `graphql_max_query_depth`: 3 (configurable)
   - Custom cost calculation that walks the document AST.
   - Queries exceeding limits are rejected early with clear GraphQLError.

2. **Authentication required** for all data fields. Unauthenticated requests return:
   ```json
   { "errors": [{ "message": "Not authenticated", "extensions": { "code": "UNAUTHENTICATED" } }] }
   ```

3. **Flat by design** — resolvers do simple DB aggregates or service calls. No joins or nested resolvers that could explode.

## Trade-offs

**Benefits**:
- Easy to reason about performance and security.
- Aligns with the "curated safe surface" philosophy (same as MCP tools).
- Works well with AI agents that might generate queries.

**Costs**:
- Clients may need multiple round-trips for complex views.
- Less "graph-like" than a fully relational schema.

This is intentional. See ADR-001 for more context.

## Enforcement in Code

See:
- `app/api/graphql/schema.py` (QueryLimitExtension + on_execute)
- `pyproject.toml` (pytest filter for extension deprecation warning)
- Tests in `tests/test_graphql.py` (depth limit test)

## Recommendations for Extension

When adding new fields:
- Keep them flat or very shallow.
- Apply the same auth + ethics checks.
- Update max depth/cost if needed, but prefer adding new top-level queries over nesting.
- Document the new field in `docs/usage/graphql.md`.

## Related Reading

- [MCP Integration](../concepts/mcp-integration.md) — same "safe curated" approach.
- [Productionizing](../productionizing.md) — rate limiting and other guards.