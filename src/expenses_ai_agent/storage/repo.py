from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Sequence

from sqlmodel import Session, create_engine, select

from expenses_ai_agent.storage.exceptions import (
    CategoryCreationError,
    CategoryNotFoundError,
    ExpenseNotFoundError,
)
from expenses_ai_agent.storage.models import Expense, ExpenseCategory


class CategoryRepository(ABC):
    """Abstract base class for category repositories."""

    @abstractmethod
    def add(self, category: ExpenseCategory) -> None:
        """Add a new ExpenseCategory.

        Args:
            name (ExpenseCategory): The name of the category to add.

        Raises:
            CategoryCreationError: If the category already exists.

        Returns:
            None
        """

    @abstractmethod
    def update(self, category: ExpenseCategory) -> None:
        """Update an existing ExpenseCategory.

        Args:
            category (ExpenseCategory): The category to update.

        Raises:
            CategoryNotFoundError: If the category is not found.

        Returns:
            None
        """

    @abstractmethod
    def get(self, name: str) -> ExpenseCategory | None:
        """Get a category by name.

        Args:
            name (str): The name of the category to retrieve.

        Raises:
            CategoryNotFoundError: If the category is not found.

        Returns:
            ExpenseCategory | None: The retrieved category or None if not found.
        """

    @abstractmethod
    def delete(self, name: str) -> None:
        """Delete a category by name.

        Args:
            name (str): The name of the category to delete.

        Raises:
            CategoryNotFoundError: If the category is not found.

        Returns:
            None
        """

    @abstractmethod
    def list(self) -> Sequence[str]:
        """List all categories.

        Returns:
            Sequence[str]: A list of category names.
        """


class ExpenseRepository(ABC):
    """Abstract base class for expense repositories."""

    @abstractmethod
    def add(self, expense: Expense) -> None:
        """Add a new Expense."""

    @abstractmethod
    def get(self, expense_id: int) -> Expense | None:
        """Get an expense by id.

        Args:
            expense_id (int): The ID of the expense to retrieve.

        Raises:
            ExpenseNotFoundError: If the expense is not found.

        Returns:
            Expense | None: The retrieved expense or None if not found.
        """

    @abstractmethod
    def search_by_dates(
        self, from_date: datetime, to_date: datetime
    ) -> Sequence[Expense]:
        """Seach for expeneses within a date range.

        Args:
            from_date (datetime): The start date of the range.
            to_date (datetime): The end date of the range.

        Raises:
            ExpenseNotFoundError: If no expenses are found within the date range.

        Returns:
            Sequence[Expense]: A list of expenses within the date range.
        """

    @abstractmethod
    def search_by_category(self, category: ExpenseCategory) -> Sequence[Expense]:
        """Search for expenses by category.

        Args:
            category (ExpenseCategory): The category to search for.
        Raises:
            ExpenseNotFoundError: If no expenses are found for the category.
        Returns:
            Sequence[Expense]: A list of expenses for the category.
        """

    @abstractmethod
    def update(self, expense: Expense) -> None:
        """Update an existing expense.

        Args:
            expense (Expense): The expense to update.

        Raises:
            ExpenseNotFoundError: If the expense is not found.

        Returns:
            None
        """

    @abstractmethod
    def delete(self, expense_id: int) -> None:
        """Delete an expense by ID.

        Args:
            expense_id (int): The ID of the expense to delete.
        Raises:
            ExpenseNotFoundError: If the expense is not found.

        Returns:
            None
        """

    @abstractmethod
    def list(self) -> Sequence[Expense]:
        """List all expenses."""


class InMemoryCategoryRepository(CategoryRepository):
    """In-memory implementation of CategoryRepository."""

    def __init__(self):
        self.categories: Dict[str, ExpenseCategory] = {}

    def add(self, category: ExpenseCategory) -> None:
        if category.name in self.categories:
            raise CategoryCreationError("Category already exists")
        self.categories[category.name] = category

    def update(self, category: ExpenseCategory) -> None:
        if category.name not in self.categories:
            raise CategoryNotFoundError()
        self.categories[category.name] = category

    def get(self, name: str) -> ExpenseCategory | None:
        category = self.categories.get(name)
        if not category:
            raise CategoryNotFoundError()
        return category

    def delete(self, name: str) -> None:
        if name not in self.categories:
            raise CategoryNotFoundError()
        del self.categories[name]

    def list(self) -> Sequence[str]:
        return list(self.categories.keys())


class InMemoryExpenseRepository(ExpenseRepository):
    """In-memory implementation of ExpenseRepository."""

    def __init__(self):
        self.expenses: Dict[int, Expense] = {}
        self.next_id = 1

    def add(self, expense: Expense) -> None:
        expense.id = self.next_id
        self.expenses[self.next_id] = expense
        self.next_id += 1

    def get(self, expense_id: int) -> Expense | None:
        expense = self.expenses.get(expense_id)
        if not expense:
            raise ExpenseNotFoundError("Expense not found")
        return expense

    def search_by_dates(
        self, from_date: datetime, to_date: datetime
    ) -> Sequence[Expense]:
        results = [
            expense
            for expense in self.expenses.values()
            if from_date <= expense.date <= to_date
        ]
        if not results:
            raise ExpenseNotFoundError("No expenses found in the given date range")
        return results

    def search_by_category(self, category: ExpenseCategory) -> Sequence[Expense]:
        results = [
            expense
            for expense in self.expenses.values()
            if expense.category == category
        ]
        if not results:
            raise ExpenseNotFoundError("No expenses found for the given category")
        return results

    def update(self, expense: Expense) -> None:
        if expense.id not in self.expenses:
            raise ExpenseNotFoundError("Expense not found")
        self.expenses[expense.id] = expense

    def delete(self, expense_id: int) -> None:
        if expense_id not in self.expenses:
            raise ExpenseNotFoundError("Expense not found")
        del self.expenses[expense_id]

    def list(self) -> Sequence[Expense]:
        return list(self.expenses.values())


class DBCategoryRepo(CategoryRepository):
    """A repository that uses a database to store categories"""

    def __init__(self, db_url: str):
        """Initialize the repository with an optional SQLModel session."""
        self.engine = create_engine(db_url)
        self.session = Session(self.engine)

    def __enter__(self):  # pragma: no cover
        """Enter the context manager"""
        return self

    def __exit__(
        self, exc_type: str | None, exc_val: int, ext_tb: str | None
    ) -> None:  # pragma: no cover
        """Exit the context manager"""
        self.session.close()

    def add(self, category: ExpenseCategory) -> None:
        """Add a new ExpenseCategory"""
        with self.session as session:
            session.add(category)
            session.commit()

    def update(self, category: ExpenseCategory) -> None:
        """Update an existing ExpenseCategory"""
        with self.session as session:
            db_category = session.get(ExpenseCategory, category.id)
            if not db_category:
                raise CategoryNotFoundError()
            db_category.name = category.name
            session.add(db_category)
            session.commit()

    def get(self, name: str) -> ExpenseCategory | None:
        """Get a category by name"""
        with self.session as session:
            statement = select(ExpenseCategory).where(ExpenseCategory.name == name)
            results = session.exec(statement)
            category = results.first()
            if not category:
                raise CategoryNotFoundError()
            return category

    def delete(self, name: str) -> None:
        """Delete a category by name"""
        with self.session as session:
            statement = select(ExpenseCategory).where(ExpenseCategory.name == name)
            results = session.exec(statement)
            category = results.first()
            if not category:
                raise CategoryNotFoundError()
            session.delete(category)
            session.commit()

    def list(self) -> Sequence[str]:
        """List all categories"""
        with self.session as session:
            statement = select(ExpenseCategory)
            results = session.exec(statement)
            categories = results.all()
            return [category.name for category in categories]
