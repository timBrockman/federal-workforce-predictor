# Recipe: Add a New Recommendation Path

## Goal

Add a new top-level recommendation category or strategy that still respects Principal, ethics, and source attribution.

## Steps

1. **Update the recommender**

In `app/services/recommender.py`, extend the rules or add a new function:

```python
def _compute_custom_category(principal, context):
    # your logic
    return {"category": "travel", "suggested...": 120.0, ...}
```

Make sure you attach `data_sources` and call `EthicalPolicy` (or reuse the existing decision).

2. **Expose in GraphQL**

Add to the `recommendations` resolver or create a new field if it makes sense.

Keep it flat.

3. **Expose via MCP**

Update the tool description and the `call_tool` handler in `mcp_server.py` if you want the new path available to agents.

Or simply let the existing `get_career_recommendations` (or legacy) return it.

4. **Tests**

- Add unit test in recommender with different consent levels.
- Add GraphQL test case.
- Add MCP test case passing explicit `consent_level`.

5. **Documentation**

- Update `docs/usage/graphql.md` and `docs/usage/mcp.md`
- Add example in use-cases if relevant
- Update ADR if this changes a core decision

## Example Commit Message

```
feat(recommender): add travel category with consent gating

- New logic only appears when consent_level >= 2
- Sources always declared
- Tests for both consent paths
```

## Keep the Spirit

Every new path must:
- Receive a `Principal`
- Go through `EthicalPolicy`
- Return explicit sources
- Be auditable (ideally call `persist_decision`)

This is what makes the template valuable as a reference.