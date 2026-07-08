# ADR-004: Ethics Decisions as First-Class Logged Objects

## Status

Accepted

## Context

Many AI systems hide decision logic inside prompts or scattered if-statements. This makes auditing, debugging, and compliance nearly impossible.

## Decision

Every recommendation and agent response produces an `EthicalDecision` dataclass that is:
- Logged via `log_decision`
- Optionally persisted via `persist_decision` → `EthicsLogRepository`

The object contains:
- decision_type
- allowed
- reason
- data_sources
- classification
- metadata

## Consequences

**Positive**
- Clear audit trail
- Easy to unit test ethics rules
- Can be extended with retention, export, "forget me" later
- Same objects used in GraphQL responses, MCP, and logs

**Costs**
- Slightly more code than just returning strings
- Need to keep the in-memory logger and DB path in sync during development

## References

- `app/core/ethics.py`
- `app/db/models.py` (EthicalDecisionLog)
- `app/db/repositories.py` (EthicsLogRepository)
- Multiple places calling `persist_decision`