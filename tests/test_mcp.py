"""Tests for MCP server with real Principal support (Phase 2).

Exercises different user contexts (user_id + consent_level) passed via tool arguments.
Both direct (in-process) calls and stdio client are covered.
"""

import json

import pytest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from app.services.mcp_server import call_tool as mcp_call_tool
from app.services.mcp_server import list_tools as mcp_list_tools


@pytest.mark.asyncio
async def test_mcp_list_tools():
    tools = await mcp_list_tools()
    names = [t.name for t in tools]
    assert "get_spend_summary" in names
    assert "get_budget_recommendations" in names
    assert "ask_budget_agent" in names
    assert "get_career_recommendations" in names


@pytest.mark.asyncio
async def test_mcp_get_spend_summary_default_and_explicit():
    # Default
    res = await mcp_call_tool("get_spend_summary", {})
    data = json.loads(res[0].text)
    assert "total_spent" in data
    assert data.get("user_id") == "demo-user-123"

    # Explicit different user
    res2 = await mcp_call_tool("get_spend_summary", {"user_id": "mcp-test-user"})
    data2 = json.loads(res2[0].text)
    assert data2.get("user_id") == "mcp-test-user"


@pytest.mark.asyncio
async def test_mcp_recommendations_respects_consent():
    """High consent should allow synthetic sources and succeed; low consent should degrade."""
    # High consent (default 2)
    res_high = await mcp_call_tool("get_budget_recommendations", {"consent_level": 2})
    data_high = json.loads(res_high[0].text)
    assert data_high.get("allowed") is True
    assert "recommendations" in data_high
    assert data_high.get("user_id") == "demo-user-123"
    # sources should include synthetic when consent high
    recs = data_high.get("recommendations", [])
    if recs:
        assert any("synthetic" in str(s).lower() for r in recs for s in r.get("data_sources", []))

    # Low consent user
    res_low = await mcp_call_tool(
        "get_budget_recommendations", {"user_id": "low-consent-mcp", "consent_level": 0}
    )
    data_low = json.loads(res_low[0].text)
    assert data_low.get("user_id") == "low-consent-mcp"
    # Policy should refuse or return empty
    assert data_low.get("allowed") is False or len(data_low.get("recommendations", [])) == 0


@pytest.mark.asyncio
async def test_mcp_ask_agent_with_context():
    res = await mcp_call_tool(
        "ask_budget_agent", {"question": "What is a sensible groceries budget?", "consent_level": 1}
    )
    data = json.loads(res[0].text)
    assert "answer" in data
    assert data.get("consent_level") == 1
    assert "user_id" in data


@pytest.mark.asyncio
async def test_mcp_submit_assessment():
    """Submit assessment via MCP and verify success + consent recorded."""
    res = await mcp_call_tool(
        "submit_assessment",
        {
            "skills_inventory": "python,cloud",
            "performance_level": "high",
            "career_goals": "cyber leadership",
            "consent_for_career_modeling": True,
            "consent_level": 2,
        },
    )
    data = json.loads(res[0].text)
    assert data.get("success") is True
    assert "Assessment recorded" in data.get("message", "")


@pytest.mark.slow
@pytest.mark.asyncio
async def test_mcp_stdio_with_explicit_principal():
    """Full end-to-end via stdio client, passing real principal context."""
    server_params = StdioServerParameters(
        command="uv", args=["run", "python", "-m", "app.services.mcp_server"]
    )
    async with stdio_client(server_params) as (read, write), ClientSession(read, write) as session:
        await session.initialize()
        # Call with explicit low-consent principal (verifies no crash + context passed)
        result = await session.call_tool(
            "get_budget_recommendations",
            {"user_id": "stdio-low", "consent_level": 0},
        )
        # MCP result is typically CallToolResult; content may be TextContent list
        text = None
        if hasattr(result, "content") and result.content:
            first = result.content[0]
            text = getattr(first, "text", str(first))
        data = json.loads(text) if text else {}
        assert data.get("user_id") == "stdio-low"
        assert data.get("allowed") is False or len(data.get("recommendations", [])) == 0


@pytest.mark.asyncio
async def test_mcp_career_recommendations_respects_consent():
    """High consent should return career recs; low consent should degrade (new federal path)."""
    # High consent
    res_high = await mcp_call_tool("get_career_recommendations", {"consent_level": 2})
    data_high = json.loads(res_high[0].text)
    assert data_high.get("user_id") == "demo-user-123"
    assert data_high.get("allowed") is True
    assert "recommendations" in data_high

    # Low consent
    res_low = await mcp_call_tool(
        "get_career_recommendations", {"user_id": "low-consent-mcp", "consent_level": 0}
    )
    data_low = json.loads(res_low[0].text)
    assert data_low.get("user_id") == "low-consent-mcp"
    assert data_low.get("allowed") is False or len(data_low.get("recommendations", [])) == 0
