# IL Deployment Guidance (Skeleton)

**Status**: Initial placeholder. Expand with actual guidance for DoD Impact Levels.

## Overview
This app is designed as a reference for deploying ethics-first AI services into federal environments.

- **IL4 / FedRAMP Moderate baseline**: Current Docker + SQLite/Postgres setup can be adapted with standard FIPS endpoints, US-person restrictions noted in docs.
- **IL5**: Requires GovCloud (or equivalent), FedRAMP High + DoD overlays, US persons only for certain roles, separation of duties. Synthetic data only in this reference; real PII/CUI handling needs additional controls (SC, AC, AU enhancements).
- **IL6**: Classified (SECRET), SIPRNet, dedicated infrastructure, cleared personnel. Not in scope for this public reference template.

## Key Considerations
- Data classification: Extend Principal with sensitivity level.
- Supply chain: Document LLM providers (FedRAMP authorized where possible).
- Monitoring: Leverage existing EthicalDecisionLog + audit for continuous monitoring.

See plan.md, threat model, and NIST crosswalk for related controls.

*This is reference guidance only — obtain ATO from your Authorizing Official.*
