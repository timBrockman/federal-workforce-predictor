# Productionizing Checklist

This document collects practical steps to take customer-spend-api from template to production service.

## 1. Database

- Switch to managed Postgres (or equivalent)
- Run `alembic upgrade head` as part of deploy pipeline
- Tune connection pooling
- Set up backups, point-in-time recovery, monitoring

## 2. Authentication

- Disable local test keys: `USE_LOCAL_TEST_KEYS=false`
- Provide real JWKS + issuer + audience
- Use short-lived tokens + proper refresh
- Consider rotating keys and using kid in JWKS

## 3. Agent

- Replace the simulation in `agent.py` with real Pydantic AI + tools
- Add proper tool calling for spend data
- Add timeouts, retries, and circuit breakers around LLM calls
- Log model + prompt versions for auditability

## 4. Ethics & Audit

- Wire `persist_decision` reliably (remove the `create_task` hack if needed)
- Add retention policies on `ethical_decision_logs`
- Implement "right to be forgotten" flows
- Add compliance exports

## 5. Observability

- Structured logging with correlation IDs
- Metrics (request rate, latency, error rate, refusal rate)
- Tracing across GraphQL → services → DB / LLM
- Alerts on unusual refusal patterns or high error rates

## 6. Scaling & Resilience

- Horizontal scaling behind load balancer
- Rate limiting (per principal where possible)
- Caching layer (Redis) for recommendations if appropriate
- DB read replicas for summaries

## 7. Security Hardening

- Secrets management (no env in images)
- Network policies / private networking
- Regular dependency updates (`uv lock --upgrade`)
- Input validation and size limits (already partially present)
- Consider signed MCP calls if exposing to untrusted agents

## 8. Documentation & Runbooks

- Keep this template's docs updated as you customize
- Add runbooks for "user wants their data deleted"
- Document your specific synthetic → real data migration path

## 9. Testing in Prod-like Environment

- Keep using `scripts/verify.py` (or fork it) in staging
- Add contract tests against your real IdP
- Load test with realistic consent distributions

## 10. Feature Flags

Introduce flags for:
- Real vs synthetic social
- Real agent vs simulation
- Different recommendation strategies

This makes progressive rollout and A/B testing much safer.

## Remember the Core Values

The reason this template exists is to make **ethics, consent, and transparency** first-class and auditable. When productionizing, preserve that property above all else.

Good luck — and feel free to contribute improvements back to the reference implementation.