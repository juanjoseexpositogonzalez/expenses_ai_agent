"""
Week 1 - Definition of Done: In-Memory Repositories

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week1_repos.py -v
All tests must pass to complete Week 1's repository milestone.

These tests verify your implementation of:
- CategoryRepository abstract base class
- ExpenseRepository abstract base class
- InMemoryCategoryRepository (dict-backed)
- InMemoryExpenseRepository (dict-backed)
- Custom exceptions for not-found cases
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest


class TestStorageExceptions:
    """Tests for custom storage exceptions."""

    def test_category_not_found_error_exists(self):
        """CategoryNotFoundError should be a custom exception."""
        from expenses_ai_agent.storage.exceptions import CategoryNotFoundError

        error = CategoryNotFoundError("Food")
        assert isinstance(error, Exception)
        assert "Food" in str(error)

    def test_expense_not_found_error_exists(self):
        """ExpenseNotFoundError should be a custom exception."""
        from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError

        error = ExpenseNotFoundError(123)
        assert isinstance(error, Exception)
        assert "123" in str(error)


class TestInMemoryCategoryRepository:
    """Tests for the in-memory category repository."""

    @pytest.fixture
    def repo(self):
        """Create a fresh in-memory category repository for each test."""
        from expenses_ai_agent.storage.repo import InMemoryCategoryRepository

        return InMemoryCategoryRepository()

    @pytest.fixture
    def sample_category(self):
        """Create a sample category for testing."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        return ExpenseCategory.create(name="Food")

    def test_add_category(self, repo, sample_category):
        """Should be able to add a category to the repository."""
        repo.add(sample_category)

        result = repo.get("Food")
        assert result is not None
        assert result.name == "Food"

    def test_get_nonexistent_category_returns_none(self, repo):
        """Getting a non-existent category should return None."""
        result = repo.get("NonExistent")
        assert result is None

    def test_list_categories(self, repo):
        """Should list all category names."""
        from expenses_ai_agent.storage.models import ExpenseCategory

        repo.add(ExpenseCategory.create(name="Food"))
        repo.add(ExpenseCategory.create(name="Transport"))
        repo.add(ExpenseCategory.create(name="Entertainment"))

        names = repo.list()

        assert len(names) == 3
        assert "Food" in names
        assert "Transport" in names
        assert "Entertainment" in names

    def test_update_category(self, repo, sample_category):
        """Should be able to update an existing category."""
        repo.add(sample_category)

        # Modify the category
        sample_category.name = "Groceries"
        repo.update(sample_category)

        # Original name should no longer exist
        assert repo.get("Food") is None
        # New name should exist
        result = repo.get("Groceries")
        assert result is not None
        assert result.name == "Groceries"

    def test_delete_category(self, repo, sample_category):
        """Should be able to delete a category."""
        repo.add(sample_category)
        repo.delete("Food")

        assert repo.get("Food") is None

    def test_delete_nonexistent_raises(self, repo):
        """Deleting a non-existent category should raise CategoryNotFoundError."""
        from expenses_ai_agent.storage.exceptions import CategoryNotFoundError

        with pytest.raises(CategoryNotFoundError):
            repo.delete("NonExistent")


class TestInMemoryExpenseRepository:
    """Tests for the in-memory expense repository."""

    @pytest.fixture
    def repo(self):
        """Create a fresh in-memory expense repository for each test."""
        from expenses_ai_agent.storage.repo import InMemoryExpenseRepository

        return InMemoryExpenseRepository()

    @pytest.fixture
    def sample_expense(self):
        """Create a sample expense for testing."""
        from expenses_ai_agent.storage.models import Currency, Expense

        return Expense(
            amount=Decimal("42.50"),
            currency=Currency.EUR,
            description="Test expense",
        )

    def test_add_expense_assigns_id(self, repo, sample_expense):
        """Adding an expense should assign an auto-incremented ID."""
        assert sample_expense.id is None

        repo.add(sample_expense)

        assert sample_expense.id is not None
        assert sample_expense.id >= 1

    def test_get_expense_by_id(self, repo, sample_expense):
        """Should retrieve expense by ID."""
        repo.add(sample_expense)

        result = repo.get(sample_expense.id)

        assert result is not None
        assert result.amount == Decimal("42.50")

    def test_get_nonexistent_returns_none(self, repo):
        """Getting a non-existent expense should return None."""
        result = repo.get(999)
        assert result is None

    def test_list_all_expenses(self, repo):
        """Should list all expenses."""
        from expenses_ai_agent.storage.models import Currency, Expense

        repo.add(Expense(amount=Decimal("10.00"), currency=Currency.EUR))
        repo.add(Expense(amount=Decimal("20.00"), currency=Currency.USD))

        expenses = repo.list()

        assert len(expenses) == 2

    def test_delete_expense(self, repo, sample_expense):
        """Should be able to delete an expense."""
        repo.add(sample_expense)
        expense_id = sample_expense.id

        repo.delete(expense_id)

        assert repo.get(expense_id) is None

    def test_delete_nonexistent_raises(self, repo):
        """Deleting a non-existent expense should raise ExpenseNotFoundError."""
        from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError

        with pytest.raises(ExpenseNotFoundError):
            repo.delete(999)

    def test_search_by_category(self, repo):
        """Should be able to search expenses by category."""
        from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory

        food = ExpenseCategory(id=1, name="Food")
        transport = ExpenseCategory(id=2, name="Transport")

        repo.add(Expense(amount=Decimal("10.00"), currency=Currency.EUR, category=food))
        repo.add(Expense(amount=Decimal("20.00"), currency=Currency.EUR, category=food))
        repo.add(Expense(amount=Decimal("30.00"), currency=Currency.EUR, category=transport))

        food_expenses = repo.search_by_category(food)

        assert len(food_expenses) == 2
        assert all(e.category.name == "Food" for e in food_expenses)


class TestRepositoryAbstractBase:
    """Tests to verify abstract base classes are properly defined."""

    def test_category_repository_is_abstract(self):
        """CategoryRepository should be an abstract base class."""
        from abc import ABC

        from expenses_ai_agent.storage.repo import CategoryRepository

        assert issubclass(CategoryRepository, ABC)

        # Should not be instantiable directly
        with pytest.raises(TypeError):
            CategoryRepository()

    def test_expense_repository_is_abstract(self):
        """ExpenseRepository should be an abstract base class."""
        from abc import ABC

        from expenses_ai_agent.storage.repo import ExpenseRepository

        assert issubclass(ExpenseRepository, ABC)

        # Should not be instantiable directly
        with pytest.raises(TypeError):
            ExpenseRepository()

    def test_inmemory_repos_inherit_from_abstract(self):
        """In-memory repositories should implement the abstract base classes."""
        from expenses_ai_agent.storage.repo import (
            CategoryRepository,
            ExpenseRepository,
            InMemoryCategoryRepository,
            InMemoryExpenseRepository,
        )

        assert issubclass(InMemoryCategoryRepository, CategoryRepository)
        assert issubclass(InMemoryExpenseRepository, ExpenseRepository)
