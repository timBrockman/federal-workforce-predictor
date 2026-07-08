"""Pytest configuration and fixtures for the customer-spend-api template.

Provides reusable authenticated clients and principal overrides.
"""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.core.security import Principal, get_current_principal


@pytest.fixture
def auth_principal():
    """Default authenticated principal with social consent for tests."""
    return Principal(
        user_id="demo-user-123",
        scopes=["read:all", "agent:read"],
        consent_level=2,
    )


@pytest.fixture
def client(auth_principal):
    """TestClient with principal dependency overridden."""
    def _get_principal():
        return auth_principal

    app.dependency_overrides[get_current_principal] = _get_principal
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()


@pytest.fixture
def no_consent_principal():
    return Principal(user_id="demo-user-123", scopes=["read:all"], consent_level=0)


@pytest.fixture
def no_consent_client(no_consent_principal):
    def _get_principal():
        return no_consent_principal

    app.dependency_overrides[get_current_principal] = _get_principal
    c = TestClient(app)
    yield c
    app.dependency_overrides.clear()
