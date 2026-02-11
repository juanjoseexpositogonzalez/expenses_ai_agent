# syntax=docker/dockerfile:1

# Expenses AI Agent - Multi-service Dockerfile
# Supports: FastAPI (api), Telegram Bot (bot), Streamlit (streamlit)

FROM python:3.12-slim AS base

# Prevent Python from writing .pyc files and buffering stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast package management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Copy dependency files and source code
COPY pyproject.toml uv.lock ./
COPY src/ ./src/

# Install dependencies using uv sync (creates .venv automatically)
RUN uv sync --frozen --no-dev
ENV PATH="/app/.venv/bin:$PATH"

# Create data directory for SQLite
RUN mkdir -p /app/data

# Default environment variables
ENV DATABASE_URL="sqlite:///./data/expenses.db"

# Expose ports
EXPOSE 8000 8501

# Default command (FastAPI)
CMD ["uvicorn", "expenses_ai_agent.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
