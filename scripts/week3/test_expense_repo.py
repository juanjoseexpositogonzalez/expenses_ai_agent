import logging
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Final

from decouple import config
from sqlmodel import Session, SQLModel, create_engine

from expenses_ai_agent.storage.exceptions import (
    CategoryNotFoundError,
    ExpenseNotFoundError,
)
from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import DBCategoryRepo, DBExpenseRepo

DB_URL: Final[str] = config("DB_URL", default="sqlite:///expenses.db")  # type: ignore
engine = create_engine(DB_URL, echo=False)  # type: ignore

# Create tables if they don't exist
SQLModel.metadata.create_all(engine)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_add_expense() -> None:
    """Test adding a new expense to the database."""
    logger.info("=== Test: Add Expense ===")

    with Session(engine) as session:
        # First, create a category
        category_repo = DBCategoryRepo(str(DB_URL), session)
        try:
            category = category_repo.get(name="Food & Dining")
            logger.info("Category 'Food & Dining' already exists")
        except CategoryNotFoundError:
            category = ExpenseCategory.create(name="Food & Dining")
            category_repo.add(category)
            session.refresh(category)
            logger.info("Category 'Food & Dining' created")

        # Create and add an expense
        expense = Expense.create(
            amount=Decimal("25.50"),
            currency=Currency.USD,
            description="Lunch at restaurant",
            category=category,
        )

        expense_repo = DBExpenseRepo(str(DB_URL), session)
        expense_repo.add(expense)
        session.refresh(expense)

        logger.info("✅ Expense added successfully: %s", expense)
        logger.info("   ID: %s", expense.id)
        logger.info("   Amount: %s %s", expense.amount, expense.currency.value)
        logger.info(
            "   Category: %s", expense.category.name if expense.category else "N/A"
        )


def test_get_expense() -> None:
    """Test retrieving an expense by ID."""
    logger.info("\n=== Test: Get Expense ===")

    with Session(engine) as session:
        # First, create a test expense
        category_repo = DBCategoryRepo(str(DB_URL), session)
        try:
            category = category_repo.get(name="Transportation")
        except CategoryNotFoundError:
            category = ExpenseCategory.create(name="Transportation")
            category_repo.add(category)
            session.refresh(category)

        expense = Expense.create(
            amount=Decimal("45.00"),
            currency=Currency.EUR,
            description="Taxi to airport",
            category=category,
        )

        expense_repo = DBExpenseRepo(str(DB_URL), session)
        expense_repo.add(expense)
        session.refresh(expense)
        expense_id = expense.id

        logger.info("Created expense with ID: %s", expense_id)

        # Now retrieve it
        retrieved_expense = expense_repo.get(expense_id)  # type: ignore
        logger.info("✅ Expense retrieved successfully: %s", retrieved_expense)
        logger.info(
            "   Amount: %s %s",
            retrieved_expense.amount,
            retrieved_expense.currency.value,
        )  # type: ignore


def test_update_expense() -> None:
    """Test updating an existing expense."""
    logger.info("\n=== Test: Update Expense ===")

    with Session(engine) as session:
        # Create a test expense
        category_repo = DBCategoryRepo(str(DB_URL), session)
        try:
            category = category_repo.get(name="Shopping")
        except CategoryNotFoundError:
            category = ExpenseCategory.create(name="Shopping")
            category_repo.add(category)
            session.refresh(category)

        expense = Expense.create(
            amount=Decimal("100.00"),
            currency=Currency.AUD,
            description="Office supplies - original",
            category=category,
        )

        expense_repo = DBExpenseRepo(str(DB_URL), session)
        expense_repo.add(expense)
        session.refresh(expense)

        logger.info("Original expense: %s", expense)

        # Update the expense
        expense.amount = Decimal("120.00")
        expense.description = "Office supplies - updated"
        expense_repo.update(expense)

        # Retrieve and verify
        updated_expense = expense_repo.get(expense.id)  # type: ignore
        logger.info("✅ Expense updated successfully: %s", updated_expense)
        logger.info(
            "   New amount: %s %s",
            updated_expense.amount,
            updated_expense.currency.value,
        )  # type: ignore
        logger.info("   New description: %s", updated_expense.description)  # type: ignore


def test_delete_expense() -> None:
    """Test deleting an expense."""
    logger.info("\n=== Test: Delete Expense ===")

    with Session(engine) as session:
        # Create a test expense
        category_repo = DBCategoryRepo(str(DB_URL), session)
        try:
            category = category_repo.get(name="Entertainment")
        except CategoryNotFoundError:
            category = ExpenseCategory.create(name="Entertainment")
            category_repo.add(category)
            session.refresh(category)

        expense = Expense.create(
            amount=Decimal("29.99"),
            currency=Currency.USD,
            description="Movie tickets",
            category=category,
        )

        expense_repo = DBExpenseRepo(str(DB_URL), session)
        expense_repo.add(expense)
        session.refresh(expense)
        expense_id = expense.id

        logger.info("Created expense with ID: %s", expense_id)

        # Delete the expense
        expense_repo.delete(expense_id)  # type: ignore
        logger.info("✅ Expense deleted successfully")

        # Try to retrieve it (should raise exception)
        try:
            expense_repo.get(expense_id)  # type: ignore
            logger.error("❌ Expense should not exist after deletion!")
        except ExpenseNotFoundError:
            logger.info("✅ Confirmed: Expense no longer exists in database")


def test_list_expenses() -> None:
    """Test listing all expenses."""
    logger.info("\n=== Test: List All Expenses ===")

    with Session(engine) as session:
        expense_repo = DBExpenseRepo(str(DB_URL), session)
        expenses = expense_repo.list()

        logger.info("✅ Found %d expenses in the database:", len(expenses))
        for expense in expenses:
            logger.info(
                "   - ID: %s | %s %s | %s | Category: %s",
                expense.id,
                expense.amount,
                expense.currency.value,
                expense.description,
                expense.category.name if expense.category else "N/A",
            )


def test_search_by_dates() -> None:
    """Test searching expenses by date range."""
    logger.info("\n=== Test: Search by Date Range ===")

    with Session(engine) as session:
        category_repo = DBCategoryRepo(str(DB_URL), session)
        try:
            category = category_repo.get(name="Subscriptions")
        except CategoryNotFoundError:
            category = ExpenseCategory.create(name="Subscriptions")
            category_repo.add(category)
            session.refresh(category)

        # Create expenses with different dates
        today = datetime.now(timezone.utc)
        yesterday = today - timedelta(days=1)
        last_week = today - timedelta(days=7)

        expenses_to_add = [
            Expense.create(
                amount=Decimal("9.99"),
                currency=Currency.USD,
                description="Netflix - today",
                date=today,
                category=category,
            ),
            Expense.create(
                amount=Decimal("14.99"),
                currency=Currency.USD,
                description="Spotify - yesterday",
                date=yesterday,
                category=category,
            ),
            Expense.create(
                amount=Decimal("19.99"),
                currency=Currency.USD,
                description="Amazon Prime - last week",
                date=last_week,
                category=category,
            ),
        ]

        expense_repo = DBExpenseRepo(str(DB_URL), session)
        for expense in expenses_to_add:
            expense_repo.add(expense)
            session.refresh(expense)
            logger.info("Added expense: %s", expense.description)

        # Search for expenses in the last 3 days
        from_date = today - timedelta(days=3)
        to_date = today + timedelta(days=1)

        results = expense_repo.search_by_dates(from_date, to_date)
        logger.info("✅ Found %d expenses in the last 3 days:", len(results))
        for expense in results:
            logger.info(
                "   - %s | %s %s | Date: %s",
                expense.description,
                expense.amount,
                expense.currency.value,
                expense.date.strftime("%Y-%m-%d %H:%M"),
            )


def test_search_by_category() -> None:
    """Test searching expenses by category."""
    logger.info("\n=== Test: Search by Category ===")

    with Session(engine) as session:
        category_repo = DBCategoryRepo(str(DB_URL), session)
        expense_repo = DBExpenseRepo(str(DB_URL), session)

        # Create a specific category for this test
        try:
            category = category_repo.get(name="Healthcare")
        except CategoryNotFoundError:
            category = ExpenseCategory.create(name="Healthcare")
            category_repo.add(category)
            session.refresh(category)

        # Add expenses to this category
        expenses_to_add = [
            Expense.create(
                amount=Decimal("50.00"),
                currency=Currency.USD,
                description="Doctor visit",
                category=category,
            ),
            Expense.create(
                amount=Decimal("25.50"),
                currency=Currency.USD,
                description="Pharmacy - prescription",
                category=category,
            ),
            Expense.create(
                amount=Decimal("15.00"),
                currency=Currency.USD,
                description="Vitamins",
                category=category,
            ),
        ]

        for expense in expenses_to_add:
            expense_repo.add(expense)
            session.refresh(expense)

        # Search by category
        results = expense_repo.search_by_category(category)  # type: ignore
        logger.info("✅ Found %d expenses in 'Healthcare' category:", len(results))
        total = Decimal("0.00")
        for expense in results:
            logger.info(
                "   - %s | %s %s",
                expense.description,
                expense.amount,
                expense.currency.value,
            )
            total += expense.amount

        logger.info("   Total Healthcare expenses: %s USD", total)


def test_error_handling() -> None:
    """Test error handling for non-existent expenses."""
    logger.info("\n=== Test: Error Handling ===")

    with Session(engine) as session:
        expense_repo = DBExpenseRepo(str(DB_URL), session)

        # Try to get non-existent expense
        try:
            expense_repo.get(99999)
            logger.error("❌ Should have raised ExpenseNotFoundError!")
        except ExpenseNotFoundError:
            logger.info(
                "✅ Correctly raised ExpenseNotFoundError for non-existent expense"
            )

        # Try to delete non-existent expense
        try:
            expense_repo.delete(99999)
            logger.error("❌ Should have raised ExpenseNotFoundError!")
        except ExpenseNotFoundError:
            logger.info(
                "✅ Correctly raised ExpenseNotFoundError when deleting non-existent expense"
            )

        # Try to search in date range with no results
        try:
            future_date = datetime.now(timezone.utc) + timedelta(days=365)
            far_future = future_date + timedelta(days=365)
            expense_repo.search_by_dates(future_date, far_future)
            logger.error("❌ Should have raised ExpenseNotFoundError!")
        except ExpenseNotFoundError:
            logger.info(
                "✅ Correctly raised ExpenseNotFoundError for date range with no expenses"
            )


def main() -> None:
    """Run all tests."""
    test_add_expense()
    test_get_expense()
    test_update_expense()
    test_delete_expense()
    test_list_expenses()
    test_search_by_dates()
    test_search_by_category()
    test_error_handling()


if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("Starting DBExpenseRepo Tests...")
    logger.info("=" * 70)
    main()
    logger.info("=" * 70)
    logger.info("All tests completed!")
    logger.info("=" * 70)
