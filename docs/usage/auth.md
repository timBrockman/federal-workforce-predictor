# Authentication & Authorization

## Token Acquisition

### Demo / Local (default, no network)

```bash
uv run python scripts/get_demo_token.py --user demo-user-123 --consent 2
```

Uses locally generated RSA keys. Perfect for development and tests.

The token contains:
- `sub` (user_id)
- `consent_level`
- `scope`
- Standard JWT claims (iss, aud, exp)

### Real Client Credentials (Auth0 / Keycloak)

Set in `.env` or environment:

```env
USE_LOCAL_TEST_KEYS=false
AUTH0_CLIENT_ID=...
AUTH0_CLIENT_SECRET=...
AUTH0_TOKEN_URL=https://your-tenant.auth0.com/oauth/token
AUTH_ISSUER=...
AUTH_AUDIENCE=...
```

Then:

```bash
curl -X GET "http://localhost:8000/demo-token?client_id=xxx&client_secret=yyy"
```

Or use the helper in code.

See `app/core/security.py:get_token_via_client_credentials`.

## The Principal Object

Every authenticated request yields a `Principal`:

```python
class Principal:
    user_id: str
    scopes: list[str]
    consent_level: int
    email: str | None = None
```

Key method:
- `has_consent_for_social()` → respects `require_consent_for_social` setting

This object is passed to:
- All GraphQL resolvers (via context)
- Recommender
- Agent
- **MCP tools** (via `user_id` + `consent_level` arguments)

## Consent Level Effects

| Level | Synthetic Social? | Typical Behavior |
|-------|-------------------|------------------|
| 0     | No                | Questionnaire only; recommendations may be more conservative |
| 1     | No                | Same as 0 |
| 2+    | Yes (if enabled)  | Full sources including synthetic signals + richer notes |

All responses declare the sources used.

## Token Claims

Demo tokens set:
- `consent_level`
- `scope` (space separated)
- `sub`

Real IdP tokens should provide equivalent claims (or use the same mapping logic in `verify_token`).

## Error Handling

- Missing / invalid token on protected fields → 200 + GraphQL error with `extensions.code: "UNAUTHENTICATED"`
- Expired / bad signature → same
- The `/demo-token` endpoint itself returns 401 on real credential exchange failure.

## Best Practices

- Never log raw tokens.
- Use short-lived tokens + refresh where possible.
- In production, set `USE_LOCAL_TEST_KEYS=false` and provide real JWKS.
- For MCP clients, pass the minimal `user_id` + `consent_level` needed for the call (principle of least privilege).

## Testing Different Principals

```bash
# High consent
TOKEN=$(uv run python scripts/get_demo_token.py --consent 2)

# Low consent (see ethics degradation)
LOW=$(uv run python scripts/get_demo_token.py --user low-c --consent 0)
```

`scripts/verify.py` and the MCP tests do exactly this.

## Related Documentation

- [Principal Model](../concepts/principal-model.md)
- [Ethics & Consent](../concepts/ethics-and-consent.md)
- [MCP Usage](mcp.md) — how consent flows to tools
- Configuration: `AUTH_*`, `USE_LOCAL_TEST_KEYS`, `REQUIRE_CONSENT_FOR_SOCIAL`