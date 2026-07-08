"""Common FastAPI dependencies (DB session, rate limiter, etc.)."""

from __future__ import annotations

from fastapi import Depends
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import get_settings
from app.core.security import Principal, get_current_principal

settings = get_settings()

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=[f"{settings.rate_limit_per_minute}/minute"],
)


async def get_current_user(principal: Principal = Depends(get_current_principal)) -> Principal:
    """Alias / extension point for future user enrichment."""
    # In future could load user profile from DB here
    return principal


# Placeholder for async DB session dependency (implemented in db package)
# from app.db.session import get_session
# async def get_db_session():
#     ...
