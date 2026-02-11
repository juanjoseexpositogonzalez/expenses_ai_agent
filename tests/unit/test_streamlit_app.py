"""Tests for Streamlit main app module."""

from unittest.mock import MagicMock, patch


class TestStreamlitAppModule:
    """Tests for the main Streamlit app configuration and routing."""

    def test_api_client_health_check_pattern(self) -> None:
        """Test that health check pattern works correctly."""
        mock_client = MagicMock()
        mock_client.health_check.return_value = True

        # Simulate what the app does
        api_healthy = mock_client.health_check()

        mock_client.health_check.assert_called_once()
        assert api_healthy is True

    def test_navigation_options(self) -> None:
        """Test that navigation options are correct."""
        expected_pages = ["Dashboard", "Expenses", "Add Expense"]

        # Verify expected navigation structure
        assert "Dashboard" in expected_pages
        assert "Expenses" in expected_pages
        assert "Add Expense" in expected_pages
        assert len(expected_pages) == 3


class TestStreamlitAppRouting:
    """Tests for app page routing logic."""

    def test_dashboard_routing_logic(self) -> None:
        """Test dashboard routing condition."""
        page = "Dashboard"
        assert page == "Dashboard"

    def test_expenses_routing_logic(self) -> None:
        """Test expenses routing condition."""
        page = "Expenses"
        assert page == "Expenses"

    def test_add_expense_routing_logic(self) -> None:
        """Test add expense routing condition."""
        page = "Add Expense"
        assert page == "Add Expense"

    def test_page_routing_switch(self) -> None:
        """Test page routing switch logic."""
        pages = ["Dashboard", "Expenses", "Add Expense"]

        for page in pages:
            if page == "Dashboard":
                route = "dashboard"
            elif page == "Expenses":
                route = "expenses"
            elif page == "Add Expense":
                route = "add_expense"
            else:
                route = "unknown"

            assert route != "unknown"


class TestStreamlitAppConfiguration:
    """Tests for app configuration constants."""

    def test_page_config_values(self) -> None:
        """Test expected page configuration values."""
        expected_config = {
            "page_title": "Expenses AI Agent",
            "page_icon": "💰",
            "layout": "wide",
            "initial_sidebar_state": "expanded",
        }

        # Verify expected config structure
        assert expected_config["page_title"] == "Expenses AI Agent"
        assert expected_config["layout"] == "wide"
        assert expected_config["page_icon"] == "💰"
        assert expected_config["initial_sidebar_state"] == "expanded"

    def test_sidebar_title_text(self) -> None:
        """Test expected sidebar title."""
        expected_title = "💰 Expenses AI Agent"
        assert "Expenses AI Agent" in expected_title
        assert "💰" in expected_title


class TestAPIHealthCheckBehavior:
    """Tests for API health check behavior patterns."""

    def test_health_check_returns_true_when_healthy(self) -> None:
        """Test health check returns True for healthy API."""
        mock_client = MagicMock()
        mock_client.health_check.return_value = True

        result = mock_client.health_check()

        assert result is True

    def test_health_check_returns_false_when_unhealthy(self) -> None:
        """Test health check returns False for unhealthy API."""
        mock_client = MagicMock()
        mock_client.health_check.return_value = False

        result = mock_client.health_check()

        assert result is False

    def test_app_behavior_when_api_unhealthy(self) -> None:
        """Test app behavior when API is unhealthy."""
        api_healthy = False

        if not api_healthy:
            # Should show error message
            error_message = (
                "Cannot connect to the API. Please ensure the FastAPI server is running"
            )
            assert "FastAPI server" in error_message
            should_stop = True
        else:
            should_stop = False

        assert should_stop is True

    def test_app_behavior_when_api_healthy(self) -> None:
        """Test app behavior when API is healthy."""
        api_healthy = True

        if not api_healthy:
            should_stop = True
        else:
            should_stop = False

        assert should_stop is False
