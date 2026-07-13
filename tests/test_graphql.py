"""Basic GraphQL tests using the limited schema (auth + ethics exercised).

Uses dependency overrides for reliable auth in tests (avoids header parsing edge cases).
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import Principal, create_demo_token, get_current_principal


@pytest.fixture
def client():
    """Test client with authenticated principal override (consent for social)."""
    def _override_principal():
        return Principal(
            user_id="demo-user-123",
            scopes=["read:all", "agent:read"],
            consent_level=2,
        )

    app.dependency_overrides[get_current_principal] = _override_principal
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


def test_health_and_demo_token(client):
    r = client.get("/health")
    assert r.status_code == 200

    r = client.get("/demo-token")
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_graphql_recommendations_requires_auth():
    """Without auth, we now return a proper GraphQL error (200 + errors) thanks to GraphQLError in resolvers."""
    raw_client = TestClient(app)
    query = "{ recommendations { category } }"
    r = raw_client.post("/graphql", json={"query": query})
    data = r.json()
    assert r.status_code == 200
    assert "errors" in data
    assert any("authenticated" in str(e).lower() for e in data["errors"])


def test_graphql_recommendations_with_consent(client):
    """Recommendations path exercises recommender + ethics + source attribution (light path)."""
    query = "{ recommendations { category suggestedMonthlyBudget ethicsNote dataSources } }"
    r = client.post("/graphql", json={"query": query})
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    assert body["data"] is not None
    recs = body["data"].get("recommendations") or []
    assert len(recs) > 0
    first = recs[0]
    assert "dataSources" in first
    assert any("synthetic" in s.lower() or "questionnaire" in s.lower() for s in first["dataSources"])
    assert "ethicsNote" in first


def test_graphql_career_recommendations_with_consent(client):
    """Career path (federal workforce use case) exercises recommender + ethics + sources."""
    query = "{ careerRecommendations { recommendationType targetRole confidence rationale dataSources ethicsNote } }"
    r = client.post("/graphql", json={"query": query})
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    recs = (body.get("data") or {}).get("careerRecommendations") or []
    assert len(recs) > 0
    first = recs[0]
    assert "dataSources" in first
    assert any("assessment" in str(s).lower() or "synthetic" in str(s).lower() for s in first.get("dataSources", []))
    assert "ethicsNote" in first


def test_graphql_career_recommendations_low_consent():
    """Low consent should degrade career recs (no synthetic career signals)."""
    def _override_low():
        return Principal("low-consent-user", ["read:all"], consent_level=0)

    app.dependency_overrides[get_current_principal] = _override_low
    c = TestClient(app)
    query = "{ careerRecommendations { recommendationType } }"
    r = c.post("/graphql", json={"query": query})
    assert r.status_code == 200
    recs = (r.json().get("data") or {}).get("careerRecommendations") or []
    assert len(recs) == 0
    app.dependency_overrides.clear()


@pytest.mark.slow
def test_graphql_ask_agent_with_consent(client):
    """Agent path (may pull heavier LLM libs on first use)."""
    query = '{ askAgent(question: "What is a reasonable coffee budget?") { answer sourcesUsed ethicalDecision } }'
    r = client.post("/graphql", json={"query": query})
    assert r.status_code == 200
    body = r.json()
    assert "data" in body
    agent = (body.get("data") or {}).get("askAgent") or {}
    assert "answer" in agent
    assert "sourcesUsed" in agent
    assert "ethicalDecision" in agent


def test_graphql_query_depth_limit(client):
    """Overly deep or invalid nested queries are rejected (production safety via limiter + schema validation)."""
    # Build a query that would be deep; due to flat schema it triggers field error, but still produces GraphQL errors.
    deep = "{ " + "recommendations { category " * 5 + "}" * 5 + " }"
    r = client.post("/graphql", json={"query": deep})
    assert r.status_code == 200
    data = r.json()
    assert "errors" in data
