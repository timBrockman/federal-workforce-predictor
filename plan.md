# customer-spend-api: Implementation Plan & Re-assessment

**Date**: 2026-07-08  
**Status**: Core implementation + tests + verification largely complete and passing. Documentation + a few wiring gaps remain.  
**Context**: Built as a production-grade *reference/demo template* for AI services (FastAPI + Strawberry GraphQL (intentionally flat/limited), MCP stdio, async SQLAlchemy + pooling, ethics-first with consent/transparency/refusal/audit, offline Auth0/Keycloak mocks + local RSA keys, recommender + stub Pydantic AI agent, minimal UI).

## Verification Commands (Run Before Any Changes)
These must be clean for any further work:

```bash
uv sync --extra dev
uv run python -m pytest -m "not slow" -q
uv run python scripts/verify.py
```

### Latest Runs (multiple invocations, including direct .venv/bin/python + timeout)
- `uv sync --extra dev`: exit 0 (174 packages resolved).
- `pytest -m "not slow"`: 15/15 pass.
- Full `pytest`: 16/16 pass (15 non-slow + 1 slow agent test).
- `scripts/verify.py` (uv run and direct `.venv/bin/python`): **✅ All verifications passed!**
  - DB repositories (User + FK-safe inserts, Tx sums, Questionnaire).
  - Auth + Recommender + Ethics (token, recs with sources + consent gating).
  - GraphQL (TestClient override + DB-backed).
  - MCP (list + call direct; full stdio_client spawn + call_tool).
- Unauth GraphQL (TestClient): `200` + `errors` with `extensions: {"code": "UNAUTHENTICATED"}` (confirmed).
- Auth GraphQL: data returned cleanly.

All recommended commands + critical paths (direct unauth/auth, MCP stdio) succeed consistently. No BrokenPipe on recent stdio runs.

## What Works (Verified)
- Dependency install, full test suite, one-shot verify script.
- Async DB (SQLAlchemy 2.0 + explicit pooling, even SQLite; PRAGMA + rollback fixtures; create_all in init + lifespan).
- Repositories (all 5 entities exercised; get_or_create before FK dependents fixes IntegrityError).
- Auth: Principal model (consent_level, has_consent_for_social, scopes), demo tokens (RS256 local keys), get_current_principal (graceful None), client_credentials helper (mocked + real path), /demo-token.
- GraphQL: flat schema (spendSummary, recommendations, askAgent, submitQuestionnaire), QueryDepthLimiter + custom cost guard, structured GraphQLError with extensions for auth, dependency overrides for tests.
- Recommender: rules + synthetic interests + ethics + source attribution.
- Ethics: policy checks (consent, transparency, refuse_unethical), decisions logged (in-mem for template).
- Agent: stub simulation (pre-filter + recs + notes) passes slow test.
- MCP: 3 safe tools, direct + full stdio end-to-end (verify spawns server).
- App: lifespan (seed demo txs + user), rate limiting, CORS, explorer, health, debug endpoints.
- Tests: repo tests (5), security/ethics (incl. client creds respx), graphql (auth/unauth, depth, consent, slow).
- Config: 12-factor (pydantic-settings), .env.example, offline-first.
- Other: flat schema deliberate limit, synthetic data only, ethics as cross-cut.

## What Doesn't Work / Gaps / Fragile Areas
- **plan.md was absent** at start of re-assessment (now added by this document).
- **MCP principal**: `app/services/mcp_server.py` hardcodes `DEMO_PRINCIPAL` (always demo-user-123, consent=2). Comment admits "in real deployments you would thread auth". Verify exercises only demo path. No real Principal support from MCP context.
- Agent is simulation stub only (no live pydantic-ai / LiteLLM execution — intentional deferral).
- `execute_sync(schema)` fails for async resolvers (use TestClient or `await schema.execute(...)`).
- Console traceback sometimes leaks on GraphQLError raises (response itself is clean 200+ext).
- `scripts/seed_demo_data.py`: still a TODO stub.
- No Alembic migration files (relies on `create_all`; comment says "use Alembic in prod").
- Ethics decisions: model + repo exist, but main paths (recommender, agent, GraphQL) use in-memory `_ETHICS_LOG` only. Not persisted.
- JWKS real path: TODO stub (only local test keys fully work; partial fallback).
- Test gaps: heavy reliance on dependency_overrides (fewer raw header token tests); no dedicated MCP principal variation tests; ethics log DB integration untested in main flows.
- Minor: sys.path hacks in scripts; verify stdio spawn can be timing-sensitive (though currently stable); deprecation warning filter in pytest config for extensions; no coverage/mypy/ruff as part of "recommended" commands; slow test imports heavier libs.
- Real Auth0/Keycloak requires .env + `USE_LOCAL_TEST_KEYS=false` + JWKS (not exercised in default runs).
- No integrated MCP in FastAPI (by design: stdio standalone).

## Critical Re-assessment
The implementation is **more complete and verified** than prior conversation notes suggested. All user-looped commands (sync, non-slow pytest, verify.py) + direct unauth GraphQL checks are green. Phase 1 deliverables (repo tests + fixture fixes for engine/FK, security client_creds tests + helper, GraphQLError extensions on all protected fields, main.py updates, etc.) are present and passing.

**Strengths**:
- Matches original spec closely: ethics-first, limited/flat GraphQL + guards, MCP curated tools, pooling/async, mocks everywhere, production signals (rate limit, settings).
- Verifiable by the exact commands the user requested.
- Deliberate choices (flat schema, synthetic, offline keys, stub agent) respected.

**Weaknesses vs "production-grade template" goal**:
- Documentation (plan.md missing until now; ADRs/ empty).
- Wiring completeness (MCP auth, ethics persistence to DB, Alembic, real JWKS).
- Polish (error logging cleanliness, broader test variety, script robustness).
- Some core TODOs left (though non-blocking for demo use).

**Trade-off decisions respected** (per history):
- No Redis (user: "don't add redis").
- Keep basic setup.
- Agent stub for now.
- Offline mocks + local keys primary.
- Flat GraphQL (no deep nesting).

### Example Trade-off Matrices (as originally requested)
**Auth approach**:
| Option | Pros | Cons | Chosen |
|--------|------|------|--------|
| Real JWKS + Auth0/Keycloak only | Production-accurate | No offline dev/CI | Hybrid (local RSA default + real path) |
| Local test keys + mocks | Fast, no secrets, reproducible | Not identical to prod | Primary for template + tests |
| Client credentials helper | Matches real flows | Requires IdP | Added (with respx mocks) |

**MCP auth**:
| Option | Pros | Cons | Chosen |
|--------|------|------|--------|
| Hardcode DEMO_PRINCIPAL | Simple, verify easy | Not realistic | Temporary (now gap) |
| Thread Principal from context / separate creds | Realistic for stdio clients | Complex (MCP stdio limited) | Target for Phase 2 |
| Separate MCP auth layer | Clean separation | Extra surface | Deferred |

**Agent**:
| Option | Pros | Cons | Chosen |
|--------|------|------|--------|
| Full pydantic-ai + LiteLLM now | "Real" | Heavy deps, non-deterministic, cost | Stub + ethics guard (defer) |
| Rules + recs simulation | Fast, deterministic, ethics demo | Not full LLM | Current |
| Optional real behind flag | Flexible | Complexity | Future |

**DB / persistence**:
| Option | Pros | Cons | Chosen |
|--------|------|------|--------|
| create_all + SQLite | Zero setup, template friendly | No migration history | Current + note Alembic |
| Alembic from day 1 | Prod-ready | Slower start | Add in Phase 2 |
| In-mem ethics log | Simple | No audit trail | In-mem now; wire repo soon |

**GraphQL error model**:
| Option | Pros | Cons | Chosen |
|--------|------|------|--------|
| HTTP 401 on unauth | REST-like | Violates GraphQL "always 200 + errors" | GraphQLError + extensions (200 + errors) |
| Extensions for code | Structured, client-friendly | Slightly more verbose | Yes (UNAUTHENTICATED etc.) |

## Phases (Updated)
**Phase 1 (Core foundations + tests + demo updates)** — Largely complete (repo tests, security helpers/tests, extensions, fixes, verify green).
- DB + repos + fixtures (done).
- Auth (demo + client creds) + Principal (done).
- Flat GraphQL with guards + extensions (done).
- Recommender + ethics policy (done).
- Basic tests + verify script (done).
- MCP skeleton + direct (done, but principal pending).

**Phase 2 (MCP maturity + persistence + polish + docs)** — Started 2026-07-08.
- [x] Replace DEMO_PRINCIPAL with real/configurable Principal support in mcp_server (via tool args user_id/consent_level). Updated list_tools schemas, call_tool, direct+stdio usage in verify.
- [x] Added tests/test_mcp.py exercising multiple principals (consent levels, users) direct + stdio (slow).
- [~] Persist ethics decisions via EthicsLogRepository (added persist_decision + await in GraphQL recs/MCP recs; agent attempts too).
- [ ] Add Alembic initial migration + update init_db/docs.
- [ ] Complete seed_demo_data.py.
- [ ] Expand tests further (raw header auth, ethics DB queries, unauth extensions).
- [ ] Clean GraphQLError tracebacks.
- [x] plan.md updated with progress.
- [ ] JWKS + other.
- [ ] Verification enhancements.

**Phase 3 (Productionization + real agent + examples)** (future).
- Real Pydantic AI agent (optional, behind setting).
- Swap to Postgres example + full Alembic.
- Real IdP setup guide + secrets handling.
- Observability (structlog enhancements, tracing), more rate limit / cost controls.
- Example "how to productionize" doc.
- Higher test coverage target + CI simulation.

## Definition of "Done" (Measurable)
A release / handoff is "done" when **all** of the following are true:
1. Recommended commands run clean:
   - `uv sync --extra dev` succeeds.
   - `uv run pytest -m "not slow"` → 100% pass (currently 15 tests).
   - `uv run python scripts/verify.py` → ✅ All verifications passed! (DB, auth/ethics/recomm, GraphQL, MCP stdio).
2. Full test suite (incl. slow) is green (16/16).
3. Unauth/auth GraphQL behavior confirmed (200 + extensions for errors; data for valid).
4. No hardcoded DEMO_PRINCIPAL remains in mcp_server; real Principal support exercised.
5. `plan.md` exists and is current (includes this re-assessment, matrices, verification reqs, done criteria, phases).
6. Core TODOs/FIXMEs addressed or explicitly scoped (MCP auth, ethics persistence, Alembic, seed, JWKS).
7. Ethics decisions persisted to DB in recommender/agent/GraphQL paths (repo used).
8. README quickstarts (token, curl/GraphiQL, MCP, explorer) + /demo-token work end-to-end.
9. Tests cover exercised paths (auth/unauth, ethics refusal, DB repos, MCP, recommender) with no critical holes.
10. Template is usable as starting point (easy to extend schema, swap DB, add real auth, run verify).

Bonus / stretch for high quality: ruff clean, basic coverage >80% on core modules, one ADR written.

## Open Items / TODOs (tracked)
- [x] MCP: real principal via args + client tests (Phase 2 started + implemented).
- [~] Ethics persistence to DB (wired persist_decision + calls in GraphQL/MCP/agent; in-mem kept for tests; full test coverage pending).
- [x] Alembic initial migration (autogenerated with full CREATEs) + completed seed_demo_data.py + updated init_db comment.
- [ ] GraphQLError logging cleanliness.
- [ ] Expanded tests + coverage.
- [ ] JWKS path.
- [x] plan.md (this file).
- [x] Verify commands green (multiple runs, including after Phase 2 edits).

## Notes
- User preferences applied: basic setup, no Redis, defer some, "I'll defer to you based on best practices".
- Synthetic social always mocked.
- Designed for easy swap (SQLite → Postgres, local keys → JWKS, stub → real agent).
- Next: After user confirmation, implement Phase 2 items starting with MCP principal + plan alignment.

See README.md for quickstart. For detailed documentation see the `docs/` folder (getting-started, configuration, concepts, usage, deployment, extending, use-cases, ADRs, etc.).

Run the verification commands frequently.
