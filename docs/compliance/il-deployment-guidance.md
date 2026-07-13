# IL Deployment Guidance (Skeleton)

**Status**: Initial placeholder. Expand with actual guidance for DoD Impact Levels.

## Overview
This app is designed as a reference for deploying ethics-first AI services into federal environments.

- **IL4 / FedRAMP Moderate baseline**: Current Docker + SQLite/Postgres + ethics layer can be adapted with FIPS endpoints, US-person notes. Good starting point for Moderate ATO.
- **IL5**: Requires GovCloud (or equivalent), FedRAMP High + DoD overlays, US persons for ops, separation of duties. Synthetic-only reference; real PII/CUI needs SC/AC/AU enhancements + immutable logs.
- **IL6**: Classified (SECRET), SIPRNet, dedicated infrastructure, cleared personnel. Not in scope for this public reference template.

## Key Considerations
- **Data classification & handling**: Extend Principal with sensitivity level (e.g. CUI, SBU). Synthetic data only in reference; real assessments require encryption at rest/transit (SC-8, SC-28), access control (AC-2, AC-3, AC-6), and minimization.
- **Supply chain & models**: Document/pin LLM providers (FedRAMP authorized where possible). Current agent is rules-based simulation to avoid live model risk in template. Use LiteLLM with verified endpoints.
- **Monitoring & audit**: Leverage EthicalDecisionLog + persist_decision (already wired in GraphQL/MCP/agent). Export logs for continuous monitoring (FedRAMP CA/CM). Support AU-2, AU-3, AU-6, AU-12.
- **Auth & identity**: Use Keycloak/Auth0 with proper IL overlays. Principal + consent must be preserved. Demo local keys for dev only.
- **Deployment artifacts**: Dockerfile + docker-compose for IL4 baseline. For IL5: add FIPS modules, network policies, non-root containers, signed images. Use Postgres + Alembic (not SQLite).
- **Ethics as control**: The built-in refusals for bias/protected classes, consent gating, and source attribution directly support risk management (NIST Map/Manage) and can map to AC, AU, SI controls.

See plan.md (MVP), expanded STRIDE-AI (7 threats), and NIST crosswalk for related controls.

**IL5/IL6 note**: This public repo provides patterns and guidance only. Real deployments require ATO, cleared personnel for IL6, and additional overlays (e.g. DoD 8500, CNSSI 1253).

*This is reference guidance only — obtain ATO from your Authorizing Official.*
