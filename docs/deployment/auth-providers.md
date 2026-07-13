# Auth Providers (Auth0 & Keycloak)

## Auth0 (Primary Recommended)

1. Create an application (Machine to Machine for client credentials, or SPA/API for JWTs).
2. Note the Domain, Client ID, Client Secret, Audience.
3. Configure Allowed Callback URLs etc. as needed.
4. In `.env`:

```env
USE_LOCAL_TEST_KEYS=false
AUTH_ISSUER=https://your-tenant.us.auth0.com/
AUTH_AUDIENCE=https://api.federal-workforce-predictor.example.com
AUTH0_CLIENT_ID=...
AUTH0_CLIENT_SECRET=...
AUTH0_TOKEN_URL=https://your-tenant.us.auth0.com/oauth/token
```

5. For JWT validation you can use the JWKS:
   `AUTH_JWKS_URL=https://your-tenant.us.auth0.com/.well-known/jwks.json`

The code in `security.py` supports both the client credentials helper and standard Bearer JWT validation.

## Keycloak (Self-Hosted / Enterprise)

Use the optional profile in docker-compose:

```bash
docker compose --profile keycloak up
```

Then point your app at the Keycloak instance.

The realm import file lives at `docker/keycloak-realm.json` (minimal client created for service accounts).

Environment:

```env
AUTH_ISSUER=http://localhost:8080/realms/federal-workforce-predictor
AUTH_AUDIENCE=federal-workforce-predictor
AUTH_JWKS_URL=http://localhost:8080/realms/federal-workforce-predictor/protocol/openid-connect/certs
```

For production Keycloak, use proper TLS and service account credentials.

## Switching Between Demo and Real

The single switch:

```env
USE_LOCAL_TEST_KEYS=true   # demo / tests (default)
USE_LOCAL_TEST_KEYS=false  # real IdP
```

When false, the code will attempt to use `AUTH_JWKS_URL` (or fall back).

See `verify_token` and `_get_public_key` in `app/core/security.py`.

## Token Claims Expected

- `sub` or `user_id` → becomes `Principal.user_id`
- `consent_level` or `custom:consent` → consent level
- `scope` → space-separated scopes
- `email` (optional)

If your IdP uses different claim names, extend the mapping in `verify_token`.

## Client Credentials vs User Tokens

- `/demo-token` with client_id/secret → service token (good for MCP or backend-to-backend)
- Regular user login flow → user tokens with their consent_level

The template primarily demonstrates service + consent_level style.

## Security Recommendations

- Use short-lived tokens + refresh where possible.
- Validate `aud` and `iss` strictly.
- Rotate RSA keys / JWKS regularly.
- For MCP, treat the caller as trusted only within the scope of the `user_id` + `consent_level` it provides.

See also the main [Auth usage](../usage/auth.md).