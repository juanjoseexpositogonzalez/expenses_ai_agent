"""
Week 3 - Definition of Done: Database Repositories

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week3_db_repos.py -v
All tests must pass to complete Week 3's database repository milestone.

These tests verify your implementation of:
- DBCategoryRepo with SQLModel
- DBExpenseRepo with SQLModel
- Session management (owned vs injected)
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from sqlmodel import Session, SQLModel, create_engine


@pytest.fixture
def db_engine():
    """Create an in-memory SQLite engine for testing."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    """Create a test session."""
    with Session(db_engine) as session:
        yield session


class TestDBCategoryRepo:
    """Tests for the database-backed category repository."""

    def test_db_category_repo_with_injected_session(self, db_session):
        """DBCategoryRepo should accept an injected session."""
        from expenses_ai_agent.storage.models import ExpenseCategory
        from expenses_ai_agent.storage.repo import DBCategoryRepo

        repo = DBCategoryRepo(db_url="sqlite:///:memory:", session=db_session)

        category = ExpenseCategory.create(name="Food")
        repo.add(category)

        result = repo.get("Food")
        assert result is not None
        assert result.name == "Food"

    def test_db_category_repo_list(self, db_session):
        """Should list all category names."""
        from expenses_ai_agent.storage.models import ExpenseCategory
        from expenses_ai_agent.storage.repo import DBCategoryRepo

        repo = DBCategoryRepo(db_url="sqlite:///:memory:", session=db_session)

        repo.add(ExpenseCategory.create(name="Food"))
        repo.add(ExpenseCategory.create(name="Transport"))

        names = repo.list()

        assert len(names) == 2
        assert "Food" in names
        assert "Transport" in names

    def test_db_category_repo_delete(self, db_session):
        """Should be able to delete a category."""
        from expenses_ai_agent.storage.models import ExpenseCategory
        from expenses_ai_agent.storage.repo import DBCategoryRepo

        repo = DBCategoryRepo(db_url="sqlite:///:memory:", session=db_session)

        repo.add(ExpenseCategory.create(name="ToDelete"))
        repo.delete("ToDelete")

        assert repo.get("ToDelete") is None

    def test_db_category_repo_delete_nonexistent_raises(self, db_session):
        """Deleting non-existent category should raise error."""
        from expenses_ai_agent.storage.exceptions import CategoryNotFoundError
        from expenses_ai_agent.storage.repo import DBCategoryRepo

        repo = DBCategoryRepo(db_url="sqlite:///:memory:", session=db_session)

        with pytest.raises(CategoryNotFoundError):
            repo.delete("NonExistent")


class TestDBExpenseRepo:
    """Tests for the database-backed expense repository."""

    @pytest.fixture
    def category_in_db(self, db_session):
        """Create a category in the test database."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        category = ExpenseCategory.create(name="Food")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    def test_db_expense_repo_add_and_get(self, db_session, category_in_db):
        """Should add and retrieve expenses."""
        from expenses_ai_agent.storage.models import Currency, Expense
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        expense = Expense(
            amount=Decimal("42.50"),
            currency=Currency.EUR,
            description="Lunch",
            category=category_in_db,
        )
        repo.add(expense)

        result = repo.get(expense.id)
        assert result is not None
        assert result.amount == Decimal("42.50")
        assert result.description == "Lunch"

    def test_db_expense_repo_list(self, db_session):
        """Should list all expenses."""
        from expenses_ai_agent.storage.models import Currency, Expense
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        repo.add(Expense(amount=Decimal("10.00"), currency=Currency.EUR))
        repo.add(Expense(amount=Decimal("20.00"), currency=Currency.USD))

        expenses = repo.list()
        assert len(expenses) == 2

    def test_db_expense_repo_delete(self, db_session):
        """Should delete an expense."""
        from expenses_ai_agent.storage.models import Currency, Expense
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        expense = Expense(amount=Decimal("15.00"), currency=Currency.EUR)
        repo.add(expense)
        expense_id = expense.id

        repo.delete(expense_id)
        assert repo.get(expense_id) is None

    def test_db_expense_repo_delete_nonexistent_raises(self, db_session):
        """Deleting non-existent expense should raise error."""
        from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        with pytest.raises(ExpenseNotFoundError):
            repo.delete(99999)

    def test_db_expense_repo_search_by_category(self, db_session, category_in_db):
        """Should search expenses by category."""
        from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        transport = ExpenseCategory.create(name="Transport")
        db_session.add(transport)
        db_session.commit()
        db_session.refresh(transport)

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        repo.add(Expense(amount=Decimal("10"), currency=Currency.EUR, category=category_in_db))
        repo.add(Expense(amount=Decimal("20"), currency=Currency.EUR, category=category_in_db))
        repo.add(Expense(amount=Decimal("30"), currency=Currency.EUR, category=transport))

        food_expenses = repo.search_by_category(category_in_db)
        assert len(food_expenses) == 2

    def test_db_expense_repo_search_by_dates(self, db_session):
        """Should search expenses by date range."""
        from expenses_ai_agent.storage.models import Currency, Expense
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)

        # Add expenses with different dates
        expense1 = Expense(amount=Decimal("10"), currency=Currency.EUR, date=now)
        expense2 = Expense(amount=Decimal("20"), currency=Currency.EUR, date=yesterday)
        expense3 = Expense(amount=Decimal("30"), currency=Currency.EUR, date=last_week)

        repo.add(expense1)
        repo.add(expense2)
        repo.add(expense3)

        # Search for last 3 days
        start = now - timedelta(days=3)
        results = repo.search_by_dates(start, now)

        assert len(results) == 2  # expense1 and expense2

    def test_db_expense_repo_list_by_user(self, db_session):
        """Should filter expenses by telegram user ID."""
        from expenses_ai_agent.storage.models import Currency, Expense
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        repo.add(Expense(amount=Decimal("10"), currency=Currency.EUR, telegram_user_id=100))
        repo.add(Expense(amount=Decimal("20"), currency=Currency.EUR, telegram_user_id=100))
        repo.add(Expense(amount=Decimal("30"), currency=Currency.EUR, telegram_user_id=200))

        user_100_expenses = repo.list_by_user(telegram_user_id=100)
        assert len(user_100_expenses) == 2
