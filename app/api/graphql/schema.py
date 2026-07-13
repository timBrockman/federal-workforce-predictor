"""Strawberry schema - deliberately flat and limited."""

from typing import Any

import strawberry
from graphql import GraphQLError
from strawberry.extensions import QueryDepthLimiter, SchemaExtension
from strawberry.types import Info

from app.api.graphql import types as gql_types
from app.core.config import get_settings
from app.core.ethics import persist_decision
from app.core.security import Principal
from app.db.engine import get_session_factory
from app.db.repositories import EmployeeAssessmentRepository, TransactionRepository
from app.services.recommender import get_career_recommendations, get_recommendations

settings = get_settings()


class QueryLimitExtension(SchemaExtension):
    """Simple production-grade guard against deep nesting and expensive queries.

    Uses settings.graphql_max_query_depth and graphql_max_query_cost.
    This is a lightweight version; real systems often use graphql-query-complexity.
    """

    def on_execute(self) -> None:  # type: ignore[override]
        # Enforce limits on the parsed document (runs for every operation)
        document = getattr(self.execution_context, "graphql_document", None)
        if not document:
            return

        max_depth = settings.graphql_max_query_depth
        max_cost = settings.graphql_max_query_cost

        def calc(node: object, depth: int = 0) -> int:
            if depth > max_depth:
                raise GraphQLError(f"Query too deep (max depth {max_depth})")
            cost = 1
            selections = getattr(getattr(node, "selection_set", None), "selections", []) or []
            for selection in selections:
                cost += calc(selection, depth + 1)
            return cost

        for definition in getattr(document, "definitions", []):
            total_cost = calc(definition)
            if total_cost > max_cost:
                raise GraphQLError(f"Query too expensive (cost {total_cost} > {max_cost})")


# Lazy import for the heavy agent (Pydantic AI + LLM libs) to keep app startup light
def _ask_budget_agent(principal: Principal, question: str) -> Any:
    from app.services.agent import ask_budget_agent as _impl

    return _impl(principal, question)


@strawberry.type
class Query:
    @strawberry.field
    async def health(self) -> str:
        return "ok"

    @strawberry.field
    async def career_recommendations(self, info: Info) -> list[gql_types.CareerRecommendation]:
        """New flat field for federal workforce career recommendations."""
        principal: Principal | None = info.context.get("principal")
        if not principal:
            raise GraphQLError("Not authenticated", extensions={"code": "UNAUTHENTICATED"})

        # Fetch latest assessment so recommender uses real submitted data (not only synthetic)
        assessment = None
        factory = get_session_factory()
        async with factory() as session:
            a_repo = EmployeeAssessmentRepository(session)
            assess = await a_repo.get_latest_for_user(principal.user_id)
            if assess:
                assessment = {"skills_inventory": assess.skills_inventory}

        recs, decision = get_career_recommendations(principal, assessment)

        await persist_decision(decision)

        if not decision.allowed:
            return []

        return [
            gql_types.CareerRecommendation(
                recommendation_type=r["recommendation_type"],
                target_role=r.get("target_role"),
                suggested_action=r.get("suggested_action"),
                confidence=r["confidence"],
                rationale=r["rationale"],
                data_sources=r["data_sources"],
                ethics_note=r.get("ethics_note", decision.reason),
            )
            for r in recs
        ]

    # Legacy spend path (kept for reference during pivot;
    # new federal paths are career_* and submit_assessment)
    @strawberry.field
    async def spend_summary(self, info: Info) -> gql_types.SpendSummary:
        principal: Principal | None = info.context.get("principal")
        if not principal:
            raise GraphQLError("Not authenticated", extensions={"code": "UNAUTHENTICATED"})

        factory = get_session_factory()
        async with factory() as session:
            repo = TransactionRepository(session)
            totals = await repo.sum_by_category(principal.user_id)
            if not totals:
                # Fallback demo data if no transactions yet
                totals = {"groceries": 450.0, "coffee": 85.5, "transport": 120.0}
            sorted_cats = sorted(totals.items(), key=lambda x: -x[1])[:3]
            top = [c for c, _ in sorted_cats]
            total = sum(totals.values())

        return gql_types.SpendSummary(
            total_spent=round(total, 2),
            top_categories=top,
            month="2026-06",
        )

    # Legacy spend recommendations (kept during pivot)
    @strawberry.field
    async def recommendations(
        self, info: Info, income_bracket: str | None = None
    ) -> list[gql_types.BudgetRecommendation]:
        principal: Principal | None = info.context.get("principal")
        if not principal:
            raise GraphQLError("Not authenticated", extensions={"code": "UNAUTHENTICATED"})

        recs, decision = get_recommendations(
            principal, {"income_bracket": income_bracket or "medium"}
        )

        # Phase 2: persist ethics decision for audit trail
        await persist_decision(decision)

        if not decision.allowed:
            # Return empty with note? Or raise policy error. For demo return with note.
            return []

        return [
            gql_types.BudgetRecommendation(
                category=r["category"],
                suggested_monthly_budget=r["suggested_monthly_budget"],
                confidence=r["confidence"],
                rationale=r["rationale"],
                data_sources=r["data_sources"],
                ethics_note=r.get("ethics_note", decision.reason),
            )
            for r in recs
        ]

    @strawberry.field
    async def ask_agent(self, info: Info, question: str) -> gql_types.AgentResponse:
        principal: Principal | None = info.context.get("principal")
        if not principal:
            raise GraphQLError("Not authenticated", extensions={"code": "UNAUTHENTICATED"})

        result = await _ask_budget_agent(principal, question)
        # Note: agent already attempts persist via create_task; we can also ensure here if needed.
        # For now the internal one covers it.
        return gql_types.AgentResponse(
            answer=result["answer"],
            sources_used=result["sources_used"],
            ethical_decision=result["ethical_decision"],
            follow_up_questions=result.get("follow_up_questions", []),
        )


@strawberry.type
class Mutation:
    # Legacy submit (kept during pivot; use submit_assessment for new domain)
    @strawberry.mutation
    async def submit_questionnaire(
        self, info: Info, input: gql_types.QuestionnaireInput
    ) -> gql_types.MutationResult:
        principal: Principal | None = info.context.get("principal")
        if not principal:
            raise GraphQLError("Not authenticated", extensions={"code": "UNAUTHENTICATED"})

        from app.db.engine import get_session_factory
        from app.db.repositories import ConsentRepository, QuestionnaireRepository

        factory = get_session_factory()
        async with factory() as session:
            q_repo = QuestionnaireRepository(session)
            await q_repo.create(
                user_id=principal.user_id,
                income_bracket=input.income_bracket,
                goals=input.goals,
                risk_tolerance=input.risk_tolerance,
                has_social_consent=input.consent_social,
                raw_answers={"income_bracket": input.income_bracket, "goals": input.goals},
            )

            if input.consent_social:
                c_repo = ConsentRepository(session)
                await c_repo.record_consent(
                    user_id=principal.user_id,
                    purpose="synthetic_social_for_budget_recs",
                    granted=True,
                    level=2,
                )

        return gql_types.MutationResult(
            success=True,
            message=f"Questionnaire recorded. Social consent: {input.consent_social}",
        )

    @strawberry.mutation
    async def submit_assessment(
        self, info: Info, input: gql_types.AssessmentInput
    ) -> gql_types.MutationResult:
        principal: Principal | None = info.context.get("principal")
        if not principal:
            raise GraphQLError("Not authenticated", extensions={"code": "UNAUTHENTICATED"})

        from app.db.engine import get_session_factory
        from app.db.repositories import ConsentRepository, EmployeeAssessmentRepository

        factory = get_session_factory()
        async with factory() as session:
            a_repo = EmployeeAssessmentRepository(session)
            await a_repo.create(
                user_id=principal.user_id,
                skills_inventory=input.skills_inventory,
                performance_level=input.performance_level,
                career_goals=input.career_goals,
                critical_role_interest=input.critical_role_interest,
                consent_for_career_modeling=input.consent_for_career_modeling,
                raw_answers={
                    "skills_inventory": input.skills_inventory,
                    "career_goals": input.career_goals,
                },
            )

            if input.consent_for_career_modeling:
                c_repo = ConsentRepository(session)
                await c_repo.record_consent(
                    user_id=principal.user_id,
                    purpose="career_modeling",
                    granted=True,
                    level=2,
                )

        return gql_types.MutationResult(
            success=True,
            message=f"Assessment recorded. Career consent: {input.consent_for_career_modeling}",
        )


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=[
        lambda: QueryLimitExtension(),
        lambda: QueryDepthLimiter(max_depth=settings.graphql_max_query_depth),
    ],
    # Custom extension also adds cost limiting and custom messages
)
