from abc import ABC, abstractmethod
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Dict, Sequence

from sqlmodel import Session, create_engine, select

from expenses_ai_agent.storage.exceptions import (
    CategoryCreationError,
    CategoryNotFoundError,
    ExpenseNotFoundError,
)
from expenses_ai_agent.storage.models import (
    Currency,
    Expense,
    ExpenseCategory,
    UserPreference,
)


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

    @abstractmethod
    def list_by_user(self, telegram_user_id: int) -> Sequence[Expense]:
        """List all expenses for a specific user.

        Args:
            telegram_user_id: The Telegram user ID.

        Returns:
            Sequence[Expense]: A list of expenses for the user.
        """

    @abstractmethod
    def get_monthly_totals(
        self, telegram_user_id: int, months: int = 12
    ) -> Sequence[tuple[str, "Decimal"]]:
        """Get monthly expense totals for charts.

        Args:
            telegram_user_id: The Telegram user ID.
            months: Number of months to retrieve (default 12).

        Returns:
            Sequence of (month_str, total) tuples, e.g. [("2025-01", Decimal("150.00"))].
        """

    @abstractmethod
    def get_category_totals(
        self, telegram_user_id: int
    ) -> Sequence[tuple[str, "Decimal"]]:
        """Get total expenses grouped by category for a user.

        Args:
            telegram_user_id: The Telegram user ID.

        Returns:
            Sequence of (category_name, total) tuples.
        """

    @abstractmethod
    def get_unique_user_ids(self) -> Sequence[int]:
        """Get list of unique user IDs that have expenses.

        Returns:
            Sequence of unique telegram_user_id values.
        """


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

    def list_by_user(self, telegram_user_id: int) -> Sequence[Expense]:
        return [
            e for e in self.expenses.values() if e.telegram_user_id == telegram_user_id
        ]

    def get_monthly_totals(
        self, telegram_user_id: int, months: int = 12
    ) -> Sequence[tuple[str, Decimal]]:
        user_expenses = self.list_by_user(telegram_user_id)
        totals: Dict[str, Decimal] = defaultdict(Decimal)

        for expense in user_expenses:
            month_key = expense.date.strftime("%Y-%m")
            totals[month_key] += expense.amount

        # Sort by month and return last N months
        sorted_months = sorted(totals.items(), key=lambda x: x[0])
        return sorted_months[-months:]

    def get_category_totals(
        self, telegram_user_id: int
    ) -> Sequence[tuple[str, Decimal]]:
        user_expenses = self.list_by_user(telegram_user_id)
        totals: Dict[str, Decimal] = defaultdict(Decimal)

        for expense in user_expenses:
            category_name = (
                expense.category.name if expense.category else "Uncategorized"
            )
            totals[category_name] += expense.amount

        return list(totals.items())

    def get_unique_user_ids(self) -> Sequence[int]:
        user_ids = {
            e.telegram_user_id for e in self.expenses.values() if e.telegram_user_id
        }
        return sorted(user_ids)


class DBCategoryRepo(CategoryRepository):
    """A repository that uses a database to store categories"""

    def __init__(self, db_url: str, session: Session | None = None):
        """Initialize the repository with an optional SQLModel session."""
        if session:
            self.session = session
            self.engine = None
            self._owns_session = False
        else:
            self.engine = create_engine(db_url)
            self.session = Session(self.engine)
            self._owns_session = True

    def __enter__(self):  # pragma: no cover
        """Enter the context manager"""
        return self

    def __exit__(
        self, exc_type: str | None, exc_val: int, ext_tb: str | None
    ) -> None:  # pragma: no cover
        """Exit the context manager"""
        if self._owns_session:
            self.session.close()

    def add(self, category: ExpenseCategory) -> None:
        """Add a new ExpenseCategory"""
        if self._owns_session:
            with self.session as session:
                session.add(category)
                session.commit()
        else:
            self.session.add(category)
            self.session.commit()

    def update(self, category: ExpenseCategory) -> None:
        """Update an existing ExpenseCategory"""
        if self._owns_session:
            with self.session as session:
                db_category = session.get(ExpenseCategory, category.id)
                if not db_category:
                    raise CategoryNotFoundError()
                db_category.name = category.name
                session.add(db_category)
                session.commit()
        else:
            db_category = self.session.get(ExpenseCategory, category.id)
            if not db_category:
                raise CategoryNotFoundError()
            db_category.name = category.name
            self.session.add(db_category)
            self.session.commit()

    def get(self, name: str) -> ExpenseCategory | None:
        """Get a category by name"""
        if self._owns_session:
            with self.session as session:
                statement = select(ExpenseCategory).where(ExpenseCategory.name == name)
                results = session.exec(statement)
                category = results.first()
                if not category:
                    raise CategoryNotFoundError()
                return category
        else:
            statement = select(ExpenseCategory).where(ExpenseCategory.name == name)
            results = self.session.exec(statement)
            category = results.first()
            if not category:
                raise CategoryNotFoundError()
            return category

    def delete(self, name: str) -> None:
        """Delete a category by name"""
        if self._owns_session:
            with self.session as session:
                statement = select(ExpenseCategory).where(ExpenseCategory.name == name)
                results = session.exec(statement)
                category = results.first()
                if not category:
                    raise CategoryNotFoundError()
                session.delete(category)
                session.commit()
        else:
            statement = select(ExpenseCategory).where(ExpenseCategory.name == name)
            results = self.session.exec(statement)
            category = results.first()
            if not category:
                raise CategoryNotFoundError()
            self.session.delete(category)
            self.session.commit()

    def list(self) -> Sequence[str]:
        """List all categories"""
        if self._owns_session:
            with self.session as session:
                statement = select(ExpenseCategory)
                results = session.exec(statement)
                categories = results.all()
                return [category.name for category in categories]
        else:
            statement = select(ExpenseCategory)
            results = self.session.exec(statement)
            categories = results.all()
            return [category.name for category in categories]


class DBExpenseRepo(ExpenseRepository):
    """A repository that uses a database to store expenses"""

    def __init__(self, db_url: str, session: Session | None = None):
        """Initialize the repository with an optional SQLModel session."""
        if session:
            self.session = session
            self.engine = None
            self._owns_session = False
        else:
            self.engine = create_engine(db_url)
            self.session = Session(self.engine)
            self._owns_session = True

    def __enter__(self):  # pragma: no cover
        """Enter the context manager"""
        return self

    def __exit__(
        self, exc_type: str | None, exc_val: int, ext_tb: str | None
    ) -> None:  # pragma: no cover
        """Exit the context manager"""
        if self._owns_session:
            self.session.close()

    def add(self, expense: Expense) -> None:
        """Add a new Expense"""
        if self._owns_session:
            with self.session as session:
                session.add(expense)
                session.commit()
        else:
            self.session.add(expense)
            self.session.commit()

    def update(self, expense: Expense) -> None:
        """Update an existing Expense"""
        if self._owns_session:
            with self.session as session:
                db_expense = session.get(Expense, expense.id)
                if not db_expense:
                    raise ExpenseNotFoundError()
                db_expense.amount = expense.amount
                db_expense.currency = expense.currency
                db_expense.description = expense.description
                db_expense.date = expense.date
                db_expense.category_id = expense.category_id
                session.add(db_expense)
                session.commit()
        else:
            db_expense = self.session.get(Expense, expense.id)
            if not db_expense:
                raise ExpenseNotFoundError()
            db_expense.amount = expense.amount
            db_expense.currency = expense.currency
            db_expense.description = expense.description
            db_expense.date = expense.date
            db_expense.category_id = expense.category_id
            self.session.add(db_expense)
            self.session.commit()

    def get(self, expense_id: int) -> Expense | None:
        """Get an expense by id"""
        if self._owns_session:
            with self.session as session:
                expense = session.get(Expense, expense_id)
                if not expense:
                    raise ExpenseNotFoundError()
                return expense
        else:
            expense = self.session.get(Expense, expense_id)
            if not expense:
                raise ExpenseNotFoundError()
            return expense

    def search_by_dates(
        self, from_date: datetime, to_date: datetime
    ) -> Sequence[Expense]:
        """Seach for expeneses within a date range."""
        if self._owns_session:
            with self.session as session:
                statement = select(Expense).where(
                    Expense.date >= from_date, Expense.date <= to_date
                )
                results = session.exec(statement)
                expenses = results.all()
                if not expenses:
                    raise ExpenseNotFoundError()
                return expenses
        else:
            statement = select(Expense).where(
                Expense.date >= from_date, Expense.date <= to_date
            )
            results = self.session.exec(statement)
            expenses = results.all()
            if not expenses:
                raise ExpenseNotFoundError()
            return expenses

    def search_by_category(self, category: ExpenseCategory) -> Sequence[Expense]:
        """Search for expenses by category."""
        if self._owns_session:
            with self.session as session:
                statement = select(Expense).where(Expense.category_id == category.id)
                results = session.exec(statement)
                expenses = results.all()
                if not expenses:
                    raise ExpenseNotFoundError()
                return expenses
        else:
            statement = select(Expense).where(Expense.category_id == category.id)
            results = self.session.exec(statement)
            expenses = results.all()
            if not expenses:
                raise ExpenseNotFoundError()
            return expenses

    def delete(self, expense_id: int) -> None:
        """Delete an expense by ID."""
        if self._owns_session:
            with self.session as session:
                expense = session.get(Expense, expense_id)
                if not expense:
                    raise ExpenseNotFoundError()
                session.delete(expense)
                session.commit()
        else:
            expense = self.session.get(Expense, expense_id)
            if not expense:
                raise ExpenseNotFoundError()
            self.session.delete(expense)
            self.session.commit()

    def list(self) -> Sequence[Expense]:
        """List all expenses."""
        if self._owns_session:
            with self.session as session:
                statement = select(Expense)
                results = session.exec(statement)
                expenses = results.all()
                return expenses
        else:
            statement = select(Expense)
            results = self.session.exec(statement)
            expenses = results.all()
            return expenses

    def list_by_user(self, telegram_user_id: int) -> Sequence[Expense]:
        """List all expenses for a specific user."""
        if self._owns_session:
            with self.session as session:
                statement = select(Expense).where(
                    Expense.telegram_user_id == telegram_user_id
                )
                results = session.exec(statement)
                return results.all()
        else:
            statement = select(Expense).where(
                Expense.telegram_user_id == telegram_user_id
            )
            results = self.session.exec(statement)
            return results.all()

    def get_monthly_totals(
        self, telegram_user_id: int, months: int = 12
    ) -> Sequence[tuple[str, Decimal]]:
        """Get monthly expense totals for charts."""
        expenses = self.list_by_user(telegram_user_id)
        totals: Dict[str, Decimal] = defaultdict(Decimal)

        for expense in expenses:
            month_key = expense.date.strftime("%Y-%m")
            totals[month_key] += expense.amount

        sorted_months = sorted(totals.items(), key=lambda x: x[0])
        return sorted_months[-months:]

    def get_category_totals(
        self, telegram_user_id: int
    ) -> Sequence[tuple[str, Decimal]]:
        """Get total expenses grouped by category for a user."""
        expenses = self.list_by_user(telegram_user_id)
        totals: Dict[str, Decimal] = defaultdict(Decimal)

        for expense in expenses:
            category_name = (
                expense.category.name if expense.category else "Uncategorized"
            )
            totals[category_name] += expense.amount

        return list(totals.items())

    def get_unique_user_ids(self) -> Sequence[int]:
        """Get list of unique user IDs that have expenses."""
        if self._owns_session:
            with self.session as session:
                statement = (
                    select(Expense.telegram_user_id)
                    .distinct()
                    .where(
                        Expense.telegram_user_id.isnot(None)  # type: ignore[union-attr]
                    )
                )
                results = session.exec(statement)
                return sorted(results.all())
        else:
            statement = (
                select(Expense.telegram_user_id)
                .distinct()
                .where(
                    Expense.telegram_user_id.isnot(None)  # type: ignore[union-attr]
                )
            )
            results = self.session.exec(statement)
            return sorted(results.all())


class UserPreferenceRepository(ABC):
    """Abstract base class for user preference repositories."""

    @abstractmethod
    def get_by_user_id(self, telegram_user_id: int) -> UserPreference | None:
        """Get user preference by Telegram user ID.

        Args:
            telegram_user_id: The Telegram user ID.

        Returns:
            UserPreference if found, None otherwise.
        """

    @abstractmethod
    def upsert(self, telegram_user_id: int, currency: Currency) -> UserPreference:
        """Create or update a user preference.

        Args:
            telegram_user_id: The Telegram user ID.
            currency: The preferred currency.

        Returns:
            The created or updated UserPreference.
        """


class InMemoryUserPreferenceRepo(UserPreferenceRepository):
    """In-memory implementation of UserPreferenceRepository."""

    def __init__(self) -> None:
        self.preferences: Dict[int, UserPreference] = {}

    def get_by_user_id(self, telegram_user_id: int) -> UserPreference | None:
        return self.preferences.get(telegram_user_id)

    def upsert(self, telegram_user_id: int, currency: Currency) -> UserPreference:
        from datetime import datetime, timezone

        existing = self.preferences.get(telegram_user_id)
        if existing:
            existing.preferred_currency = currency
            existing.updated_at = datetime.now(timezone.utc)
            return existing
        else:
            pref = UserPreference(
                telegram_user_id=telegram_user_id,
                preferred_currency=currency,
            )
            self.preferences[telegram_user_id] = pref
            return pref


class DBUserPreferenceRepo(UserPreferenceRepository):
    """Database implementation of UserPreferenceRepository."""

    def __init__(self, db_url: str, session: Session | None = None) -> None:
        """Initialize the repository with an optional SQLModel session."""
        if session:
            self.session = session
            self.engine = None
            self._owns_session = False
        else:
            self.engine = create_engine(db_url)
            self.session = Session(self.engine)
            self._owns_session = True

    def __enter__(self):  # pragma: no cover
        """Enter the context manager."""
        return self

    def __exit__(
        self, exc_type: str | None, exc_val: int, ext_tb: str | None
    ) -> None:  # pragma: no cover
        """Exit the context manager."""
        if self._owns_session:
            self.session.close()

    def get_by_user_id(self, telegram_user_id: int) -> UserPreference | None:
        """Get user preference by Telegram user ID."""
        if self._owns_session:
            with self.session as session:
                statement = select(UserPreference).where(
                    UserPreference.telegram_user_id == telegram_user_id
                )
                results = session.exec(statement)
                return results.first()
        else:
            statement = select(UserPreference).where(
                UserPreference.telegram_user_id == telegram_user_id
            )
            results = self.session.exec(statement)
            return results.first()

    def upsert(self, telegram_user_id: int, currency: Currency) -> UserPreference:
        """Create or update a user preference."""
        from datetime import datetime, timezone

        if self._owns_session:
            with self.session as session:
                statement = select(UserPreference).where(
                    UserPreference.telegram_user_id == telegram_user_id
                )
                results = session.exec(statement)
                existing = results.first()

                if existing:
                    existing.preferred_currency = currency
                    existing.updated_at = datetime.now(timezone.utc)
                    session.add(existing)
                    session.commit()
                    session.refresh(existing)
                    return existing
                else:
                    pref = UserPreference(
                        telegram_user_id=telegram_user_id,
                        preferred_currency=currency,
                    )
                    session.add(pref)
                    session.commit()
                    session.refresh(pref)
                    return pref
        else:
            statement = select(UserPreference).where(
                UserPreference.telegram_user_id == telegram_user_id
            )
            results = self.session.exec(statement)
            existing = results.first()

            if existing:
                existing.preferred_currency = currency
                existing.updated_at = datetime.now(timezone.utc)
                self.session.add(existing)
                self.session.commit()
                self.session.refresh(existing)
                return existing
            else:
                pref = UserPreference(
                    telegram_user_id=telegram_user_id,
                    preferred_currency=currency,
                )
                self.session.add(pref)
                self.session.commit()
                self.session.refresh(pref)
                return pref
