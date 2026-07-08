# ADR-003: Threading Principal (with Consent) into MCP Tools

## Status

Accepted

## Context

MCP (stdio) has no HTTP headers or session. Many implementations either skip auth or hardcode a user.

We wanted to demonstrate that identity + consent can still be passed cleanly even to stdio-based tool servers.

## Decision

- MCP tools accept `user_id` and `consent_level` in their `arguments`.
- `_principal_from_args` constructs a `Principal` on every call.
- The exact same services, `EthicalPolicy`, and `persist_decision` paths are used as GraphQL.

## Consequences

**Positive**
- External agents (Claude, etc.) can act on behalf of different users or with different consent.
- No duplication of business or ethics logic.
- Shows a realistic pattern for multi-interface AI services.

**Trade-offs**
- The MCP client is trusted to send the correct principal (transport-level auth is out of scope for this template).
- Slightly more verbose tool calls.

## Alternatives Considered

- Global / singleton principal (breaks multi-tenancy and consent)
- Separate MCP auth layer (adds complexity not needed for a reference template)
- Only expose unauthenticated safe tools (misses the point of consent-aware services)

## References

- `app/services/mcp_server.py`
- `docs/concepts/principal-model.md`
- `docs/usage/mcp.md`