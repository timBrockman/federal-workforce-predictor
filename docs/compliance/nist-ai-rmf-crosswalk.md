# NIST AI RMF Crosswalk (Initial Skeleton)

**Purpose**: Placeholder for mapping the federal-workforce-predictor controls and practices to the NIST AI Risk Management Framework (Govern / Map / Measure / Manage).

This is a reference starting point only — not a complete or certifiable artifact. It does **not** represent an ATO or authorized implementation. Always verify current FedRAMP, NIST, and agency requirements.

## Govern
- [x] Risk management policies and procedures (EthicalPolicy class + persist_decision + EthicalDecisionLog)
- [x] Accountability structures (Principal carries user_id + consent_level through all layers; audit via logs)
- [~] Supply chain risk (LLM provider notes in docs; simulation agent reduces exposure; production: pin FedRAMP authorized models)

## Map
- [x] Context identification (employee lifecycle / critical role use case documented in README + use-cases.md)
- [x] Risk identification (bias in career outcomes, privacy of HR data, prompt injection on agent — see STRIDE-AI-initial.md)
- [x] Impact assessment (high-stakes for mission-critical staffing called out; refusals for protected-class inference)

## Map
- [ ] Context identification (employee lifecycle / critical role use case)
- [ ] Risk identification (bias in career outcomes, privacy of HR data, prompt injection on agent)
- [ ] Impact assessment (high-stakes for mission-critical staffing)

## Measure
- [x] Risk metrics (consent levels exercised in verify/tests; source attribution + ethics_note always present; refusal paths tested)
- [~] Bias / fairness testing (synthetic profiles + ethics tests for protected-class keywords; full bias harness future)
- [x] Performance and robustness (verify.py + pytest matrix cover happy + low-consent + refusal paths)

## Manage
- [x] Risk treatment (refusals + degradation on low consent in EthicalPolicy + recommender; human-in-loop emphasized for high impact)
- [x] Incident response (EthicalDecisionLog persisted on all paths; queryable for audits)
- [~] Continuous monitoring (decision logs provide foundation; future integrate with SIEM / FedRAMP CM)

## Notes
- Many existing ethics/Principal/flat-interface + persist controls map naturally to Govern/Map/Measure/Manage.
- See plan.md (MVP status) and expanded STRIDE-AI (7 threats).
- Cross-reference with il-deployment-guidance.md and FedRAMP notes.

*This is now a substantive starting crosswalk for the reference implementation.*

