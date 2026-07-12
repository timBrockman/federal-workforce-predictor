"""Guardrailed agent (originally for budget questions).

Evolving to support federal workforce / employee lifecycle queries
(e.g. career trajectory, skill gaps, critical role readiness).

Uses LiteLLM abstraction (default Ollama in template).
Tools are safe wrappers around other services.
Ethics enforced before and after.
"""

from __future__ import annotations

from typing import Any

from app.core.ethics import EthicalDecision, EthicalPolicy, log_decision, persist_decision
from app.core.security import Principal
from app.services.recommender import get_recommendations, get_career_recommendations


async def ask_budget_agent(
    principal: Principal, question: str, context: dict[str, Any] | None = None
) -> dict[str, Any]:
    # Pre-filter
    allowed, reason = EthicalPolicy.refuse_unethical_request(question, principal)
    if not allowed:
        decision = EthicalDecision(
            decision_type="agent_response",
            user_id=principal.user_id,
            allowed=False,
            reason=reason,
            data_sources=["user_query"],
        )
        log_decision(decision)
        return {
            "answer": "I cannot assist with that request as it may violate our ethical guidelines.",
            "sources_used": [],
            "ethical_decision": reason,
        }

    # In real: call pydantic-ai agent with tools
    # For template we simulate with rules + recs call
    recs, rec_decision = get_recommendations(principal, context)
    answer = f"Based on your profile, consider these adjustments: {recs}. "

    if not principal.has_consent_for_social():
        answer += " (Note: social signals were not used because consent was not granted.)"

    # Small federal pivot integration (career recs when relevant)
    career_recs, _ = get_career_recommendations(principal, context)
    if career_recs:
        answer += f" Career readiness notes: {career_recs}."

    sources = ["questionnaire"]
    if principal.has_consent_for_social():
        sources.append("synthetic_social")
    if career_recs and principal.has_consent_for_social():
        sources.append("synthetic_career_signals")

    decision = EthicalDecision(
        "agent_response",
        principal.user_id,
        True,
        "Passed ethics pre-filter and used declared sources.",
        data_sources=sources,
    )
    log_decision(decision)
    # Phase 2: also persist for audit
    # (fire and forget in this context; await in callers if top level)
    import asyncio
    try:
        asyncio.create_task(persist_decision(decision))
    except RuntimeError:
        # no running loop in some contexts; caller will handle
        pass

    return {
        "answer": answer,
        "sources_used": decision.data_sources,
        "ethical_decision": decision.reason,
        "follow_up_questions": ["Would you like to adjust a category?"],
    }
