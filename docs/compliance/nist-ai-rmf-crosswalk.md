# NIST AI RMF Crosswalk (Initial Skeleton)

**Purpose**: Placeholder for mapping the federal-workforce-predictor controls and practices to the NIST AI Risk Management Framework (Govern / Map / Measure / Manage).

This is a reference starting point only — not a complete or certifiable artifact. Expand in small increments.

## Govern
- [ ] Risk management policies and procedures (see EthicalPolicy, decision logging)
- [ ] Accountability structures (Principal + consent model, audit logs)
- [ ] Supply chain risk (LLM provider notes — future)

## Map
- [ ] Context identification (employee lifecycle / critical role use case)
- [ ] Risk identification (bias in career outcomes, privacy of HR data, prompt injection on agent)
- [ ] Impact assessment (high-stakes for mission-critical staffing)

## Measure
- [ ] Risk metrics (consent levels, source attribution completeness, refusal rate for unethical queries)
- [ ] Bias / fairness testing (synthetic protected attributes in tests)
- [ ] Performance and robustness (verify.py + pytest matrix)

## Manage
- [ ] Risk treatment (refusals, degradation on low consent, human-in-loop recommendations for high impact)
- [ ] Incident response (EthicalDecisionLog + audit)
- [ ] Continuous monitoring (future: integrate with FedRAMP continuous monitoring)

## Notes
- Many existing ethics/Principal/flat-interface controls map naturally to multiple functions.
- See plan.md for the full federal pivot plan and threat modeling.
- Cross-reference with FedRAMP SSP skeleton and DoD IL guides when created.

*This document will be updated in subsequent small commits as the implementation and threat model mature.*
