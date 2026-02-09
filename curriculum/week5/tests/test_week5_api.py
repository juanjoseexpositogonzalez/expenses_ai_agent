"""
Week 5 - Definition of Done: FastAPI REST API

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week5_api.py -v
All tests must pass to complete Week 5's API milestone.

These tests verify your implementation of:
- FastAPI application structure
- Expense routes (CRUD + classify)
- Analytics routes
- Dependency injection
"""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def mock_expense_repo():
    """Create a mock expense repository."""
    from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory

    repo = MagicMock()
    category = ExpenseCategory(id=1, name="Food")
    expenses = [
        Expense(id=1, amount=Decimal("10.00"), currency=Currency.EUR, category=category, telegram_user_id=12345),
        Expense(id=2, amount=Decimal("20.00"), currency=Currency.USD, category=category, telegram_user_id=12345),
    ]
    repo.list_by_user.return_value = expenses
    repo.get.return_value = expenses[0]
    repo.list.return_value = expenses
    return repo


@pytest.fixture
def mock_category_repo():
    """Create a mock category repository."""
    from expenses_ai_agent.storage.models import ExpenseCategory

    repo = MagicMock()
    repo.list.return_value = ["Food", "Transport", "Entertainment"]
    repo.get.return_value = ExpenseCategory(id=1, name="Food")
    return repo


@pytest.fixture
def test_client(mock_expense_repo, mock_category_repo):
    """Create a test client with mocked dependencies."""
    from expenses_ai_agent.api.deps import get_category_repo, get_expense_repo
    from expenses_ai_agent.api.main import app

    app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo
    app.dependency_overrides[get_category_repo] = lambda: mock_category_repo

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()


class TestFastAPIApp:
    """Tests for the FastAPI application structure."""

    def test_app_exists(self):
        """FastAPI app should be importable."""
        from expenses_ai_agent.api.main import app

        assert app is not None

    def test_app_has_cors(self, test_client):
        """App should have CORS middleware configured."""
        # OPTIONS request should work
        response = test_client.options("/api/v1/health")
        # CORS headers should be present or request should succeed
        assert response.status_code in [200, 405]

    def test_health_endpoint(self, test_client):
        """Health endpoint should return OK status."""
        response = test_client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] in ["ok", "healthy", "OK"]


class TestExpenseRoutes:
    """Tests for expense CRUD routes."""

    def test_list_expenses(self, test_client, mock_expense_repo):
        """GET /expenses/ should return paginated expenses."""
        response = test_client.get("/api/v1/expenses/")

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_list_expenses_with_user_header(self, test_client, mock_expense_repo):
        """List should filter by X-User-ID header."""
        response = test_client.get(
            "/api/v1/expenses/",
            headers={"X-User-ID": "12345"}
        )

        assert response.status_code == 200
        mock_expense_repo.list_by_user.assert_called()

    def test_get_expense_by_id(self, test_client, mock_expense_repo):
        """GET /expenses/{id} should return single expense."""
        response = test_client.get("/api/v1/expenses/1")

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "amount" in data

    def test_get_nonexistent_expense_returns_404(self, test_client, mock_expense_repo):
        """GET /expenses/{id} should return 404 if not found."""
        from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError

        mock_expense_repo.get.side_effect = ExpenseNotFoundError(999)

        response = test_client.get("/api/v1/expenses/999")

        assert response.status_code == 404

    def test_delete_expense(self, test_client, mock_expense_repo):
        """DELETE /expenses/{id} should remove expense."""
        response = test_client.delete("/api/v1/expenses/1")

        assert response.status_code == 204
        mock_expense_repo.delete.assert_called_with(1)

    def test_classify_expense(self, test_client, mock_expense_repo, mock_category_repo):
        """POST /expenses/classify should classify and store expense."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        with patch("expenses_ai_agent.api.routes.expenses.ClassificationService") as mock_cls:
            mock_service = MagicMock()
            mock_result = MagicMock()
            mock_result.response = ExpenseCategorizationResponse(
                category="Food",
                total_amount=Decimal("5.50"),
                currency=Currency.USD,
                confidence=0.95,
                cost=Decimal("0.001"),
            )
            mock_result.persisted = True
            mock_service.classify.return_value = mock_result
            mock_cls.return_value = mock_service

            response = test_client.post(
                "/api/v1/expenses/classify",
                json={"description": "Coffee $5.50"},
                headers={"X-User-ID": "12345"},
            )

            assert response.status_code == 201
            data = response.json()
            assert "category" in data


class TestCategoryRoutes:
    """Tests for category routes."""

    def test_list_categories(self, test_client, mock_category_repo):
        """GET /categories/ should return all category names."""
        response = test_client.get("/api/v1/categories/")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert "Food" in data


class TestAnalyticsRoutes:
    """Tests for analytics routes."""

    def test_get_summary(self, test_client, mock_expense_repo):
        """GET /analytics/summary should return aggregated data."""
        mock_expense_repo.get_category_totals.return_value = {
            "Food": Decimal("100.00"),
            "Transport": Decimal("50.00"),
        }
        mock_expense_repo.get_monthly_totals.return_value = {
            "2024-01": Decimal("150.00"),
        }

        response = test_client.get(
            "/api/v1/analytics/summary",
            headers={"X-User-ID": "12345"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "category_totals" in data or "categories" in str(data).lower()


class TestAPISchemas:
    """Tests for Pydantic request/response schemas."""

    def test_expense_classify_request_exists(self):
        """ExpenseClassifyRequest schema should exist."""
        from expenses_ai_agent.api.schemas.expense import ExpenseClassifyRequest

        request = ExpenseClassifyRequest(description="Test")
        assert request.description == "Test"

    def test_expense_response_exists(self):
        """ExpenseResponse schema should exist."""
        from expenses_ai_agent.api.schemas.expense import ExpenseResponse

        assert ExpenseResponse is not None

    def test_expense_list_response_has_pagination(self):
        """ExpenseListResponse should include pagination fields."""
        from expenses_ai_agent.api.schemas.expense import ExpenseListResponse

        # Check the model has expected fields
        fields = ExpenseListResponse.model_fields
        assert "items" in fields
        assert "total" in fields


class TestDependencyInjection:
    """Tests for dependency injection functions."""

    def test_get_expense_repo_exists(self):
        """get_expense_repo dependency should be importable."""
        from expenses_ai_agent.api.deps import get_expense_repo

        assert callable(get_expense_repo)

    def test_get_user_id_exists(self):
        """get_user_id dependency should be importable."""
        from expenses_ai_agent.api.deps import get_user_id

        assert callable(get_user_id)
