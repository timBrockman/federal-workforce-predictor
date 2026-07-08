"""Flat GraphQL types - deliberately limited to avoid nesting problems."""

import strawberry
from typing import Optional


@strawberry.type
class BudgetRecommendation:
    category: str
    suggested_monthly_budget: float
    confidence: float
    rationale: str
    data_sources: list[str]
    ethics_note: str


@strawberry.type
class AgentResponse:
    answer: str
    sources_used: list[str]
    ethical_decision: str
    follow_up_questions: list[str] = strawberry.field(default_factory=list)


@strawberry.type
class SpendSummary:
    total_spent: float
    top_categories: list[str]
    month: str


@strawberry.input
class QuestionnaireInput:
    income_bracket: str
    goals: str
    risk_tolerance: str
    consent_social: bool = False


@strawberry.type
class MutationResult:
    success: bool
    message: str
