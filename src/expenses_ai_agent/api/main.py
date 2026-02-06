"""FastAPI application for expense tracking."""

from contextlib import asynccontextmanager
from typing import Any

from decouple import config
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel

from expenses_ai_agent.api.deps import engine
from expenses_ai_agent.api.routes import analytics, categories, expenses, health
# Import models to ensure they're registered with SQLModel before create_all
from expenses_ai_agent.storage.models import Expense, ExpenseCategory, UserPreference  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    """Handle application startup and shutdown."""
    # Create database tables on startup
    SQLModel.metadata.create_all(engine)
    yield
    # Cleanup on shutdown (if needed)


app = FastAPI(
    title="Expenses AI Agent API",
    description="AI-powered expense classification and tracking API",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS
cors_origins = config("CORS_ORIGINS", default="http://localhost:8501", cast=str)
origins = [origin.strip() for origin in cors_origins.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(expenses.router, prefix="/api/v1")
app.include_router(categories.router, prefix="/api/v1")
app.include_router(analytics.router, prefix="/api/v1")


@app.get("/")
def root() -> dict[str, str]:
    """Root endpoint with API info."""
    return {
        "name": "Expenses AI Agent API",
        "version": "1.0.0",
        "docs": "/docs",
    }
