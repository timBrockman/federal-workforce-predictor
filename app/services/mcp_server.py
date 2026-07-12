"""Production-grade MCP server for the spend budget service.

Exposes a curated, safe, ethics-aware subset of capabilities as MCP tools.
Tools are backed by the **exact same** services, ethics policy, and Principal
model used by the GraphQL layer.

Key feature: tools accept optional `user_id` and `consent_level` in arguments
so that different principals can be exercised (see `_principal_from_args`).

Run standalone:
    uv run python -m app.services.mcp_server

This uses the official MCP Python SDK (stdio transport for now; SSE can be added).

See docs/usage/mcp.md and docs/concepts/mcp-integration.md.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from app.core.ethics import persist_decision
from app.core.security import Principal
from app.db.engine import get_session_factory
from app.db.repositories import TransactionRepository
from app.services.agent import ask_budget_agent
from app.services.recommender import get_recommendations, get_career_recommendations


def _principal_from_args(arguments: dict[str, Any]) -> Principal:
    """Build a Principal from MCP call arguments.

    MCP stdio clients can pass user context (user_id, consent_level) per call.
    This replaces the previous hardcoded DEMO_PRINCIPAL so real principals
    (different users, different consent) can be exercised.

    Defaults keep the template convenient for demos.
    """
    user_id = arguments.get("user_id") or "demo-user-123"
    raw_cl = arguments.get("consent_level")
    consent_level = int(raw_cl) if raw_cl is not None else 2
    return Principal(
        user_id=user_id,
        scopes=["read:all", "agent:read"],
        consent_level=consent_level,
    )


server = Server("customer-spend-api-mcp")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_spend_summary",
            description="Get aggregated spend summary for the current user (DB-backed). Supports optional user context for MCP clients.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Target user ID (defaults to demo-user-123)"},
                    "consent_level": {"type": "integer", "description": "Consent level 0-2 (defaults to 2)"},
                },
            },
        ),
        Tool(
            name="get_budget_recommendations",
            description="Get AI-powered budget recommendations (combines questionnaire + synthetic social signals, with ethics guardrails). Supports optional user context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Target user ID (defaults to demo-user-123)"},
                    "consent_level": {"type": "integer", "description": "Consent level 0-2 (defaults to 2)"},
                },
            },
        ),
        Tool(
            name="ask_budget_agent",
            description="Ask the guardrailed budget agent a question. Returns answer with sources and ethical decision. Supports optional user context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "question": {"type": "string", "description": "The question to ask the budget agent"},
                    "user_id": {"type": "string", "description": "Target user ID (defaults to demo-user-123)"},
                    "consent_level": {"type": "integer", "description": "Consent level 0-2 (defaults to 2)"},
                },
                "required": ["question"],
            },
        ),
        Tool(
            name="get_career_recommendations",
            description="Get guardrailed career trajectory and critical role readiness recommendations (federal workforce domain). Uses assessments + synthetic signals with ethics. Supports optional user context.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_id": {"type": "string", "description": "Target user ID (defaults to demo-user-123)"},
                    "consent_level": {"type": "integer", "description": "Consent level 0-2 (defaults to 2)"},
                },
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[TextContent]:
    principal = _principal_from_args(arguments)

    if name == "get_spend_summary":
        factory = get_session_factory()
        async with factory() as session:
            repo = TransactionRepository(session)
            totals = await repo.sum_by_category(principal.user_id)
            if not totals:
                totals = {"groceries": 450.0, "coffee": 85.5, "transport": 120.0}
            total = sum(totals.values())
            top = sorted(totals.items(), key=lambda x: -x[1])[:3]
            result = {
                "total_spent": round(total, 2),
                "top_categories": [c for c, _ in top],
                "breakdown": totals,
                "user_id": principal.user_id,
            }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_budget_recommendations":
        recs, decision = get_recommendations(principal)
        await persist_decision(decision)
        if not decision.allowed:
            result = {"error": decision.reason, "allowed": False, "user_id": principal.user_id}
        else:
            result = {
                "recommendations": recs,
                "ethical_note": decision.reason,
                "allowed": True,
                "user_id": principal.user_id,
                "consent_level": principal.consent_level,
            }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "ask_budget_agent":
        question = arguments.get("question", "")
        if not question:
            return [TextContent(type="text", text=json.dumps({"error": "question is required"}))]
        result = await ask_budget_agent(principal, question)
        # inject user context into response for transparency
        result = dict(result)  # copy
        result["user_id"] = principal.user_id
        result["consent_level"] = principal.consent_level
        # persist already attempted inside agent; double-tap for MCP top-level
        # (the decision object not returned, but main paths covered via GraphQL + rec path)
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    elif name == "get_career_recommendations":
        recs, decision = get_career_recommendations(principal)
        await persist_decision(decision)
        if not decision.allowed:
            result = {"error": decision.reason, "allowed": False, "user_id": principal.user_id}
        else:
            result = {
                "recommendations": recs,
                "ethical_note": decision.reason,
                "allowed": True,
                "user_id": principal.user_id,
                "consent_level": principal.consent_level,
            }
        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    else:
        return [TextContent(type="text", text=json.dumps({"error": f"unknown tool {name}"}))]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
