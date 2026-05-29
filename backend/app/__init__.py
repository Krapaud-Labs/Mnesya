"""Application initialization module.

This module handles the initialization of the FastAPI application,
including database setup, CORS configuration, and API documentation.
"""

from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from contextlib import asynccontextmanager
from typing import Generator
import secrets
import os

# ==================== Database setup ====================
database = declarative_base()
engine = None
SessionLocal = None


def init_app(database_url: str):
    """Initialize the application database.
    
    Creates the database engine, session maker, and creates all tables.
    
    Args:
        database_url (str): Database connection URL
    """
    global engine, SessionLocal
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    database.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """Dependency to get database session.
    
    Yields:
        Session: SQLAlchemy database session
        
    Note:
        Session is automatically closed after use
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan.
    
    Handles startup and shutdown events for the FastAPI application.
    Properly disposes of database engine on shutdown.
    
    Args:
        app (FastAPI): The FastAPI application instance
        
    Yields:
        None: Control to the application
    """
    yield
    if engine:
        engine.dispose()

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Adds security headers to every HTTP response."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = "default-src 'none'"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Server"] = "mnesya"
        return response


security = HTTPBasic()


def verify_docs_credentials(
        credentials: HTTPBasicCredentials = Depends(security)):
    """Protects Swagger and ReDoc with HTTP Basic Auth using environment variables.
    
    Args:
        credentials (HTTPBasicCredentials): HTTP Basic credentials from request
        
    Raises:
        HTTPException: If credentials are invalid (401 Unauthorized)
    """
    correct_username = secrets.compare_digest(
        credentials.username, os.environ["DOCS_USERNAME"]
    )
    correct_password = secrets.compare_digest(
        credentials.password, os.environ["DOCS_PASSWORD"]
    )
    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )


def create_app():
    """Create and configure the FastAPI application.

    Sets up the FastAPI application with:
    - CORS middleware for cross-origin requests
    - API documentation endpoints only in development (APP_ENV=development)
    - Application lifecycle management

    Returns:
        FastAPI: Configured FastAPI application instance
    """
    is_dev = os.environ.get("APP_ENV") == "development"
    app = FastAPI(
        title="Mnesya app",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url="/openapi.json" if is_dev else None,
    )

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:8081", "https://mnesya.com"],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Content-Type", "Authorization"],
    )

    if os.environ.get("APP_ENV") == "development":
        @app.get("/openapi.json", include_in_schema=False)
        async def protected_openapi(
                credentials: HTTPBasicCredentials = Depends(security)):
            verify_docs_credentials(credentials)
            return app.openapi()

        @app.get("/docs", include_in_schema=False)
        async def custom_swagger(
                credentials: HTTPBasicCredentials = Depends(security)):
            verify_docs_credentials(credentials)
            return get_swagger_ui_html(
                openapi_url="/openapi.json", title="Mnesya API Docs")

        @app.get("/redoc", include_in_schema=False)
        async def custom_redoc(
                credentials: HTTPBasicCredentials = Depends(security)):
            verify_docs_credentials(credentials)
            return get_redoc_html(openapi_url="/openapi.json",
                                  title="Mnesya API ReDoc")

    return app
