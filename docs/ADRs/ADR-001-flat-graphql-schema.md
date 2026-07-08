# ADR-001: Deliberately Flat & Limited GraphQL Schema

## Status

Accepted

## Context

GraphQL is extremely powerful but also easy to abuse (deep nesting, expensive joins, N+1, denial of service via complexity).

We wanted the flexibility of a single endpoint and strong typing without the classic operational risks.

## Decision

- Use Strawberry GraphQL.
- Schema is intentionally **flat** (no deep relationships exposed).
- Hard limits: `graphql_max_query_depth=3`, custom cost limiter + Strawberry's `QueryDepthLimiter`.
- All protected fields require an authenticated `Principal`.
- Errors for auth failures use structured `extensions: { "code": "UNAUTHENTICATED" }`.

## Consequences

**Positive**
- Very hard to write accidentally expensive queries.
- Resolvers stay simple (no dataloaders needed for the current model).
- Easy to reason about and secure.
- Matches the "curated safe surface" philosophy also used for MCP.

**Negative**
- Clients may need more round-trips for richer views.
- Loses some of the "graph" appeal of GraphQL.

## Alternatives Considered

- Full nested schema with dataloaders + complexity analysis (more powerful but much more surface area to secure).
- REST + JSON:API (simpler rate limiting per route, but loses the single-endpoint DX that many AI/agent clients prefer).

## References

- `app/api/graphql/schema.py` (QueryLimitExtension + depth)
- `app/api/graphql/types.py` (flat types only)
- GraphQL best practices around depth/cost limiting.