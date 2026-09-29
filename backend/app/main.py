"""Main application entry point.

This module initializes the FastAPI application, configures the database,
and registers all API routers. This is the entry point for the Mnesya backend.
"""

import os

from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app import create_app, init_app
from app.api import (
    authentication,
    caregiver,
    pairing,
    push_notification,
    reminder,
    reminder_status_api,
    user,
)
from app.limiter import limiter
from app.models import user_session_revocation  # noqa: F401 — ensures table is created

# Initialize database
database_url = os.environ["DATABASE_URL"]
init_app(database_url)

# Create FastAPI app
app = create_app()

# Include routers
app.include_router(authentication.router)
app.include_router(user.router)
app.include_router(caregiver.router)
app.include_router(pairing.router)
app.include_router(reminder.router)
app.include_router(reminder_status_api.router)
app.include_router(push_notification.router)

# Register rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def root():
    """Root endpoint.

    Returns:
        dict: Welcome message
    """
    return {"message": "Welcome to Mnesya API"}
