"""Async repositories for the (legacy spend +) federal workforce domain.

These provide the data access layer. Services depend on these (not directly on models/engine).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CareerSignal,
    ConsentRecord,
    EmployeeAssessment,
    EthicalDecisionLog,
    QuestionnaireResponse,
    SpendTransaction,
    User,
)


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, user_id: str) -> User:
        result = await self.session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if user is None:
            user = User(id=user_id)
            self.session.add(user)
            await self.session.commit()
            await self.session.refresh(user)
        return user


class QuestionnaireRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: str,
        income_bracket: str,
        goals: str,
        risk_tolerance: str,
        has_social_consent: bool,
        raw_answers: dict[str, Any] | None = None,
    ) -> QuestionnaireResponse:
        q = QuestionnaireResponse(
            user_id=user_id,
            income_bracket=income_bracket,
            goals=goals,
            risk_tolerance=risk_tolerance,
            has_social_consent=has_social_consent,
            raw_answers=raw_answers or {},
        )
        self.session.add(q)
        await self.session.commit()
        await self.session.refresh(q)
        return q

    async def get_latest_for_user(self, user_id: str) -> QuestionnaireResponse | None:
        result = await self.session.execute(
            select(QuestionnaireResponse)
            .where(QuestionnaireResponse.user_id == user_id)
            .order_by(QuestionnaireResponse.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class TransactionRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_many(
        self, user_id: str, transactions: list[dict[str, Any]]
    ) -> list[SpendTransaction]:
        objs = [
            SpendTransaction(
                user_id=user_id,
                amount=t["amount"],
                category=t["category"],
                occurred_at=t.get("occurred_at", datetime.utcnow()),
                description=t.get("description"),
            )
            for t in transactions
        ]
        self.session.add_all(objs)
        await self.session.commit()
        for o in objs:
            await self.session.refresh(o)
        return objs

    async def list_for_user(self, user_id: str, limit: int = 100) -> list[SpendTransaction]:
        result = await self.session.execute(
            select(SpendTransaction)
            .where(SpendTransaction.user_id == user_id)
            .order_by(SpendTransaction.occurred_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def sum_by_category(self, user_id: str) -> dict[str, float]:
        # Simple in-memory aggregation for template (real would use group_by)
        txs = await self.list_for_user(user_id, limit=1000)
        totals: dict[str, float] = {}
        for t in txs:
            totals[t.category] = totals.get(t.category, 0.0) + t.amount
        return totals


class ConsentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_consent(
        self, user_id: str, purpose: str, granted: bool, level: int
    ) -> ConsentRecord:
        rec = ConsentRecord(user_id=user_id, purpose=purpose, granted=granted, level=level)
        self.session.add(rec)
        await self.session.commit()
        await self.session.refresh(rec)
        return rec


class EthicsLogRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log(self, decision: dict[str, Any]) -> EthicalDecisionLog:
        log = EthicalDecisionLog(
            user_id=decision["user_id"],
            decision_type=decision["decision_type"],
            allowed=decision["allowed"],
            reason=decision["reason"],
            data_sources=decision.get("data_sources", []),
            classification=decision.get("classification", "public"),
            metadata_json=decision.get("metadata", {}),
        )
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log


# =============================================================================
# New repositories for federal workforce domain (added incrementally)
# =============================================================================


class EmployeeAssessmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        user_id: str,
        skills_inventory: str,
        performance_level: str,
        career_goals: str,
        critical_role_interest: bool = False,
        consent_for_career_modeling: bool = False,
        raw_answers: dict[str, Any] | None = None,
    ) -> EmployeeAssessment:
        assessment = EmployeeAssessment(
            user_id=user_id,
            skills_inventory=skills_inventory,
            performance_level=performance_level,
            career_goals=career_goals,
            critical_role_interest=critical_role_interest,
            consent_for_career_modeling=consent_for_career_modeling,
            raw_answers=raw_answers or {},
        )
        self.session.add(assessment)
        await self.session.commit()
        await self.session.refresh(assessment)
        return assessment

    async def get_latest_for_user(self, user_id: str) -> EmployeeAssessment | None:
        result = await self.session.execute(
            select(EmployeeAssessment)
            .where(EmployeeAssessment.user_id == user_id)
            .order_by(EmployeeAssessment.created_at.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()


class CareerSignalRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_many(self, user_id: str, signals: list[dict[str, Any]]) -> list[CareerSignal]:
        objs = [
            CareerSignal(
                user_id=user_id,
                signal_type=s["signal_type"],
                value=s["value"],
                occurred_at=s.get("occurred_at", datetime.utcnow()),
                source=s.get("source", "synthetic"),
            )
            for s in signals
        ]
        self.session.add_all(objs)
        await self.session.commit()
        for o in objs:
            await self.session.refresh(o)
        return objs
