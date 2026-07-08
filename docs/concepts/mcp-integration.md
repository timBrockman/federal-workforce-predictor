# MCP Integration

customer-spend-microservice includes a lightweight MCP server (using the official `mcp` Python SDK) that exposes a **curated, safe subset** of the same capabilities available through GraphQL.

## Why MCP?

MCP lets other AI agents and tools discover and call your service's capabilities in a standardized way. By exposing only the guarded operations, you get the benefits of agent interoperability without opening dangerous or unaudited paths.

## The Three Tools

- `get_spend_summary` — DB-backed aggregates for a user.
- `get_budget_recommendations` — ethics-aware recommendations.
- `ask_budget_agent` — conversational access (currently simulated).

All three tools are backed by the **exact same service layer** used by GraphQL.

## Passing Identity & Consent (The Interesting Part)

Because MCP stdio does not carry HTTP Authorization headers, identity is passed **per call** via tool arguments:

```json
{
  "user_id": "demo-user-123",
  "consent_level": 2
}
```

See `_principal_from_args` in `app/services/mcp_server.py`. The server builds a `Principal` from these values on every call.

This design lets an external MCP client (Claude, Cursor, a custom agent, etc.) act on behalf of different users or with different consent levels — while still going through the full ethics checks.

## Running the Server

Standalone (stdio):

```bash
uv run python -m app.services.mcp_server
```

In-process (used by `verify.py` and tests):

```python
from app.services.mcp_server import list_tools, call_tool

tools = await list_tools()
result = await call_tool("get_budget_recommendations", {"consent_level": 0})
```

## Ethics & Transparency

The same `EthicalPolicy` and `persist_decision` paths are used. Responses include `ethical_note`, `data_sources` (when successful), or clear refusal reasons.

## Security Model for MCP

- No automatic auth from the transport.
- Trust boundary is the MCP client + the arguments it sends.
- In production you would typically run the MCP server in a context where the calling agent has already been authorized to act for a specific principal, or you would add an additional lightweight auth mechanism on top of the tool arguments.

The template demonstrates the clean "principal per call" pattern that works today with stdio MCP clients.

See also:
- [Principal Model](principal-model.md)
- [MCP Usage](usage/mcp.md)
- `app/services/mcp_server.py` (tool schemas + `_principal_from_args`)