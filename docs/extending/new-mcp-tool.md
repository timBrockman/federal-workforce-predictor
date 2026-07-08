# Recipe: Add a New MCP Tool

## Goal

Expose a new safe capability through the MCP server while keeping the same ethics and principal guarantees.

## Steps

1. **Add the tool definition**

In `app/services/mcp_server.py`, extend `list_tools`:

```python
Tool(
    name="get_monthly_spend_trend",
    description="...",
    inputSchema={
        "type": "object",
        "properties": {
            "user_id": {...},
            "consent_level": {...},
            "months": {"type": "integer"}
        }
    }
)
```

2. **Implement the handler**

In `call_tool`:

```python
elif name == "get_monthly_spend_trend":
    principal = _principal_from_args(arguments)
    months = arguments.get("months", 3)
    # call a service that takes principal
    result = await get_spend_trend(principal, months)
    return [TextContent(type="text", text=json.dumps(result))]
```

3. **Implement the backend**

Create (or extend) a service that accepts `Principal` and performs the ethics check.

4. **Wire ethics**

```python
decision = EthicalPolicy... 
log_decision(decision)
await persist_decision(decision)
```

5. **Tests**

Add to `tests/test_mcp.py`:
- Direct call with different consent
- Stdio client call

Update `scripts/verify.py` if you want it exercised in the smoke test.

6. **Docs**

- Update `docs/usage/mcp.md`
- Add to `docs/concepts/mcp-integration.md` if the pattern is new
- Mention in use-cases if relevant

## Important

MCP tools must never bypass the Principal or ethics layer. This is the whole point of the template.