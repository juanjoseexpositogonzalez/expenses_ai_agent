"""Tests for Streamlit API client."""

from unittest.mock import MagicMock, patch

import httpx
import pytest

from expenses_ai_agent.streamlit.api_client import APIClient, get_client


class TestAPIClientInit:
    """Tests for APIClient initialization."""

    def test_init_with_defaults(self) -> None:
        """Test client initializes with default values from env."""
        with patch("expenses_ai_agent.streamlit.api_client.config") as mock_config:
            mock_config.side_effect = lambda key, **kwargs: kwargs.get("default")
            client = APIClient()

            assert client.base_url == "http://localhost:8000/api/v1"
            assert client.user_id == 12345

    def test_init_with_custom_values(self) -> None:
        """Test client initializes with custom values."""
        client = APIClient(base_url="http://test:9000/api", user_id=99999)

        assert client.base_url == "http://test:9000/api"
        assert client.user_id == 99999
        client.close()

    def test_context_manager(self) -> None:
        """Test client works as context manager."""
        with APIClient(base_url="http://test:9000") as client:
            assert isinstance(client, APIClient)


class TestAPIClientExpenses:
    """Tests for expense-related API methods."""

    @pytest.fixture
    def client(self) -> APIClient:
        """Create API client for testing."""
        return APIClient(base_url="http://test:8000/api/v1", user_id=12345)

    @pytest.fixture
    def mock_response(self) -> MagicMock:
        """Create mock response."""
        response = MagicMock()
        response.status_code = 200
        return response

    def test_list_expenses_success(self, client: APIClient) -> None:
        """Test listing expenses successfully."""
        expected_data = {
            "items": [{"id": 1, "description": "Coffee"}],
            "total": 1,
            "page": 1,
            "page_size": 20,
        }

        with patch.object(client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = expected_data
            mock_get.return_value = mock_response

            result = client.list_expenses(page=1, page_size=20)

            mock_get.assert_called_once_with(
                "/expenses/",
                params={"page": 1, "page_size": 20},
            )
            assert result == expected_data

        client.close()

    def test_list_expenses_with_pagination(self, client: APIClient) -> None:
        """Test listing expenses with custom pagination."""
        with patch.object(client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {"items": [], "total": 0}
            mock_get.return_value = mock_response

            client.list_expenses(page=3, page_size=50)

            mock_get.assert_called_once_with(
                "/expenses/",
                params={"page": 3, "page_size": 50},
            )

        client.close()

    def test_classify_expense_success(self, client: APIClient) -> None:
        """Test classifying expense successfully."""
        expected_data = {
            "id": 1,
            "description": "Coffee at Starbucks $5",
            "category": "Food & Dining",
        }

        with patch.object(client._client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.json.return_value = expected_data
            mock_post.return_value = mock_response

            result = client.classify_expense("Coffee at Starbucks $5")

            mock_post.assert_called_once_with(
                "/expenses/classify",
                json={"description": "Coffee at Starbucks $5"},
            )
            assert result == expected_data

        client.close()

    def test_classify_expense_http_error(self, client: APIClient) -> None:
        """Test classify expense raises on HTTP error."""
        with patch.object(client._client, "post") as mock_post:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
                "Error", request=MagicMock(), response=MagicMock()
            )
            mock_post.return_value = mock_response

            with pytest.raises(httpx.HTTPStatusError):
                client.classify_expense("invalid")

        client.close()

    def test_delete_expense_success(self, client: APIClient) -> None:
        """Test deleting expense successfully."""
        with patch.object(client._client, "delete") as mock_delete:
            mock_response = MagicMock()
            mock_delete.return_value = mock_response

            client.delete_expense(123)

            mock_delete.assert_called_once_with("/expenses/123")

        client.close()

    def test_get_users_success(self, client: APIClient) -> None:
        """Test getting users list."""
        expected_users = [12345, 67890]

        with patch.object(client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = expected_users
            mock_get.return_value = mock_response

            result = client.get_users()

            mock_get.assert_called_once_with("/expenses/users/")
            assert result == expected_users

        client.close()

    def test_set_user_id(self, client: APIClient) -> None:
        """Test setting user ID updates headers."""
        client.set_user_id(99999)

        assert client.user_id == 99999
        assert client._client.headers["X-User-ID"] == "99999"

        client.close()


class TestAPIClientAnalytics:
    """Tests for analytics-related API methods."""

    @pytest.fixture
    def client(self) -> APIClient:
        """Create API client for testing."""
        return APIClient(base_url="http://test:8000/api/v1", user_id=12345)

    def test_get_analytics_summary_success(self, client: APIClient) -> None:
        """Test getting analytics summary."""
        expected_data = {
            "category_totals": [{"category": "Food", "total": 100.0}],
            "monthly_totals": [{"month": "2024-01", "total": 50.0}],
        }

        with patch.object(client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = expected_data
            mock_get.return_value = mock_response

            result = client.get_analytics_summary(months=6)

            mock_get.assert_called_once_with(
                "/analytics/summary",
                params={"months": 6},
            )
            assert result == expected_data

        client.close()

    def test_get_analytics_summary_default_months(self, client: APIClient) -> None:
        """Test analytics summary uses default 12 months."""
        with patch.object(client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = {}
            mock_get.return_value = mock_response

            client.get_analytics_summary()

            mock_get.assert_called_once_with(
                "/analytics/summary",
                params={"months": 12},
            )

        client.close()


class TestAPIClientCategories:
    """Tests for category-related API methods."""

    @pytest.fixture
    def client(self) -> APIClient:
        """Create API client for testing."""
        return APIClient(base_url="http://test:8000/api/v1", user_id=12345)

    def test_list_categories_success(self, client: APIClient) -> None:
        """Test listing categories."""
        expected_categories = [
            {"id": 1, "name": "Food & Dining"},
            {"id": 2, "name": "Transportation"},
        ]

        with patch.object(client._client, "get") as mock_get:
            mock_response = MagicMock()
            mock_response.json.return_value = expected_categories
            mock_get.return_value = mock_response

            result = client.list_categories()

            mock_get.assert_called_once_with("/categories/")
            assert result == expected_categories

        client.close()


class TestAPIClientHealth:
    """Tests for health check method."""

    @pytest.fixture
    def client(self) -> APIClient:
        """Create API client for testing."""
        return APIClient(base_url="http://test:8000/api/v1", user_id=12345)

    def test_health_check_success(self, client: APIClient) -> None:
        """Test health check returns True when API is healthy."""
        with patch("expenses_ai_agent.streamlit.api_client.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_get.return_value = mock_response

            result = client.health_check()

            mock_get.assert_called_once_with("http://test:8000/health", timeout=5.0)
            assert result is True

        client.close()

    def test_health_check_failure_status(self, client: APIClient) -> None:
        """Test health check returns False on non-200 status."""
        with patch("expenses_ai_agent.streamlit.api_client.httpx.get") as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_get.return_value = mock_response

            result = client.health_check()

            assert result is False

        client.close()

    def test_health_check_connection_error(self, client: APIClient) -> None:
        """Test health check returns False on connection error."""
        with patch("expenses_ai_agent.streamlit.api_client.httpx.get") as mock_get:
            mock_get.side_effect = httpx.ConnectError("Connection refused")

            result = client.health_check()

            assert result is False

        client.close()

    def test_health_check_timeout(self, client: APIClient) -> None:
        """Test health check returns False on timeout."""
        with patch("expenses_ai_agent.streamlit.api_client.httpx.get") as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Timeout")

            result = client.health_check()

            assert result is False

        client.close()


class TestGetClientSingleton:
    """Tests for get_client singleton function."""

    def test_get_client_returns_client(self) -> None:
        """Test get_client returns APIClient instance."""
        # Reset singleton
        import expenses_ai_agent.streamlit.api_client as module

        module._client = None

        with patch.object(APIClient, "__init__", return_value=None):
            client = get_client()
            # Should be same instance on second call
            client2 = get_client()
            assert client is client2

        # Reset for other tests
        module._client = None

    def test_get_client_creates_new_when_none(self) -> None:
        """Test get_client creates new client when singleton is None."""
        import expenses_ai_agent.streamlit.api_client as module

        module._client = None

        with patch("expenses_ai_agent.streamlit.api_client.APIClient") as mock_cls:
            mock_instance = MagicMock()
            mock_cls.return_value = mock_instance

            result = get_client()

            mock_cls.assert_called_once()
            assert result is mock_instance

        # Reset for other tests
        module._client = None
