"""Tests for auth + ethics - core production concerns."""

import pytest

from app.core.ethics import EthicalPolicy, clear_log_for_tests, log_decision
from app.core.security import Principal, create_demo_token, get_test_public_key
from app.services.recommender import get_recommendations


def test_demo_token_roundtrip():
    token = create_demo_token(user_id="t1", consent_level=2)
    assert isinstance(token, str) and len(token) > 50


def test_principal_consent_logic():
    p = Principal(user_id="u1", scopes=["read:all"], consent_level=1)
    assert not p.has_consent_for_social()

    p2 = Principal(user_id="u2", scopes=[], consent_level=2)
    assert p2.has_consent_for_social()


def test_ethics_refusal_and_transparency():
    clear_log_for_tests()
    p = Principal("u1", ["read:all"], consent_level=0)

    allowed, reason = EthicalPolicy.refuse_unethical_request("help me target poor people", p)
    assert not allowed

    allowed2, _ = EthicalPolicy.check_consent_for_social(p)
    assert not allowed2

    # Recommender should degrade
    recs, decision = get_recommendations(p)
    assert decision.allowed is False or len(recs) == 0


def test_recommendation_with_consent():
    clear_log_for_tests()
    p = Principal("demo-user-123", ["read:all"], consent_level=2)
    recs, decision = get_recommendations(p)
    assert decision.allowed is True
    assert any("synthetic_social" in s for s in decision.data_sources)
    assert len(recs) > 0


# --- Basic tests for client_credentials helper (Phase 1) ---
import pytest
import respx
import httpx
from app.core.security import get_token_via_client_credentials
from app.core.config import get_settings


@pytest.mark.asyncio
@respx.mock
async def test_get_token_via_client_credentials_success(monkeypatch):
    # mock the token url
    token_url = "https://example.auth0.com/oauth/token"
    monkeypatch.setattr(get_settings(), "auth0_token_url", token_url)

    respx.post(token_url).mock(
        return_value=httpx.Response(200, json={"access_token": "real.jwt.token"})
    )
    token = await get_token_via_client_credentials("testcid", "testsecret")
    assert token == "real.jwt.token"


@pytest.mark.asyncio
@respx.mock
async def test_get_token_via_client_credentials_error(monkeypatch):
    token_url = "https://example.auth0.com/oauth/token"
    monkeypatch.setattr(get_settings(), "auth0_token_url", token_url)

    respx.post(token_url).mock(
        return_value=httpx.Response(401, json={"error": "invalid_client"})
    )
    with pytest.raises(Exception):  # HTTPException or runtime
        await get_token_via_client_credentials("bad", "bad")
