# ADR-005: Offline-First Auth with Local Test Keys

## Status

Accepted

## Context

A reference template must be runnable with zero external dependencies and zero cost. At the same time it must demonstrate realistic production auth flows.

## Decision

- Default: `USE_LOCAL_TEST_KEYS=true` → generated RSA keys, fully offline, identical validation path to real tokens.
- Production path: flip the flag, provide JWKS + issuer + audience.
- Client credentials helper exists for both demo and real flows.

## Consequences

**Positive**
- `uv sync && uv run pytest` works on a plane with no internet.
- Developers learn the real JWT validation code without needing an account.
- Easy to test consent_level, scopes, etc. via `create_demo_token`.

**Trade-offs**
- The local key path must never be used in real production (enforced by docs and the flag).
- Slight extra code to support both paths.

## References

- `app/core/security.py`
- `scripts/get_demo_token.py`
- `docs/deployment/auth-providers.md`
- Configuration: `USE_LOCAL_TEST_KEYS`