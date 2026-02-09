"""Tests for storage models."""

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest

from expenses_ai_agent.storage.models import (
    Currency,
    Expense,
    ExpenseCategory,
    UserPreference,
    create_db_and_tables,
)


class TestExpenseCategoryModel:
    """Tests for ExpenseCategory model."""

    def test_str_returns_formatted_string(self) -> None:
        """Test __str__ returns properly formatted string."""
        category = ExpenseCategory(id=1, name="Food & Dining")

        result = str(category)

        assert result == "Category: Food & Dining"

    def test_str_with_different_name(self) -> None:
        """Test __str__ with different category name."""
        category = ExpenseCategory(id=2, name="Transportation")

        result = str(category)

        assert result == "Category: Transportation"

    def test_create_factory_method(self) -> None:
        """Test create() class method returns new instance."""
        category = ExpenseCategory.create(name="Entertainment")

        assert isinstance(category, ExpenseCategory)
        assert category.name == "Entertainment"
        assert category.id is None  # Not yet persisted

    def test_create_with_special_characters(self) -> None:
        """Test create() with special characters in name."""
        category = ExpenseCategory.create(name="Food & Dining")

        assert category.name == "Food & Dining"


class TestExpenseModel:
    """Tests for Expense model."""

    def test_str_with_category(self) -> None:
        """Test __str__ with category set."""
        category = ExpenseCategory(id=1, name="Food")
        expense = Expense(
            id=1,
            amount=Decimal("25.50"),
            currency=Currency.USD,
            description="Lunch at cafe",
            date=datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc),
            category=category,
        )

        result = str(expense)

        assert "25.50" in result
        assert "USD" in result
        assert "Lunch at cafe" in result
        assert "Food" in result

    def test_str_without_category(self) -> None:
        """Test __str__ without category."""
        expense = Expense(
            id=1,
            amount=Decimal("10.00"),
            currency=Currency.EUR,
            description="Coffee",
            date=datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc),
            category=None,
        )

        result = str(expense)

        assert "10.00" in result
        assert "EUR" in result
        assert "Coffee" in result
        assert "No category" in result

    def test_str_without_description(self) -> None:
        """Test __str__ without description."""
        expense = Expense(
            id=1,
            amount=Decimal("5.00"),
            currency=Currency.GBP,
            description=None,
            date=datetime(2024, 1, 15, tzinfo=timezone.utc),
        )

        result = str(expense)

        assert "No description" in result

    def test_create_factory_method(self) -> None:
        """Test create() class method."""
        expense = Expense.create(
            amount=Decimal("50.00"),
            currency=Currency.USD,
            description="Groceries",
        )

        assert isinstance(expense, Expense)
        assert expense.amount == Decimal("50.00")
        assert expense.currency == Currency.USD
        assert expense.description == "Groceries"
        assert expense.id is None

    def test_create_with_all_parameters(self) -> None:
        """Test create() with all parameters."""
        category = ExpenseCategory(id=1, name="Shopping")
        test_date = datetime(2024, 6, 15, 14, 30, tzinfo=timezone.utc)

        expense = Expense.create(
            amount=Decimal("100.00"),
            currency=Currency.EUR,
            description="New shoes",
            date=test_date,
            category=category,
            telegram_user_id=12345,
        )

        assert expense.amount == Decimal("100.00")
        assert expense.currency == Currency.EUR
        assert expense.description == "New shoes"
        assert expense.date == test_date
        assert expense.category == category
        assert expense.telegram_user_id == 12345

    def test_create_with_default_date(self) -> None:
        """Test create() uses current time when date not provided."""
        before = datetime.now(timezone.utc)

        expense = Expense.create(
            amount=Decimal("20.00"),
            currency=Currency.USD,
        )

        after = datetime.now(timezone.utc)

        assert before <= expense.date <= after

    def test_create_defaults_to_eur(self) -> None:
        """Test create() defaults to EUR currency."""
        expense = Expense.create(amount=Decimal("15.00"))

        assert expense.currency == Currency.EUR


class TestUserPreferenceModel:
    """Tests for UserPreference model."""

    def test_str_returns_formatted_string(self) -> None:
        """Test __str__ returns properly formatted string."""
        preference = UserPreference(
            id=1,
            telegram_user_id=12345,
            preferred_currency=Currency.USD,
        )

        result = str(preference)

        assert result == "UserPreference: 12345 - USD"

    def test_str_with_different_currency(self) -> None:
        """Test __str__ with different currency."""
        preference = UserPreference(
            id=2,
            telegram_user_id=67890,
            preferred_currency=Currency.GBP,
        )

        result = str(preference)

        assert "67890" in result
        assert "GBP" in result

    def test_default_currency_is_eur(self) -> None:
        """Test default currency is EUR."""
        preference = UserPreference(telegram_user_id=11111)

        assert preference.preferred_currency == Currency.EUR


class TestCurrencyEnum:
    """Tests for Currency enum."""

    def test_all_currencies_defined(self) -> None:
        """Test all expected currencies are defined."""
        expected = ["USD", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SEK", "NZD"]

        for currency in expected:
            assert hasattr(Currency, currency)
            assert Currency[currency].value == currency

    def test_currency_is_str_enum(self) -> None:
        """Test Currency values are strings."""
        assert Currency.USD == "USD"
        assert Currency.EUR == "EUR"
        assert isinstance(Currency.USD, str)


class TestCreateDbAndTables:
    """Tests for create_db_and_tables function."""

    @patch("expenses_ai_agent.storage.models.SQLModel")
    @patch("expenses_ai_agent.storage.models.create_engine")
    @patch("expenses_ai_agent.storage.models.config")
    def test_create_db_and_tables_uses_default_url(
        self,
        mock_config: MagicMock,
        mock_create_engine: MagicMock,
        mock_sqlmodel: MagicMock,
    ) -> None:
        """Test create_db_and_tables uses config for database URL."""
        mock_config.return_value = "sqlite:///./test.db"
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        create_db_and_tables()

        mock_config.assert_called_once_with(
            "DATABASE_URL", default="sqlite:///./expenses.db", cast=str
        )
        mock_create_engine.assert_called_once()
        mock_sqlmodel.metadata.create_all.assert_called_once_with(mock_engine)

    @patch("expenses_ai_agent.storage.models.SQLModel")
    @patch("expenses_ai_agent.storage.models.create_engine")
    @patch("expenses_ai_agent.storage.models.config")
    def test_create_db_and_tables_creates_engine_with_echo(
        self,
        mock_config: MagicMock,
        mock_create_engine: MagicMock,
        mock_sqlmodel: MagicMock,
    ) -> None:
        """Test create_db_and_tables creates engine with echo=True."""
        mock_config.return_value = "sqlite:///./expenses.db"

        create_db_and_tables()

        # Verify echo=True was passed
        call_kwargs = mock_create_engine.call_args
        assert call_kwargs[1]["echo"] is True
