"""Tests for multiuser repository methods."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlmodel import Session, SQLModel, create_engine

from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import DBCategoryRepo, DBExpenseRepo, InMemoryExpenseRepository


# ------------------------------------------------------------------
# InMemoryExpenseRepository multiuser tests
# ------------------------------------------------------------------


class TestInMemoryExpenseRepoMultiuser:
    """Tests for InMemoryExpenseRepository multiuser methods."""

    def test_list_by_user_empty(self) -> None:
        """Test list_by_user returns empty for unknown user."""
        repo = InMemoryExpenseRepository()
        result = repo.list_by_user(999)
        assert result == []

    def test_list_by_user_filters_correctly(self) -> None:
        """Test list_by_user only returns user's expenses."""
        repo = InMemoryExpenseRepository()
        category = ExpenseCategory(id=1, name="Test")

        # Add expenses for different users
        expense1 = Expense(
            amount=Decimal("10.00"),
            currency=Currency.USD,
            category=category,
            telegram_user_id=100,
        )
        expense2 = Expense(
            amount=Decimal("20.00"),
            currency=Currency.USD,
            category=category,
            telegram_user_id=200,
        )
        expense3 = Expense(
            amount=Decimal("30.00"),
            currency=Currency.USD,
            category=category,
            telegram_user_id=100,
        )

        repo.add(expense1)
        repo.add(expense2)
        repo.add(expense3)

        # User 100 should see only their expenses
        user_100_expenses = repo.list_by_user(100)
        assert len(user_100_expenses) == 2
        assert all(e.telegram_user_id == 100 for e in user_100_expenses)

        # User 200 should see only their expenses
        user_200_expenses = repo.list_by_user(200)
        assert len(user_200_expenses) == 1
        assert user_200_expenses[0].telegram_user_id == 200

    def test_get_category_totals_empty(self) -> None:
        """Test get_category_totals returns empty for unknown user."""
        repo = InMemoryExpenseRepository()
        result = repo.get_category_totals(999)
        assert result == []

    def test_get_category_totals_aggregates_correctly(self) -> None:
        """Test get_category_totals groups by category."""
        repo = InMemoryExpenseRepository()
        food = ExpenseCategory(id=1, name="Food")
        transport = ExpenseCategory(id=2, name="Transport")

        # Add expenses
        repo.add(Expense(
            amount=Decimal("10.00"),
            currency=Currency.USD,
            category=food,
            telegram_user_id=100,
        ))
        repo.add(Expense(
            amount=Decimal("20.00"),
            currency=Currency.USD,
            category=food,
            telegram_user_id=100,
        ))
        repo.add(Expense(
            amount=Decimal("15.00"),
            currency=Currency.USD,
            category=transport,
            telegram_user_id=100,
        ))
        # Different user - should not be counted
        repo.add(Expense(
            amount=Decimal("50.00"),
            currency=Currency.USD,
            category=food,
            telegram_user_id=200,
        ))

        result = repo.get_category_totals(100)
        totals = {cat: total for cat, total in result}

        assert totals["Food"] == Decimal("30.00")
        assert totals["Transport"] == Decimal("15.00")

    def test_get_monthly_totals_empty(self) -> None:
        """Test get_monthly_totals returns empty for unknown user."""
        repo = InMemoryExpenseRepository()
        result = repo.get_monthly_totals(999)
        assert result == []

    def test_get_monthly_totals_groups_by_month(self) -> None:
        """Test get_monthly_totals groups expenses by month."""
        repo = InMemoryExpenseRepository()
        category = ExpenseCategory(id=1, name="Test")

        now = datetime.now(timezone.utc)
        last_month = now - timedelta(days=35)

        repo.add(Expense(
            amount=Decimal("10.00"),
            currency=Currency.USD,
            category=category,
            date=now,
            telegram_user_id=100,
        ))
        repo.add(Expense(
            amount=Decimal("20.00"),
            currency=Currency.USD,
            category=category,
            date=now,
            telegram_user_id=100,
        ))
        repo.add(Expense(
            amount=Decimal("15.00"),
            currency=Currency.USD,
            category=category,
            date=last_month,
            telegram_user_id=100,
        ))

        result = repo.get_monthly_totals(100, months=12)
        totals = {month: total for month, total in result}

        current_month = now.strftime("%Y-%m")
        prev_month = last_month.strftime("%Y-%m")

        assert totals[current_month] == Decimal("30.00")
        assert totals[prev_month] == Decimal("15.00")


# ------------------------------------------------------------------
# DBExpenseRepo multiuser tests
# ------------------------------------------------------------------


@pytest.fixture
def db_session():
    """Create in-memory SQLite session for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


class TestDBExpenseRepoMultiuser:
    """Tests for DBExpenseRepo multiuser methods."""

    def test_list_by_user_empty(self, db_session: Session) -> None:
        """Test list_by_user returns empty for unknown user."""
        repo = DBExpenseRepo("sqlite:///:memory:", session=db_session)
        result = repo.list_by_user(999)
        assert result == []

    def test_list_by_user_filters_correctly(self, db_session: Session) -> None:
        """Test list_by_user only returns user's expenses."""
        cat_repo = DBCategoryRepo("sqlite:///:memory:", session=db_session)
        repo = DBExpenseRepo("sqlite:///:memory:", session=db_session)

        category = ExpenseCategory(name="Test")
        cat_repo.add(category)

        # Add expenses for different users
        expense1 = Expense(
            amount=Decimal("10.00"),
            currency=Currency.USD,
            category=category,
            telegram_user_id=100,
        )
        expense2 = Expense(
            amount=Decimal("20.00"),
            currency=Currency.USD,
            category=category,
            telegram_user_id=200,
        )

        repo.add(expense1)
        repo.add(expense2)

        user_100_expenses = repo.list_by_user(100)
        assert len(user_100_expenses) == 1
        assert user_100_expenses[0].telegram_user_id == 100

    def test_get_category_totals_aggregates(self, db_session: Session) -> None:
        """Test get_category_totals groups by category."""
        cat_repo = DBCategoryRepo("sqlite:///:memory:", session=db_session)
        repo = DBExpenseRepo("sqlite:///:memory:", session=db_session)

        food = ExpenseCategory(name="Food")
        transport = ExpenseCategory(name="Transport")
        cat_repo.add(food)
        cat_repo.add(transport)

        repo.add(Expense(
            amount=Decimal("10.00"),
            currency=Currency.USD,
            category=food,
            telegram_user_id=100,
        ))
        repo.add(Expense(
            amount=Decimal("20.00"),
            currency=Currency.USD,
            category=food,
            telegram_user_id=100,
        ))
        repo.add(Expense(
            amount=Decimal("15.00"),
            currency=Currency.USD,
            category=transport,
            telegram_user_id=100,
        ))

        result = repo.get_category_totals(100)
        totals = {cat: total for cat, total in result}

        assert totals["Food"] == Decimal("30.00")
        assert totals["Transport"] == Decimal("15.00")

    def test_get_monthly_totals_groups_by_month(self, db_session: Session) -> None:
        """Test get_monthly_totals groups expenses by month."""
        cat_repo = DBCategoryRepo("sqlite:///:memory:", session=db_session)
        repo = DBExpenseRepo("sqlite:///:memory:", session=db_session)

        category = ExpenseCategory(name="Test")
        cat_repo.add(category)

        now = datetime.now(timezone.utc)

        repo.add(Expense(
            amount=Decimal("10.00"),
            currency=Currency.USD,
            category=category,
            date=now,
            telegram_user_id=100,
        ))
        repo.add(Expense(
            amount=Decimal("20.00"),
            currency=Currency.USD,
            category=category,
            date=now,
            telegram_user_id=100,
        ))

        result = repo.get_monthly_totals(100, months=12)

        # Should have at least one entry for current month
        assert len(result) >= 1
        current_month = now.strftime("%Y-%m")
        totals = {month: total for month, total in result}
        assert totals[current_month] == Decimal("30.00")
