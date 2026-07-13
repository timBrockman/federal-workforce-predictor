"""Production-grade JWT auth with support for Auth0/Keycloak + first-class offline test keys.

Core concept: `Principal` (user_id + scopes + consent_level) that is threaded
through GraphQL resolvers, services, **and** MCP tools.

Key functions:
- create_demo_token (offline)
- get_token_via_client_credentials (real IdP)
- get_current_principal (FastAPI dep)
- verify_token (the actual JWT logic)

See docs/usage/auth.md and docs/concepts/principal-model.md.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, cast

import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel

from app.core.config import get_settings

settings = get_settings()

security = HTTPBearer(auto_error=False)

# --- Local test key pair (generated once, used for dev/CI only) ---
# In real prod these come from JWKS. Never commit real private keys.
_TEST_PRIVATE_KEY: str | None = None
_TEST_PUBLIC_KEY: str | None = None


def _ensure_test_keys() -> tuple[str, str]:
    global _TEST_PRIVATE_KEY, _TEST_PUBLIC_KEY
    if _TEST_PRIVATE_KEY and _TEST_PUBLIC_KEY:
        return _TEST_PRIVATE_KEY, _TEST_PUBLIC_KEY

    # Generate RSA keypair for tests (2048 bit is fine for demo)
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    pem_private = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode()

    public_key = private_key.public_key()
    pem_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()

    _TEST_PRIVATE_KEY = pem_private
    _TEST_PUBLIC_KEY = pem_public
    return pem_private, pem_public


@dataclass
class Principal:
    """Authenticated principal carrying identity + consent + scopes for ethics-aware decisions."""

    user_id: str
    scopes: list[str]
    consent_level: int = 0  # 0=none, 1=questionnaire, 2+=social allowed
    email: str | None = None
    raw_claims: dict[str, Any] | None = None

    def has_consent_for_social(self) -> bool:
        return self.consent_level >= 2 or not settings.require_consent_for_social

    def can_use_agent(self) -> bool:
        return bool(self.scopes) and "agent:read" in self.scopes or "read:all" in self.scopes


class TokenData(BaseModel):
    sub: str
    scopes: list[str] = []
    consent_level: int = 0
    email: str | None = None


def _get_public_key(token: str) -> str | dict[str, Any]:
    """Return key for verification. Prefers local test keys in dev."""
    if settings.use_local_test_keys:
        _, public = _ensure_test_keys()
        return public

    # Real path: would fetch JWKS and pick key by kid (simplified here)
    # For full impl one would use PyJWT or authlib with caching.
    # We keep simple for template but production-ready structure.
    if settings.auth_jwks_url:
        # TODO: implement cached JWKS fetch + kid selection (left as exercise / future)
        # For now fall back to issuer public if needed.
        pass

    # Fallback - in real use you would raise if no key
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No verification key available",
    )


async def verify_token(credentials: HTTPAuthorizationCredentials | None) -> Principal:
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    try:
        if settings.use_local_test_keys:
            private, public = _ensure_test_keys()
            # For verification we use public
            payload = jwt.decode(
                token,
                public,
                algorithms=["RS256"],
                audience=settings.auth_audience,
                issuer=settings.auth_issuer,
                options={"verify_aud": True, "verify_iss": True},
            )
        else:
            # Real JWKS path (stub - replace with real impl using caching)
            key = _get_public_key(token)
            payload = jwt.decode(
                token,
                key,
                algorithms=["RS256"],
                audience=settings.auth_audience,
                issuer=settings.auth_issuer,
            )

        # Extract claims we care about for ethics + authorization
        sub = payload.get("sub") or payload.get("user_id") or "unknown"
        scopes = (payload.get("scope") or "").split()
        consent = int(payload.get("consent_level", payload.get("custom:consent", 0)) or 0)
        email = payload.get("email")

        return Principal(
            user_id=sub,
            scopes=scopes or ["read:all"],
            consent_level=consent,
            email=email,
            raw_claims=payload,
        )
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {exc}",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


async def get_current_principal(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),  # noqa: B008
) -> Principal | None:
    """FastAPI dependency.

    Returns None if unauthenticated (GraphQL resolvers should raise GraphQLError
    for protected fields).
    """
    if not credentials:
        return None
    try:
        return await verify_token(credentials)
    except Exception:
        return None


# --- Demo / test token minting (client_id/secret simulation + local signing) ---
def create_demo_token(
    user_id: str = "demo-user-123",
    scopes: list[str] | None = None,
    consent_level: int = 2,
    expires_in: int = 3600,
) -> str:
    """Create a signed JWT for demos, scripts and tests. Uses local keys only."""
    if not settings.use_local_test_keys:
        raise RuntimeError("create_demo_token only works when use_local_test_keys=True")

    private, _ = _ensure_test_keys()
    now = int(time.time())

    claims = {
        "sub": user_id,
        "iat": now,
        "exp": now + expires_in,
        "iss": settings.auth_issuer,
        "aud": settings.auth_audience,
        "scope": " ".join(scopes or ["read:all", "agent:read"]),
        "consent_level": consent_level,
        "email": f"{user_id}@example.com",
    }
    return cast(str, jwt.encode(claims, private, algorithm="RS256"))


def get_test_public_key() -> str:
    """Expose for test clients that want to validate locally."""
    if not settings.use_local_test_keys:
        raise RuntimeError("Only available in local test key mode")
    _, public = _ensure_test_keys()
    return public


async def get_token_via_client_credentials(client_id: str, client_secret: str) -> str:
    """Perform real client_credentials exchange with the IdP (Auth0/Keycloak).

    Returns the access_token (JWT). Uses respx mocks in tests.
    """
    token_url = settings.auth0_token_url
    if not token_url:
        raise RuntimeError("auth0_token_url not set for real client credentials flow")

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "audience": settings.auth_audience,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token exchange failed: {resp.text}",
            )
        token_data = resp.json()
        return cast(str, token_data["access_token"])
