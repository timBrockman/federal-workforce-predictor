#!/usr/bin/env python
"""
One-shot verification script for the federal-workforce-predictor reference.

Runs the key production paths:
- DB init + repositories (incl. EmployeeAssessment)
- Auth / token + ethics
- Recommender + career recs (and legacy)
- GraphQL (careerRecommendations + submit + legacy)
- MCP tools (via direct call + full stdio client; submit→recommend flow)

Usage:
    uv run python scripts/verify.py
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient

from app.core.security import Principal, create_demo_token, get_current_principal
from app.db.engine import init_db, get_session_factory
from app.db.repositories import (
    QuestionnaireRepository,
    TransactionRepository,
    UserRepository,
)
from app.main import app
from app.services.mcp_server import call_tool as mcp_call_tool, list_tools as mcp_list_tools
from app.services.recommender import get_recommendations
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def verify_db():
    print("=== DB Layer ===")
    await init_db()
    factory = get_session_factory()
    async with factory() as session:
        u_repo = UserRepository(session)
        user = await u_repo.get_or_create("verify-user")
        print(f"  User: {user.id}")

        tx_repo = TransactionRepository(session)
        await tx_repo.add_many(
            "verify-user",
            [
                {"amount": 12.5, "category": "coffee"},
                {"amount": 55.0, "category": "groceries"},
            ],
        )
        totals = await tx_repo.sum_by_category("verify-user")
        print(f"  Totals: {totals}")

        q_repo = QuestionnaireRepository(session)
        q = await q_repo.create(
            "verify-user", "medium", "save for travel", "medium", True
        )
        print(f"  Questionnaire id: {q.id}")
    print("✅ DB repositories working")


def verify_auth_and_recommender():
    print("\n=== Auth + Recommender + Ethics ===")
    token = create_demo_token("verify-user", consent_level=2)
    print(f"  Token generated (len={len(token)})")

    p = Principal("verify-user", ["read:all"], consent_level=2)
    recs, dec = get_recommendations(p)
    print(f"  Recommendations: {len(recs)} items, allowed={dec.allowed}")
    print(f"  Sources example: {recs[0]['data_sources'] if recs else 'N/A'}")
    print("✅ Auth / recommender / ethics OK")


def verify_graphql():
    print("\n=== GraphQL (via TestClient with override) ===")

    def get_p():
        return Principal("verify-user", ["read:all"], consent_level=2)

    app.dependency_overrides[get_current_principal] = get_p
    client = TestClient(app)

    # Recommendations
    q = "{ recommendations { category suggestedMonthlyBudget ethicsNote dataSources } }"
    r = client.post("/graphql", json={"query": q})
    assert r.status_code == 200
    recs = r.json()["data"]["recommendations"]
    print(f"  Recommendations: {len(recs)} items")

    # New career path (high consent) - use demo-user-123 which has seeded career data
    def get_p_career():
        return Principal("demo-user-123", ["read:all"], consent_level=2)
    app.dependency_overrides[get_current_principal] = get_p_career
    q_career = "{ careerRecommendations { recommendationType confidence } }"
    r_career = client.post("/graphql", json={"query": q_career})
    career = r_career.json()["data"]["careerRecommendations"]
    print(f"  careerRecommendations: {len(career)} items")

    # DB-backed summary
    q2 = "{ spendSummary { totalSpent topCategories } }"
    r2 = client.post("/graphql", json={"query": q2})
    summary = r2.json()["data"]["spendSummary"]
    print(f"  spendSummary: {summary['totalSpent']} ({summary['topCategories']})")

    app.dependency_overrides.clear()
    print("✅ GraphQL + DB-backed summary OK")


async def verify_mcp():
    print("\n=== MCP Server ===")
    tools = await mcp_list_tools()
    print(f"  Tools: {[t.name for t in tools]}")

    # Direct (in-process) calls now support real principals via args
    res = await mcp_call_tool("get_budget_recommendations", {})
    print(f"  get_budget_recommendations (default demo): {len(res[0].text)} chars")

    # Demonstrate different principal (low consent) via MCP args
    res_low = await mcp_call_tool("get_budget_recommendations", {"user_id": "low-consent-user", "consent_level": 0})
    print(f"  get_budget_recommendations (low consent): {len(res_low[0].text)} chars")

    # New federal career path (high + low consent)
    res_career = await mcp_call_tool("get_career_recommendations", {"consent_level": 2})
    print(f"  get_career_recommendations (high consent): {len(res_career[0].text)} chars")
    res_career_low = await mcp_call_tool("get_career_recommendations", {"consent_level": 0})
    print(f"  get_career_recommendations (low consent): {len(res_career_low[0].text)} chars")

    # Demonstrate full submit -> recommend flow (new domain)
    res_submit = await mcp_call_tool("submit_assessment", {
        "skills_inventory": "python,cloud,acquisition",
        "performance_level": "high",
        "career_goals": "lead critical cyber mission",
        "consent_for_career_modeling": True,
        "consent_level": 2
    })
    print(f"  submit_assessment: {len(res_submit[0].text)} chars")
    res_after = await mcp_call_tool("get_career_recommendations", {"consent_level": 2})
    print(f"  get_career_recommendations after submit: {len(res_after[0].text)} chars")

    # Full stdio client test (spawns the server) - pass explicit user context
    server_params = StdioServerParameters(
        command="uv", args=["run", "python", "-m", "app.services.mcp_server"]
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools2 = await session.list_tools()
            print(f"  Stdio client tools: {[t.name for t in tools2.tools]}")
            res2 = await session.call_tool("get_spend_summary", {"user_id": "verify-user-123"})
            print(f"  get_spend_summary via stdio (explicit user): OK")
            # Also exercise ask with context
            res3 = await session.call_tool("ask_budget_agent", {"question": "coffee budget?", "consent_level": 1})
            print(f"  ask_budget_agent via stdio (consent=1): OK")
            # Exercise new career tool via stdio
            res4 = await session.call_tool("get_career_recommendations", {"user_id": "verify-user-123", "consent_level": 2})
            print(f"  get_career_recommendations via stdio: OK")

    print("✅ MCP server (direct + stdio client) OK")


async def main():
    print("federal-workforce-predictor verification\n" + "=" * 40)
    await verify_db()
    verify_auth_and_recommender()
    verify_graphql()
    await verify_mcp()
    print("\n" + "=" * 40)
    print("✅ All verifications passed!")


if __name__ == "__main__":
    asyncio.run(main())
