# federal-workforce-predictor

**Reference implementation** of an ethics-first federal workforce / talent predictor (employee lifecycle & critical role readiness) microservice / template.

> **Important Disclaimer**  
> This is a learning reference and demonstration of patterns only. It is **not** a FedRAMP authorized system, does not constitute an ATO, and should not be used with real PII, CUI, or in production environments without significant additional review, testing, and authorization. Always verify the latest FedRAMP, NIST AI RMF, and DoD IL requirements for your use case.

This project demonstrates real patterns used in production AI systems:

- Consent-aware authentication (Principal model) that flows consistently to GraphQL **and** MCP tools.
- First-class ethics (refusal, source attribution, decision auditing, synthetic data only).
- Deliberately constrained GraphQL to avoid common pitfalls.
- Async SQLAlchemy + Alembic for easy production DB swaps.
- Curated MCP exposure of the same safe, guarded capabilities.
- Offline-first development with realistic Auth0/Keycloak paths.

It is intentionally a **reference implementation and educational template**, not a complete drop-in production application.

## Quick Links

- [Getting Started](getting-started.md) — 5-minute clone & run
- [Architecture](architecture.md)
- [Use Cases](use-cases.md)
- [Concepts](concepts/ethics-and-consent.md)
- [Compliance & Deployment Guidance](compliance/nist-ai-rmf-crosswalk.md)
- [Threat Models (STRIDE-AI + OWASP + ATLAS)](threat-models/STRIDE-AI-initial.md)
- [Usage](usage/graphql.md)

## Browse the Full Documentation

All documentation lives in the [`docs/` folder](https://github.com/timBrockman/federal-workforce-predictor/tree/master/docs) of the repository. This site is generated directly from that folder using GitHub Pages (out-of-the-box Jekyll).

See the [GitHub repository](https://github.com/timBrockman/federal-workforce-predictor) for the source code, issues, and to use this as a template.

## Key Features

See the [README](https://github.com/timBrockman/federal-workforce-predictor) for the complete feature list.