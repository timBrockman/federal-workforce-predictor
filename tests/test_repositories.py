"""Unit tests for repositories (Phase 1 of complete test coverage)."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.engine import get_session_factory
from app.db.repositories import (
    ConsentRepository,
    EthicsLogRepository,
    QuestionnaireRepository,
    TransactionRepository,
    UserRepository,
)


@pytest.fixture
async def db_session():
    """Provide a fresh async session for repo tests."""
    from app.db.engine import get_engine
    from app.db.models import Base
    from sqlalchemy import text

    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    factory = get_session_factory()
    async with factory() as session:
        await session.execute(text("PRAGMA foreign_keys=ON"))
        yield session
        await session.rollback()


@pytest.mark.asyncio
async def test_user_repo_get_or_create(db_session: AsyncSession):
    repo = UserRepository(db_session)
    user = await repo.get_or_create("test-user-1")
    assert user.id == "test-user-1"

    user2 = await repo.get_or_create("test-user-1")
    assert user2.id == "test-user-1"


@pytest.mark.asyncio
async def test_questionnaire_repo(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    await user_repo.get_or_create("u1")

    repo = QuestionnaireRepository(db_session)
    q = await repo.create(
        user_id="u1",
        income_bracket="high",
        goals="save",
        risk_tolerance="low",
        has_social_consent=True,
    )
    assert q.user_id == "u1"

    latest = await repo.get_latest_for_user("u1")
    assert latest is not None


@pytest.mark.asyncio
async def test_transaction_repo(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    await user_repo.get_or_create("u2")

    repo = TransactionRepository(db_session)
    txs = await repo.add_many(
        "u2",
        [
            {"amount": 10.5, "category": "coffee", "description": "latte"},
            {"amount": 50.0, "category": "groceries"},
        ],
    )
    assert len(txs) == 2

    listed = await repo.list_for_user("u2")
    assert len(listed) >= 2

    totals = await repo.sum_by_category("u2")
    assert "coffee" in totals


@pytest.mark.asyncio
async def test_consent_repo(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    await user_repo.get_or_create("u3")

    repo = ConsentRepository(db_session)
    rec = await repo.record_consent(
        user_id="u3", purpose="test", granted=True, level=2
    )
    assert rec.user_id == "u3"


@pytest.mark.asyncio
async def test_ethics_log_repo(db_session: AsyncSession):
    user_repo = UserRepository(db_session)
    await user_repo.get_or_create("u4")

    repo = EthicsLogRepository(db_session)
    decision = {
        "user_id": "u4",
        "decision_type": "test",
        "allowed": False,
        "reason": "test refusal",
        "data_sources": ["questionnaire"],
    }
    log = await repo.log(decision)
    assert log.user_id == "u4"
