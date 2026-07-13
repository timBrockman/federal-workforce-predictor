# Use Cases & Why This Template Exists

federal-workforce-predictor is deliberately built as a **reference and teaching template**. Here are realistic scenarios where the patterns it demonstrates are valuable.

## 1. Internal Company Spend Coach

A finance team wants to give employees a private tool that suggests budget adjustments based on their own spending questionnaire plus (optionally) some team-level signals.

**Template value**:
- Strong consent model prevents using social signals without explicit user opt-in.
- Every recommendation explains exactly which data sources were used.
- The MCP interface lets an internal AI assistant (Claude, Cursor, custom agent) call the same safe tools.

## 2. Personal Finance AI Prototype / Demo

You want to quickly stand up a credible demo that shows "AI that respects privacy and can say no".

**Template value**:
- Works completely offline with local keys + Ollama.
- Demonstrates refusal behavior live (try unethical requests).
- The verify script gives you an instant "it actually works" story for stakeholders.

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

The goal is not that you ship customer-spend-api as-is, but that you can confidently lift the patterns (especially the ethics + principal + transparency ones) into your real services.