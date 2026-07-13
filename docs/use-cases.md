# Use Cases & Why This Template Exists

federal-workforce-predictor is deliberately built as a **reference and teaching template**. Here are realistic scenarios where the patterns it demonstrates are valuable.

## 1. Federal Workforce / Critical Role Readiness Predictor

A mission owner or HR analytics team in a federal agency wants to assess employee skills, performance signals, and career goals (with explicit consent) to identify readiness for critical roles, skill gaps, or recommended development actions.

**Template value**:
- Consent_for_career_modeling flag + Principal levels gate use of synthetic signals; low consent degrades or refuses.
- Every career recommendation declares exact `data_sources` (assessment vs synthetic career signals) + `ethics_note`.
- Guardrailed agent supports queries like "skills needed for X mission" with the same ethics layer.
- MCP lets secure internal agents/tools call submit_assessment + career recs safely.

## 2. Talent & Employee Lifecycle Prototype (Agency Internal)

You want a fast, credible offline demo showing ethics-first AI for workforce planning that can say "no" on protected classes, high-stakes bias, or insufficient consent.

**Template value**:
- Works completely offline with local keys + Ollama.
- Demonstrates refusal + source transparency live.
- The verify script + seeded assessments give instant working federal flow for stakeholders.

## 3. Reference Implementation for "Ethics as Code"

You are teaching or advocating for embedding ethics/refusal logic directly in services instead of hoping prompts will be sufficient.

**Template value**:
- `EthicalPolicy` is a plain Python class — easy to audit and unit test.
- Decisions are first-class objects that can be logged and persisted.
- Consent is not a free-text field; it is a numeric level with clear semantics that affects behavior.

## 4. MCP-Enabled Capability Host

You are building (or evaluating) an agent platform and want to expose a small number of safe, well-guarded capabilities from an existing backend.

**Template value**:
- Shows how to thread a `Principal` (with consent) into MCP tool calls.
- The same business logic powers both the GraphQL API and the MCP surface.
- Tools are intentionally narrow and documented with input schemas.

## 5. Teaching Limited GraphQL + Production Patterns

You want a small but realistic codebase to teach:
- Why unconstrained GraphQL can be dangerous
- How to combine FastAPI + Strawberry + async SQLAlchemy + Alembic
- Modern auth with offline test support
- Rate limiting, health endpoints, structured config, Docker, etc.

**Template value**:
- Everything is intentionally small enough to read in an afternoon.
- The "flat schema + hard limits" decision is called out and explained.
- The code is the documentation for many production patterns.

## How to Use These

Pick the scenario closest to your need, then follow the corresponding "Extending" recipe or "Production" guide.

The goal is not that you ship federal-workforce-predictor as-is, but that you can confidently lift the patterns (especially the ethics + Principal + transparency + limited interfaces + audit logging) into your real federal or high-stakes services.