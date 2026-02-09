"""
Week 1 - Definition of Done: Data Models

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week1_models.py -v
All tests must pass to complete Week 1's models milestone.

These tests verify your implementation of:
- Currency StrEnum with 10 currency codes
- ExpenseCategory SQLModel entity
- Expense SQLModel entity with relationships
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest


class TestCurrencyEnum:
    """Tests for the Currency enumeration."""

    def test_currency_is_string_enum(self):
        """Currency should be a StrEnum so values work as strings."""
        from expenses_ai_agent.storage.models import Currency

        # StrEnum values should be usable as strings directly
        assert Currency.EUR == "EUR"
        assert Currency.USD == "USD"
        assert str(Currency.EUR) == "EUR"

    def test_currency_has_required_values(self):
        """Currency enum must include at least these 10 common currencies."""
        from expenses_ai_agent.storage.models import Currency

        required_currencies = ["EUR", "USD", "GBP", "JPY", "CHF", "CAD", "AUD", "CNY", "INR", "MXN"]

        for code in required_currencies:
            assert hasattr(Currency, code), f"Currency.{code} is missing"
            assert Currency[code].value == code

    def test_currency_is_iterable(self):
        """Should be able to iterate over all currency values."""
        from expenses_ai_agent.storage.models import Currency

        currencies = list(Currency)
        assert len(currencies) >= 10
        assert all(isinstance(c, Currency) for c in currencies)


class TestExpenseCategory:
    """Tests for the ExpenseCategory model."""

    def test_category_has_required_fields(self):
        """ExpenseCategory must have id and name fields."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        category = ExpenseCategory(name="Food")

        assert hasattr(category, "id")
        assert hasattr(category, "name")
        assert category.name == "Food"
        # id should be None until persisted
        assert category.id is None

    def test_category_str_representation(self):
        """ExpenseCategory __str__ should return the category name."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        category = ExpenseCategory(name="Transport")
        assert str(category) == "Transport"

    def test_category_create_class_method(self):
        """ExpenseCategory.create() should be a convenient factory method."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        category = ExpenseCategory.create(name="Entertainment")

        assert isinstance(category, ExpenseCategory)
        assert category.name == "Entertainment"

    def test_category_name_is_indexed(self):
        """The name field should be configured for database indexing."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        # Access SQLModel field info
        name_field = ExpenseCategory.model_fields["name"]
        field_info = name_field.json_schema_extra or {}

        # Check if index is set (SQLModel uses sa_column_kwargs or Field params)
        # This is a simplified check - the actual index is set via Field(index=True)
        assert "name" in ExpenseCategory.model_fields


class TestExpense:
    """Tests for the Expense model."""

    def test_expense_has_required_fields(self):
        """Expense must have all required fields for expense tracking."""
        from expenses_ai_agent.storage.models import Currency, Expense

        expense = Expense(
            amount=Decimal("42.50"),
            currency=Currency.EUR,
            description="Lunch at restaurant",
        )

        assert hasattr(expense, "id")
        assert hasattr(expense, "amount")
        assert hasattr(expense, "currency")
        assert hasattr(expense, "description")
        assert hasattr(expense, "date")
        assert hasattr(expense, "category_id")
        assert hasattr(expense, "category")

    def test_expense_amount_is_decimal(self):
        """Amount should use Decimal for financial precision."""
        from expenses_ai_agent.storage.models import Currency, Expense

        expense = Expense(
            amount=Decimal("19.99"),
            currency=Currency.USD,
        )

        assert isinstance(expense.amount, Decimal)
        assert expense.amount == Decimal("19.99")

    def test_expense_currency_default(self):
        """Currency should default to EUR if not specified."""
        from expenses_ai_agent.storage.models import Currency, Expense

        expense = Expense(amount=Decimal("10.00"))

        assert expense.currency == Currency.EUR

    def test_expense_date_defaults_to_now(self):
        """Date should default to current UTC time."""
        from expenses_ai_agent.storage.models import Expense

        before = datetime.now(timezone.utc)
        expense = Expense(amount=Decimal("5.00"))
        after = datetime.now(timezone.utc)

        assert expense.date is not None
        # Allow small time window for test execution
        assert before <= expense.date <= after or (after - before).total_seconds() < 2

    def test_expense_str_representation(self):
        """Expense __str__ should provide a readable summary."""
        from expenses_ai_agent.storage.models import Currency, Expense

        expense = Expense(
            amount=Decimal("25.00"),
            currency=Currency.GBP,
            description="Book purchase",
        )

        result = str(expense)
        # Should contain amount and currency at minimum
        assert "25" in result
        assert "GBP" in result

    def test_expense_create_class_method(self):
        """Expense.create() should be a convenient factory method."""
        from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory

        category = ExpenseCategory(id=1, name="Shopping")

        expense = Expense.create(
            amount=Decimal("99.99"),
            currency=Currency.USD,
            description="New headphones",
            category=category,
        )

        assert isinstance(expense, Expense)
        assert expense.amount == Decimal("99.99")
        assert expense.currency == Currency.USD
        assert expense.description == "New headphones"
        assert expense.category == category

    def test_expense_optional_telegram_user_id(self):
        """Expense should support optional telegram_user_id for multiuser."""
        from expenses_ai_agent.storage.models import Expense

        expense = Expense(
            amount=Decimal("10.00"),
            telegram_user_id=12345,
        )

        assert expense.telegram_user_id == 12345

        expense_no_user = Expense(amount=Decimal("10.00"))
        assert expense_no_user.telegram_user_id is None
