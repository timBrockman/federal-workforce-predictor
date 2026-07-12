#!/usr/bin/env python
"""Seed synthetic demo data (users, questionnaire, sample transactions).

Run after DB migrations (or alongside create_all for dev).

Usage:
    uv run python scripts/seed_demo_data.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.db.engine import init_db, get_session_factory
from app.db.repositories import (
    ConsentRepository,
    QuestionnaireRepository,
    TransactionRepository,
    UserRepository,
    EmployeeAssessmentRepository,
    CareerSignalRepository,
)


async def main() -> None:
    print("Seeding demo data (synthetic profiles + sample transactions)...")

    await init_db()

    factory = get_session_factory()
    async with factory() as session:
        u_repo = UserRepository(session)
        user = await u_repo.get_or_create("demo-user-123")
        print(f"  User: {user.id}")

        tx_repo = TransactionRepository(session)
        # Idempotent-ish: only seed if none
        existing = await tx_repo.list_for_user("demo-user-123", limit=1)
        if not existing:
            demo_txs = [
                {"amount": 12.5, "category": "coffee", "description": "Daily latte"},
                {"amount": 45.0, "category": "groceries", "description": "Weekly shop"},
                {"amount": 8.99, "category": "coffee", "description": "Espresso"},
                {"amount": 120.0, "category": "transport", "description": "Monthly pass"},
                {"amount": 67.3, "category": "groceries"},
            ]
            await tx_repo.add_many("demo-user-123", demo_txs)
            print("  Seeded demo transactions")

        q_repo = QuestionnaireRepository(session)
        q = await q_repo.create(
            user_id="demo-user-123",
            income_bracket="medium",
            goals="save for travel and reduce coffee spending",
            risk_tolerance="medium",
            has_social_consent=True,
            raw_answers={"income_bracket": "medium", "goals": "save"},
        )
        print(f"  Questionnaire id: {q.id}")

        c_repo = ConsentRepository(session)
        await c_repo.record_consent(
            user_id="demo-user-123",
            purpose="synthetic_social_for_budget_recs",
            granted=True,
            level=2,
        )
        print("  Consent recorded")

        # --- New federal workforce domain seeding (additive for pivot) ---
        assess_repo = EmployeeAssessmentRepository(session)
        existing_assess = await assess_repo.get_latest_for_user("demo-user-123")
        if not existing_assess:
            assess = await assess_repo.create(
                user_id="demo-user-123",
                skills_inventory="python,cloud,leadership,cyber",
                performance_level="high",
                career_goals="lead critical cyber mission team",
                critical_role_interest=True,
                consent_for_career_modeling=True,
                raw_answers={"skills": "python,cloud", "goals": "mission leadership"},
            )
            print(f"  EmployeeAssessment id: {assess.id}")

        sig_repo = CareerSignalRepository(session)
        # Simple check: seed signals only if we just created assessment (rough idempotency for demo)
        if not existing_assess:
            demo_signals = [
                {"signal_type": "training", "value": "advanced cloud cert"},
                {"signal_type": "mobility", "value": "internal transfer to cyber"},
                {"signal_type": "cert", "value": "CISSP"},
            ]
            await sig_repo.add_many("demo-user-123", demo_signals)
            print("  Career signals seeded (synthetic)")

    print("✅ Demo data seeded (or was already present)")


if __name__ == "__main__":
    asyncio.run(main())
