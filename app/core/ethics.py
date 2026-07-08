"""Ethics as first-class cross-cutting concern.

Demonstrates production patterns for guardrailed AI:
- Consent modeling
- Data source transparency
- Refusal / graceful degradation
- Decision audit logging (EthicalDecisionLog)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from app.core.security import Principal

# Lazy to avoid circulars / heavy import at module load for all paths
def _get_ethics_repo_session():
    from app.db.engine import get_session_factory
    from app.db.repositories import EthicsLogRepository
    return get_session_factory, EthicsLogRepository


class DataClassification(str, Enum):
    PUBLIC = "public"
    PII = "pii"
    SENSITIVE_INFERENCE = "sensitive_inference"


class DecisionType(str, Enum):
    RECOMMENDATION = "recommendation"
    AGENT_RESPONSE = "agent_response"
    SOCIAL_USE = "social_use"


@dataclass
class EthicalDecision:
    decision_type: DecisionType
    user_id: str
    allowed: bool
    reason: str
    data_sources: list[str] = field(default_factory=list)
    classification: DataClassification = DataClassification.PUBLIC
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)


class EthicalPolicy:
    """Central policy engine. Easy to extend / audit."""

    @staticmethod
    def check_consent_for_social(principal: Principal) -> tuple[bool, str]:
        if principal.has_consent_for_social():
            return True, "Consent present for synthetic social signals"
        return False, "No consent for social-derived insights. Set consent_level >= 2 or provide explicit consent."

    @staticmethod
    def require_sources_transparency(
        sources: list[str], principal: Principal
    ) -> tuple[bool, str]:
        if not sources:
            return False, "No data sources declared - violating transparency requirement"
        return True, f"Using sources: {', '.join(sources)}"

    @staticmethod
    def refuse_unethical_request(query: str, principal: Principal) -> tuple[bool, str]:
        q = query.lower()
        bad_keywords = ["discriminat", "target poor", "exclude based on", "illegal", "harm "]
        if any(kw in q for kw in bad_keywords):
            return False, "Request appears to seek unethical or discriminatory use of financial data."
        return True, "Request passed basic ethics pre-filter"

    @staticmethod
    def evaluate_recommendation(
        principal: Principal, sources: list[str], context: dict[str, Any]
    ) -> EthicalDecision:
        allowed, reason = EthicalPolicy.check_consent_for_social(principal)
        if not allowed:
            return EthicalDecision(
                decision_type=DecisionType.RECOMMENDATION,
                user_id=principal.user_id,
                allowed=False,
                reason=reason,
                data_sources=sources,
            )

        ok, msg = EthicalPolicy.require_sources_transparency(sources, principal)
        if not ok:
            return EthicalDecision(
                DecisionType.RECOMMENDATION, principal.user_id, False, msg, sources
            )

        return EthicalDecision(
            decision_type=DecisionType.RECOMMENDATION,
            user_id=principal.user_id,
            allowed=True,
            reason=msg,
            data_sources=sources,
            classification=DataClassification.SENSITIVE_INFERENCE if "social" in sources else DataClassification.PUBLIC,
        )


# Simple in-memory log for the template (in prod -> DB table)
_ETHICS_LOG: list[EthicalDecision] = []


def log_decision(decision: EthicalDecision) -> None:
    _ETHICS_LOG.append(decision)
    # In real system also persist via repository to EthicalDecisionLog


async def persist_decision(decision: EthicalDecision) -> None:
    """Best-effort persist of an EthicalDecision to the DB audit log.

    Used in async paths (GraphQL, MCP, agent). Failures are swallowed so they
    never impact the primary user experience.
    """
    try:
        get_session_factory, EthicsLogRepository = _get_ethics_repo_session()
        factory = get_session_factory()
        async with factory() as session:
            repo = EthicsLogRepository(session)
            await repo.log(
                {
                    "user_id": decision.user_id,
                    "decision_type": (
                        decision.decision_type.value
                        if isinstance(decision.decision_type, Enum)
                        else str(decision.decision_type)
                    ),
                    "allowed": decision.allowed,
                    "reason": decision.reason,
                    "data_sources": list(decision.data_sources or []),
                    "classification": (
                        decision.classification.value
                        if isinstance(decision.classification, Enum)
                        else str(decision.classification)
                    ),
                    "metadata": dict(decision.metadata or {}),
                }
            )
    except Exception:
        # Never let audit logging break the request in the template
        pass


def get_recent_decisions(limit: int = 20) -> list[EthicalDecision]:
    return list(reversed(_ETHICS_LOG[-limit:]))


def clear_log_for_tests() -> None:
    _ETHICS_LOG.clear()
