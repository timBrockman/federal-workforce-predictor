"""Recommender service.

Uses questionnaire + synthetic social (mocked) + optional scikit-learn.

All outputs go through EthicalPolicy and declare sources.
"""

from __future__ import annotations

from typing import Any

from app.core.ethics import EthicalDecision, EthicalPolicy, log_decision
from app.core.security import Principal

# Synthetic interest profiles (seeded, versioned for reproducibility)
SYNTHETIC_PROFILES: dict[str, list[str]] = {
    "demo-user-123": ["coffee", "tech gadgets", "travel", "fitness"],
    "user-ethics-test": ["fast food", "gaming"],
}


def _get_synthetic_interests(user_id: str) -> list[str]:
    return SYNTHETIC_PROFILES.get(user_id, ["general lifestyle"])


def get_recommendations(
    principal: Principal,
    questionnaire: dict[str, Any] | None = None,
) -> tuple[list[dict[str, Any]], EthicalDecision]:
    sources = ["questionnaire"]
    interests = _get_synthetic_interests(principal.user_id)
    if principal.has_consent_for_social():
        sources.append("synthetic_social")

    # Simple rules + (future) scikit path
    recs: list[dict[str, Any]] = []
    if "coffee" in interests:
        recs.append({
            "category": "coffee",
            "suggested_monthly_budget": 45.0,
            "confidence": 0.82,
            "rationale": "High interest signal + moderate income bracket",
        })
    recs.append({
        "category": "groceries",
        "suggested_monthly_budget": 280.0 if questionnaire and "medium" in str(questionnaire.get("income_bracket", "")).lower() else 320.0,
        "confidence": 0.91,
        "rationale": "Core need derived from questionnaire",
    })

    decision = EthicalPolicy.evaluate_recommendation(principal, sources, {"interests": interests})
    log_decision(decision)

    if not decision.allowed:
        # degrade
        return [], decision

    # attach sources + ethics note
    for r in recs:
        r["data_sources"] = sources
        r["ethics_note"] = decision.reason

    return recs, decision
