# MCP Usage

## Listing Tools

```python
from app.services.mcp_server import list_tools
tools = await list_tools()
for t in tools:
    print(t.name, t.inputSchema)
```

Or via stdio client (any MCP host).

Current tools:
- `get_spend_summary`
- `get_budget_recommendations`
- `ask_budget_agent`

## Calling Tools with Principal Context

All tools accept optional `user_id` and `consent_level` in the arguments object.

### Direct (in-process)

```python
from app.services.mcp_server import call_tool

# Default (demo user, full consent)
res = await call_tool("get_budget_recommendations", {})

# Explicit low-consent user
res = await call_tool("get_budget_recommendations", {
    "user_id": "user-xyz",
    "consent_level": 0
})
```

### Via stdio MCP client

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

server_params = StdioServerParameters(
    command="uv", args=["run", "python", "-m", "app.services.mcp_server"]
)

async with stdio_client(server_params) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool(
            "ask_budget_agent",
            {"question": "How much should I budget for coffee?", "consent_level": 1}
        )
        print(result.content[0].text)
```

The server will build a `Principal` from the provided values (falling back to the safe demo user when omitted).

## Response Shape

Successful recommendation responses include:
- `recommendations`
- `ethical_note`
- `allowed`
- `user_id`
- `consent_level`

Refusals include `error`, `allowed: false`, and the reason.

See the ethics layer for exact behavior.

## Important Notes

- There is no transport-level auth on stdio. The caller is responsible for sending the correct `user_id`/`consent_level`.
- The same `EthicalPolicy` and persistence logic is used as the GraphQL path.
- This is one of the template's more interesting demonstrations — see [MCP Integration](../concepts/mcp-integration.md) and [Principal Model](../concepts/principal-model.md).

## Testing

The project's `scripts/verify.py` and `tests/test_mcp.py` exercise both direct calls and full stdio client usage with different principals.