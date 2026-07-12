# STRIDE-AI for Federal Workforce Predictor (Initial)

**Status**: Starter document. Will be expanded in small commits.

This applies STRIDE-AI (adapted STRIDE for ML/GenAI per Mauri/Damiani et al.), integrated with OWASP Top 10 for LLMs (2025) and Agentic Apps (2026), plus MITRE ATLAS tactics relevant to a guardrailed career recommendation service.

Focus: Employee assessment ingestion → synthetic signal use → career trajectory / critical-role readiness recommendations + agentic advisor.

All mitigations leverage (and will extend) the existing ethics/Principal/audit/flat-interface architecture.

## Data Flow (High Level)
1. Authenticated client (GraphQL or MCP) → Principal (user_id + consent_level)
2. Submit assessment (with consent flag)
3. Recommender / agent reads assessment + (if consented) synthetic career signals
4. EthicalPolicy checks → decision logged + persisted
5. Response with data_sources + ethics_note (or refusal)

## Example Threat: Tampering - Data Poisoning of Assessments (STRIDE Tampering + OWASP Training Data Poisoning + ATLAS AML.T0001)

**Threat**: Adversary (or compromised upstream) supplies poisoned assessment data (e.g. inflated skills for a protected group or fake signals) to bias career recommendations toward/away from individuals or groups for critical roles.

**Impact**:
- Integrity of recommendations
- Repudiation (hard to audit why a bad assignment happened)
- Potential national security / fairness harm if critical roles misfilled

**Mitigations (current + planned)**:
- Explicit consent_for_career_modeling flag required; low-consent paths degrade or refuse synthetic signals (see `has_consent_for_social` proxy + future career-specific check in Principal/EthicalPolicy).
- All outputs declare exact `data_sources` (assessment vs synthetic_career_signals) + `ethics_note`.
- `EthicalDecisionLog` + `persist_decision` for audit (used in GraphQL + MCP + recommender).
- Refusal of obviously unethical queries (extended keywords for "infer demographics for career", "gender for promotion", etc. in `refuse_unethical_request`).
- Flat GraphQL + limited MCP tools (no arbitrary queries that could be used for extraction or poisoning feedback loops).
- Synthetic data only in this reference (real deployments must add provenance, validation, anomaly detection on assessment streams per NIST AI RMF Map/Measure).

**Related ATLAS**: AML.T0001 (Poison Training Data), AML.T0020 (Exploit Model), plus agentic tool misuse if future agent tools accept untrusted input.

**Status**: Partially mitigated via ethics layer. Future: add input validation / bias testing hooks in recommender, rate limiting per user on submissions, supply chain notes for any training data.

(Expand with more threats: Prompt Injection on ask_agent for career advice, Model Extraction via repeated queries, Excessive Agency on allocation suggestions, etc.)

See also:
- plan.md (Phase 2)
- docs/compliance/ (forthcoming FedRAMP/NIST mappings)
- OWASP Top 10 for LLMs 2025 / Agentic 2026
- MITRE ATLAS
