"""
Week 5 - Definition of Done: Streamlit Dashboard

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week5_streamlit.py -v
All tests must pass to complete Week 5's Streamlit milestone.

These tests verify your implementation of:
- Streamlit API client
- Dashboard views structure
"""

from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest


class TestStreamlitAPIClient:
    """Tests for the Streamlit API client."""

    def test_api_client_exists(self):
        """ExpenseAPIClient should be importable."""
        from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

        assert ExpenseAPIClient is not None

    def test_api_client_has_base_url(self):
        """Client should accept base URL configuration."""
        from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

        client = ExpenseAPIClient(base_url="http://localhost:8000/api/v1")
        assert "8000" in client.base_url or hasattr(client, "base_url")

    def test_api_client_get_expenses(self):
        """Client should have method to get expenses."""
        from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

        client = ExpenseAPIClient(base_url="http://test")
        assert hasattr(client, "get_expenses") or hasattr(client, "list_expenses")

    def test_api_client_classify_expense(self):
        """Client should have method to classify expense."""
        from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

        client = ExpenseAPIClient(base_url="http://test")
        assert hasattr(client, "classify_expense") or hasattr(client, "classify")

    def test_api_client_get_summary(self):
        """Client should have method to get analytics summary."""
        from expenses_ai_agent.streamlit.api_client import ExpenseAPIClient

        client = ExpenseAPIClient(base_url="http://test")
        assert hasattr(client, "get_summary") or hasattr(client, "get_analytics")


class TestStreamlitViews:
    """Tests for Streamlit view modules."""

    def test_dashboard_view_exists(self):
        """Dashboard view module should exist."""
        from expenses_ai_agent.streamlit.views import dashboard

        assert dashboard is not None

    def test_expenses_view_exists(self):
        """Expenses list view module should exist."""
        from expenses_ai_agent.streamlit.views import expenses

        assert expenses is not None

    def test_add_expense_view_exists(self):
        """Add expense view module should exist."""
        from expenses_ai_agent.streamlit.views import add_expense

        assert add_expense is not None


class TestStreamlitApp:
    """Tests for the main Streamlit app."""

    def test_app_module_exists(self):
        """Main app module should be importable."""
        from expenses_ai_agent.streamlit import app

        assert app is not None
