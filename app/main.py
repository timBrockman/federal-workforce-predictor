"""FastAPI application entrypoint - production template structure.

- Limited Strawberry GraphQL
- Auth via JWT + Principal (ethics aware)
- Rate limiting, CORS, health
- Ready for MCP mount and full DB wiring
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any, cast

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from strawberry.fastapi import GraphQLRouter

from app.api.graphql.schema import schema as graphql_schema
from app.core.config import get_settings
from app.core.deps import limiter
from app.core.security import (
    Principal,
    create_demo_token,
    get_current_principal,
    get_token_via_client_credentials,
)
from app.db.engine import get_session_factory, init_db
from app.db.repositories import TransactionRepository, UserRepository

settings = get_settings()


def get_context(
    principal: Principal | None = Depends(get_current_principal),  # noqa: B008
) -> dict[str, Principal | None]:
    return {"principal": principal}


graphql_router = GraphQLRouter(
    graphql_schema,
    path="/graphql",
    context_getter=get_context,
)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    print(f"🚀 Starting {settings.app_name} (Ollama default: {settings.llm_model})")
    await init_db()
    print("   - DB initialized (tables created if needed)")

    # Seed demo data for the template user (idempotent-ish)
    factory = get_session_factory()
    async with factory() as session:
        user_repo = UserRepository(session)
        await user_repo.get_or_create("demo-user-123")

        tx_repo = TransactionRepository(session)
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
            print("   - Seeded demo transactions for demo-user-123")

    print("   - GET /demo-token for a dev JWT (debug mode)")
    print("   - POST /graphql with Authorization: Bearer <token>")
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Production-grade AI service template. "
        "FastAPI + Strawberry GraphQL (intentionally limited) + MCP + Pydantic AI (guardrailed) "
        "with first-class ethics, Auth0/Keycloak JWT, SQLite+pooling."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(
    RateLimitExceeded,
    cast(Any, _rate_limit_exceeded_handler),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/health", tags=["ops"])
async def health() -> dict[str, str]:
    return {"status": "healthy", "service": settings.app_name}


@app.get("/ready", tags=["ops"])
async def ready() -> dict[str, str]:
    return {"status": "ready"}


@app.get("/demo-token", tags=["demo"], include_in_schema=settings.debug)
async def demo_token(
    user_id: str = "demo-user-123",
    consent: int = 2,
    client_id: str | None = None,
    client_secret: str | None = None,
) -> dict[str, str]:
    """Dev convenience. In production obtain real tokens via Auth0/Keycloak client credentials flow.

    If client_id and client_secret provided, performs real exchange.
    """
    if client_id and client_secret:
        token = await get_token_via_client_credentials(client_id, client_secret)
        return {"access_token": token, "token_type": "bearer"}
    token = create_demo_token(user_id=user_id, consent_level=consent)
    return {"access_token": token, "token_type": "bearer"}


app.include_router(graphql_router)

# Minimal human interface explorer
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/explorer", include_in_schema=False)
async def explorer() -> Any:
    from fastapi.responses import FileResponse

    return FileResponse("app/static/explorer.html")


# MCP server is implemented in app/services/mcp_server.py
# Run it standalone with:
#   uv run python -m app.services.mcp_server
# It exposes the same curated tools:
# get_spend_summary, get_budget_recommendations, ask_budget_agent
# using the official MCP SDK (stdio transport).


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.debug)
