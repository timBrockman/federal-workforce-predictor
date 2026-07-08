# The Principal Model

One of the most useful patterns in customer-spend-microservice is the `Principal` that carries identity **and** consent information through every layer — GraphQL resolvers, services, recommender, agent, **and** MCP tools.

## Definition

```python
@dataclass
class Principal:
    user_id: str
    scopes: list[str]
    consent_level: int = 0
    ...
    def has_consent_for_social(self) -> bool: ...
```

`consent_level` semantics (current convention):
- 0 = no consent beyond basic profile
- 1 = basic questionnaire consent
- 2+ = social/synthetic signals allowed

The flag `require_consent_for_social` in settings controls whether level < 2 actually blocks synthetic data.

## How It Flows

1. Auth layer (`get_current_principal`) produces a `Principal` (or `None`).
2. GraphQL context passes it to every resolver.
3. Services (`get_recommendations`, `ask_budget_agent`, etc.) receive the principal and must consult `EthicalPolicy`.
4. **MCP** — this is the interesting bit. Because stdio MCP doesn't carry HTTP headers, we pass context **per tool call**:

   ```python
   # In mcp_server.py
   principal = _principal_from_args(arguments)  # user_id + consent_level
   ```

   Tool input schemas now document these optional fields. Callers (including other AI agents via MCP) can therefore request data on behalf of different users or with different consent levels.

This design lets the same ethics and data-source logic apply whether the caller came through GraphQL or an MCP client.

## Why This Matters (Educational Value)

Many AI service templates either:
- Hardcode a user, or
- Only support auth at the HTTP boundary.

By making `Principal` a first-class, serializable concept that reaches the MCP layer, customer-spend-microservice demonstrates how to keep authorization + consent consistent across multiple interfaces.

See:
- `app/core/security.py`
- `app/services/mcp_server.py` (`_principal_from_args`)
- [MCP Integration](mcp-integration.md)
- [Ethics & Consent](ethics-and-consent.md)

## Example Effect

Calling recommendations with `consent_level=0` vs `2` produces different `dataSources` and may return fewer (or ethically degraded) recommendations. This is intentional and logged.

## Extending

When you add a new service or MCP tool, always accept a `Principal` (or extract one from arguments in the MCP case) and pass it to the ethics layer. Never bypass it.

This single rule keeps the whole system auditable and consent-respecting.