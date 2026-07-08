#!/usr/bin/env python
"""
One-shot verification script for the customer-spend-microservice template.

Runs the key production paths:
- DB init + repositories
- Auth / token
- Recommender + ethics
- GraphQL (recommendations + spendSummary)
- MCP tools (via direct call + full stdio client)

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

    print("✅ MCP server (direct + stdio client) OK")


async def main():
    print("customer-spend-microservice verification\n" + "=" * 40)
    await verify_db()
    verify_auth_and_recommender()
    verify_graphql()
    await verify_mcp()
    print("\n" + "=" * 40)
    print("✅ All verifications passed!")


if __name__ == "__main__":
    asyncio.run(main())
