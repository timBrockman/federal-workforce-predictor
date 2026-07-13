# federal-workforce-predictor: MVP Plan

**Date**: 2026-07-13  
**Status**: Core federal employee lifecycle / career readiness paths landed and wired (submitAssessment + careerRecommendations via GraphQL + MCP + recommender + agent + DB fetch). Legacy spend paths kept but de-emphasized + marked. Partial rebrand complete (README, config defaults, explorer, keycloak, app init, some docs). Threat model: 3 examples. Compliance docs: 2 skeletons. All `uv run pytest -m "not slow"`, full pytest, and `scripts/verify.py` green (verified 2026-07-13). Working tree clean.  
**Context**: Pivoted from customer-spend-api (budget demo) to federal-workforce-predictor reference (structured assessments + synthetic career signals + consent-gated critical-role readiness recs + guardrailed agent + ethics/audit + compliance guidance). Commit discipline: all work as small single-purpose commits/PRs with structured messages. Synthetic data only. No real PII.

## Verification Commands (Run Before + After Any Change)
These must be clean:

```bash
uv sync --extra dev
uv run python -m pytest -q -m "not slow"
uv run python scripts/verify.py
```

### Latest Runs (2026-07-13)
- `uv sync --extra dev`: exit 0.
- `pytest -m "not slow"`: 15/15 pass (........................).
- Full pytest: 16/16 pass.
- `scripts/verify.py`: ✅ All verifications passed!
  - DB (repos, tx + questionnaire + new EmployeeAssessment + CareerSignal).
  - Auth + legacy recs + ethics.
  - GraphQL (careerRecommendations + legacy spendSummary).
  - MCP (list_tools, direct calls for budget/career/submit + full stdio spawn; submit→recommend flow exercised).
- Career flow after submit_assessment demonstrably works (high/low consent degradation + sources).

## Current State (Accomplished)
- **Primary federal paths**:
  - `EmployeeAssessment` model + repo (skills_inventory, performance_level, career_goals, critical_role_interest, consent_for_career_modeling, raw_answers).
  - `CareerSignal` + synthetic career profiles in recommender.
  - `submit_assessment` mutation (GraphQL) + MCP tool.
  - `career_recommendations` query + MCP tool (fetches latest assessment for user when present; falls back to synthetic).
  - Agent updated to pull assessment + call career recs + append career notes.
  - Ethics/Principal/consent gating, source attribution, persist_decision, refusals all flow through.
  - Seeding in `scripts/seed_demo_data.py` covers assessments/signals (additive).
- GraphQL types: `AssessmentInput`, `CareerRecommendation` (legacy kept alongside).
- Schema: new fields primary in comments + ordering where possible; legacy paths explicitly labeled "kept during pivot".
- MCP server: 5 tools (3 legacy + get_career_recommendations + submit_assessment); `_principal_from_args` for context.
- Tests: added submit + career consent tests in test_graphql.py + test_mcp.py.
- Verify: demonstrates submit + after-recs flow + stdio.
- Rebrand started: app_name, README title+intro+examples, config audience, explorer, keycloak realm, some doc intros, CONTRIBUTING header.
- Threat model starter (STRIDE-AI + OWASP/ATLAS): 3 examples (assessment poisoning, prompt injection on agent, info disclosure of profiles).
- Compliance starters: nist-ai-rmf-crosswalk.md skeleton (Govern/Map/Measure/Manage), il-deployment-guidance.md (IL4/5/6 notes).
- DB: Alembic migrations present (initial + employee assessments/career).
- Everything else from prior (flat limited GraphQL + guards, async SQLA + pooling, Principal threading to MCP, EthicalPolicy, offline local keys + demo tokens, rate limits, etc.) still solid.

## Legacy Paths (Intentional During Transition)
- `spend_summary`, `recommendations`, `submit_questionnaire`, `get_spend_summary`, `get_budget_recommendations`, `ask_budget_agent`, old Questionnaire/Transaction models.
- These remain functional for reference/compatibility. Marked "legacy" or "kept during pivot" in code and docs.
- Goal for MVP: new federal paths are the documented primary; legacy do not block or confuse the main story.

## What Is the MVP? (Measurable)
MVP is a credible, runnable **reference implementation** for an ethics-first federal workforce / talent / critical-role readiness predictor. It must be clone-and-run demonstrable and document the right patterns.

MVP success criteria:
1. Primary end-to-end flow works and is the lead story: `submit_assessment` (GraphQL or MCP) → `career_recommendations` (uses real assessment data when submitted) with consent gating, `data_sources`, `ethics_note`.
2. Guardrailed agent answers workforce-oriented questions (e.g. "skills needed for X mission").
3. Consent levels visibly affect output (high = richer sources/recs; low = degraded or refused).
4. All outputs declare sources + ethical decisions are auditable (persisted).
5. Schema/docs/examples lead with federal paths; legacy clearly labeled.
6. Rebrand complete for high-visibility surfaces (no "customer-spend-api" as primary name in README, pyproject description, top-level docs, scripts, explorer, getting-started, usage).
7. Threat model expanded to 6–8 concrete examples with mitigations (STRIDE-AI / OWASP LLM+Agentic / ATLAS).
8. Compliance docs have substance: FedRAMP SSP outline or mapping skeleton + expanded NIST AI RMF crosswalk + IL deployment notes.
9. Verify + tests + one-command setup remain green and exercise the new primary paths first.
10. README + getting-started + use-cases + architecture lead with submit + career recs + federal context.
11. Full "git clone ... && uv sync && uv run python scripts/seed... && uv run python scripts/verify.py" succeeds cleanly for a new user.

## MVP Gaps / Remaining Steps (Small Atomic Commits Only)
Work in small, reviewable units. Prefer one file / one focused area per commit. Update plan + run verify before/after.

### P1: Schema / Documentation Primacy (Make New Paths the Lead)
- [ ] Update GraphQL schema.py: improve comments, ensure career_* and submit_assessment appear before or prominently vs legacy; minor docstrings.
- [ ] Update app/api/graphql/types.py docstrings if needed.
- [ ] Refresh docs/architecture.md flow diagram + text to lead with "submit assessment → career recs".
- [ ] Update docs/use-cases.md: replace spend examples with federal employee lifecycle / critical role readiness; keep one "patterns lift" note.
- [ ] Update docs/getting-started.md: change primary curl/GraphQL/MCP examples to careerRecommendations + submit_assessment (show high/low consent).

### P2: Full Rebrand Sweep (Gradual, One Area at a Time)
- [ ] pyproject.toml: name, authors, urls, description, entry points to "federal-workforce-predictor". (Note: uv.lock will be updated on next sync; commit both or let CI.)
- [ ] CONTRIBUTING.md: fix clone URL + cd.
- [ ] scripts/verify.py: header, final print, legacy tool calls ok but update narrative.
- [ ] tests/conftest.py: module docstring.
- [ ] All docs/ files still containing "customer-spend-api":
  - docs/configuration.md (table + .env example)
  - docs/usage/graphql.md
  - docs/usage/mcp.md (update tool examples to prefer career)
  - docs/concepts/*.md (synthetic-data, mcp-integration, principal-model, limited-graphql, ethics-and-consent)
  - docs/deployment/*.md (docker, auth-providers)
  - docs/productionizing.md
  - docs/extending/*.md (review for examples)
- [ ] app/main.py, app/services/*.py, app/services/mcp_server.py: update module docstrings / comments that still say "spend budget service".
- [ ] docs/usage/scripts.md and any other missed references.
- [ ] .env.example + docker-compose.yml + alembic comments (db file name `spend.db` may stay for minimal diff; add comment "legacy filename; swap via DATABASE_URL").
- [ ] After sweep: global grep for remaining "customer-spend" and "spend-api" (except historical notes in __init__.py or plan).
- [ ] Optional small: rename internal legacy functions only if low risk (prefer keep for now to minimize blast).

### P3: Threat Model + Compliance Expansion + Docs Refresh
- [ ] Expand docs/threat-models/STRIDE-AI-initial.md: add 3–5 more examples (e.g. model extraction via rec queries, excessive agency on role allocation, data exfil via agent, supply-chain on LLM, consent bypass attempts, synthetic profile poisoning). Keep structured (Threat / Impact / Mitigations / Related / Status).
- [ ] docs/compliance/nist-ai-rmf-crosswalk.md: fill out more rows with specific mappings from current code (EthicalPolicy → Govern/Manage, persist + sources → Map/Measure, etc.).
- [ ] Add or expand FedRAMP-relevant section (either in nist or new file): high-level SSP outline (AC, AU, SC, CM controls relevant to AI), ATO notes, continuous monitoring via decision logs.
- [ ] Flesh il-deployment-guidance.md with more concrete controls per IL (data handling, network, personnel, logging).
- [ ] Update README quickstart + examples to use career first; mention legacy only briefly.
- [ ] Refresh docs/concepts/ethics-and-consent.md and use-cases to use federal terminology.
- [ ] Ensure explorer.html and main health/docs point clearly.

### P4: Polish, Final Checks, MVP Closure
- [ ] Review and update any remaining code comments (agent.py, recommender.py, mcp_server.py, main.py) for accuracy.
- [ ] Add or update a "MVP Demo Flow" section in README or getting-started (submit then recommend).
- [ ] Run full end-to-end clone simulation if possible (or document exact steps).
- [ ] Ensure all tests still cover consent degradation for career paths.
- [ ] Update this plan.md to mark sections complete + add "MVP achieved" date when criteria met.
- [ ] (Optional but nice) One small commit for any polish on career rec logic / rationale quality in recommender if gaps found during docs work.
- [ ] Final verification run + git status clean.

## Immediate Next (After This Plan Update)
Pick one small item and commit atomically:
1. One rebrand file (e.g. pyproject.toml + verify header) OR
2. Add 2 more threat examples to STRIDE-AI-initial.md OR
3. Update getting-started.md primary examples to career paths.

Always: edit → run verify + targeted pytest → structured commit message (see docs/development/commit-conventions.md).

## Definition of MVP "Done" (All Must Be True)
- Verification commands (sync, pytest not-slow, verify.py) exit 0 and demonstrate new primary flows.
- Primary demo path in README/getting-started/verify is submit_assessment → career_recommendations.
- No primary branding still says "customer-spend-api" (historical mentions allowed in notes).
- At least 6–8 documented threats with mitigations.
- Compliance docs contain usable FedRAMP/NIST/IL substance (not just placeholders).
- New federal use cases dominate docs/use-cases.md and architecture.
- All GraphQL/MCP paths for career + submit exercised in tests + verify.
- Ethics decisions, sources, consent gating, refusal behavior visible and correct.
- Clean "clone, seed, verify" story for first-time users.
- plan.md reflects reality and is updated.

## Open Items / Non-MVP (Future)
- Full rebrand of internal function names (ask_budget_agent etc.) or deprecate legacy entirely.
- Real LLM agent behind flag (Pydantic AI + LiteLLM exercised).
- Postgres + full prod Alembic workflows.
- Real IdP + JWKS in primary docs (beyond the existing helpers).
- Bias testing harness, more metrics, FedRAMP SSP template (full doc).
- IL5/IL6 hardened image examples.
- Coverage, ruff, mypy in recommended commands.
- Published package / Docker Hub image.

## Notes on Process
- User constraints respected: adapt (no from-scratch), small atomic commits only, structured commit messages (Context/Why, Design decisions with paths, Tradeoffs, Changes, Verification, Refs).
- Synthetic data + refusals for high-stakes/bias protected classes remain core.
- Database filename `spend.db` left as-is for minimal migration churn (documented).
- Verify.py is the source of truth for "it works".

See README.md for quickstart. Full docs in `docs/`. Run the verification commands frequently.
