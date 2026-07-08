# Ethics & Consent

Ethics is not an afterthought or a prompt — it is a first-class, enforceable part of the system.

## Core Ideas

1. **Principal carries consent** — `consent_level` travels with the authenticated identity.
2. **Policy is code** — `EthicalPolicy` makes explicit decisions that are logged and (optionally) persisted.
3. **Transparency is mandatory** — every recommendation and agent response declares the `dataSources` it used.
4. **Refusal is a valid outcome** — unethical requests are refused with a clear reason instead of trying to be helpful.

## Consent Levels (Current Model)

- Level 0/1 → synthetic social signals are excluded.
- Level 2+ → synthetic social signals may be used (if `enable_synthetic_social` is true).

The flag `require_consent_for_social` controls whether the check is enforced.

## Where Ethics Runs

- Recommender (`get_recommendations`)
- Agent (`ask_budget_agent`)
- Summary paths (indirectly via data access)
- Every MCP tool call

`persist_decision` is called in the main async paths so that an audit trail can be built.

## Refusal Examples

- Attempting to get the system to "target poor people" or use discriminatory criteria → immediate refusal.
- Requesting recommendations while lacking required consent → degraded or empty results + explanation.

## Testing Ethics

See `tests/test_security_ethics.py` and the ethics cases inside `test_mcp.py` and `test_graphql.py`.

The `scripts/verify.py` also exercises consent variation.

## Production Implications

- The in-memory log is only for the template. Use the `EthicalDecisionLog` model + repository in real deployments.
- You will likely want to add retention policies, export, and "right to be forgotten" flows on top of the decision log.
- All of this is much easier because the decisions are already explicit objects instead of buried in LLM prompts.

See also [Principal Model](principal-model.md) and the persisted decision code in `app/core/ethics.py`.