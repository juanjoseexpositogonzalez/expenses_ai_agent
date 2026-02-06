"""Tests for FastAPI expense endpoints."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from expenses_ai_agent.api.deps import (
    get_category_repo,
    get_classification_service,
    get_expense_repo,
)
from expenses_ai_agent.api.main import app
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.services.classification import ClassificationResult
from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory


@pytest.fixture
def client():
    """Create test client with dependency overrides."""
    return TestClient(app)


@pytest.fixture
def mock_expense_repo():
    """Create mock expense repository."""
    return MagicMock()


@pytest.fixture
def mock_category_repo():
    """Create mock category repository."""
    return MagicMock()


@pytest.fixture
def mock_classification_service():
    """Create mock classification service."""
    return MagicMock()


# ------------------------------------------------------------------
# Health endpoint tests
# ------------------------------------------------------------------


class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_check(self, client: TestClient) -> None:
        """Test health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}


# ------------------------------------------------------------------
# Root endpoint tests
# ------------------------------------------------------------------


class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_returns_api_info(self, client: TestClient) -> None:
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Expenses AI Agent API"
        assert "version" in data


# ------------------------------------------------------------------
# Expenses endpoint tests
# ------------------------------------------------------------------


class TestListExpenses:
    """Tests for list expenses endpoint."""

    def test_list_expenses_empty(
        self, client: TestClient, mock_expense_repo: MagicMock
    ) -> None:
        """Test list expenses returns empty list when no expenses."""
        mock_expense_repo.list_by_user.return_value = []

        app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo

        try:
            response = client.get(
                "/api/v1/expenses/",
                headers={"X-User-ID": "12345"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["items"] == []
            assert data["total"] == 0
        finally:
            app.dependency_overrides.clear()

    def test_list_expenses_with_pagination(
        self, client: TestClient, mock_expense_repo: MagicMock
    ) -> None:
        """Test list expenses with pagination."""
        category = ExpenseCategory(id=1, name="Food")
        expenses = [
            Expense(
                id=i,
                amount=Decimal("10.00"),
                currency=Currency.USD,
                description=f"Expense {i}",
                category=category,
                date=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                telegram_user_id=12345,
            )
            for i in range(1, 6)
        ]

        mock_expense_repo.list_by_user.return_value = expenses
        app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo

        try:
            response = client.get(
                "/api/v1/expenses/",
                params={"page": 1, "page_size": 3},
                headers={"X-User-ID": "12345"},
            )
            assert response.status_code == 200
            data = response.json()
            assert len(data["items"]) == 3
            assert data["total"] == 5
            assert data["pages"] == 2
        finally:
            app.dependency_overrides.clear()


class TestClassifyExpense:
    """Tests for classify expense endpoint."""

    def test_classify_invalid_description_too_short(
        self, client: TestClient
    ) -> None:
        """Test classify rejects too short description."""
        response = client.post(
            "/api/v1/expenses/classify",
            json={"description": "ab"},
            headers={"X-User-ID": "12345"},
        )
        assert response.status_code == 422  # Pydantic validation

    def test_classify_success(
        self,
        client: TestClient,
        mock_classification_service: MagicMock,
        mock_expense_repo: MagicMock,
        mock_category_repo: MagicMock,
    ) -> None:
        """Test classify returns classified expense."""
        now = datetime.now(timezone.utc)
        llm_response = ExpenseCategorizationResponse(
            category="Food & Dining",
            total_amount=Decimal("5.50"),
            currency=Currency.USD,
            confidence=0.95,
            cost=Decimal("0.0001"),
            comments="test",
        )

        expense = Expense(
            id=1,
            amount=Decimal("5.50"),
            currency=Currency.USD,
            description="Coffee at Starbucks $5.50",
            date=now,
            telegram_user_id=12345,
        )

        mock_classification_service.classify.return_value = ClassificationResult(
            response=llm_response,
            expense=expense,
            is_persisted=True,
        )

        app.dependency_overrides[get_classification_service] = (
            lambda: mock_classification_service
        )
        app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo
        app.dependency_overrides[get_category_repo] = lambda: mock_category_repo

        try:
            response = client.post(
                "/api/v1/expenses/classify",
                json={"description": "Coffee at Starbucks $5.50"},
                headers={"X-User-ID": "12345"},
            )
            assert response.status_code == 201
            data = response.json()
            assert data["category"] == "Food & Dining"
            assert data["confidence"] == 0.95
        finally:
            app.dependency_overrides.clear()


class TestGetExpense:
    """Tests for get single expense endpoint."""

    def test_get_expense_not_found(
        self, client: TestClient, mock_expense_repo: MagicMock
    ) -> None:
        """Test get expense returns 404 for nonexistent expense."""
        from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError

        mock_expense_repo.get.side_effect = ExpenseNotFoundError("Expense 999 not found")
        app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo

        try:
            response = client.get(
                "/api/v1/expenses/999",
                headers={"X-User-ID": "12345"},
            )
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_get_expense_wrong_user(
        self, client: TestClient, mock_expense_repo: MagicMock
    ) -> None:
        """Test get expense returns 404 for different user's expense."""
        expense = Expense(
            id=1,
            amount=Decimal("10.00"),
            currency=Currency.USD,
            date=datetime.now(timezone.utc),
            telegram_user_id=99999,  # Different user
        )

        mock_expense_repo.get.return_value = expense
        app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo

        try:
            response = client.get(
                "/api/v1/expenses/1",
                headers={"X-User-ID": "12345"},
            )
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()


class TestDeleteExpense:
    """Tests for delete expense endpoint."""

    def test_delete_expense_not_found(
        self, client: TestClient, mock_expense_repo: MagicMock
    ) -> None:
        """Test delete expense returns 404 for nonexistent expense."""
        from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError

        mock_expense_repo.get.side_effect = ExpenseNotFoundError("Expense 999 not found")
        app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo

        try:
            response = client.delete(
                "/api/v1/expenses/999",
                headers={"X-User-ID": "12345"},
            )
            assert response.status_code == 404
        finally:
            app.dependency_overrides.clear()

    def test_delete_expense_success(
        self, client: TestClient, mock_expense_repo: MagicMock
    ) -> None:
        """Test delete expense succeeds."""
        expense = Expense(
            id=1,
            amount=Decimal("10.00"),
            currency=Currency.USD,
            date=datetime.now(timezone.utc),
            telegram_user_id=12345,
        )

        mock_expense_repo.get.return_value = expense
        app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo

        try:
            response = client.delete(
                "/api/v1/expenses/1",
                headers={"X-User-ID": "12345"},
            )
            assert response.status_code == 204
        finally:
            app.dependency_overrides.clear()


# ------------------------------------------------------------------
# Categories endpoint tests
# ------------------------------------------------------------------


class TestListCategories:
    """Tests for list categories endpoint."""

    def test_list_categories_empty(
        self, client: TestClient, mock_category_repo: MagicMock
    ) -> None:
        """Test list categories returns empty list."""
        mock_category_repo.list.return_value = []
        app.dependency_overrides[get_category_repo] = lambda: mock_category_repo

        try:
            response = client.get("/api/v1/categories/")
            assert response.status_code == 200
            assert response.json() == []
        finally:
            app.dependency_overrides.clear()

    def test_list_categories_with_data(
        self, client: TestClient, mock_category_repo: MagicMock
    ) -> None:
        """Test list categories returns categories."""
        categories = [
            ExpenseCategory(id=1, name="Food"),
            ExpenseCategory(id=2, name="Transport"),
        ]

        mock_category_repo.list.return_value = categories
        app.dependency_overrides[get_category_repo] = lambda: mock_category_repo

        try:
            response = client.get("/api/v1/categories/")
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 2
            assert data[0]["name"] == "Food"
        finally:
            app.dependency_overrides.clear()


# ------------------------------------------------------------------
# Analytics endpoint tests
# ------------------------------------------------------------------


class TestAnalyticsSummary:
    """Tests for analytics summary endpoint."""

    def test_analytics_summary_empty(
        self, client: TestClient, mock_expense_repo: MagicMock
    ) -> None:
        """Test analytics summary with no data."""
        mock_expense_repo.get_category_totals.return_value = []
        mock_expense_repo.get_monthly_totals.return_value = []
        mock_expense_repo.list_by_user.return_value = []
        app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo

        try:
            response = client.get(
                "/api/v1/analytics/summary",
                headers={"X-User-ID": "12345"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["total_expenses"] == "0"
            assert data["expense_count"] == 0
        finally:
            app.dependency_overrides.clear()

    def test_analytics_summary_with_data(
        self, client: TestClient, mock_expense_repo: MagicMock
    ) -> None:
        """Test analytics summary with data."""
        mock_expense_repo.get_category_totals.return_value = [
            ("Food", Decimal("100.00")),
            ("Transport", Decimal("50.00")),
        ]
        mock_expense_repo.get_monthly_totals.return_value = [
            ("2024-01", Decimal("150.00")),
        ]
        mock_expense_repo.list_by_user.return_value = [MagicMock(), MagicMock(), MagicMock()]
        app.dependency_overrides[get_expense_repo] = lambda: mock_expense_repo

        try:
            response = client.get(
                "/api/v1/analytics/summary",
                headers={"X-User-ID": "12345"},
            )
            assert response.status_code == 200
            data = response.json()
            assert data["expense_count"] == 3
            assert len(data["category_totals"]) == 2
        finally:
            app.dependency_overrides.clear()
