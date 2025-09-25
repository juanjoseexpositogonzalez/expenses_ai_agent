import logging
from decimal import Decimal

from sqlmodel import Session, create_engine

from expenses_ai_agent.storage.exceptions import ExpenseCreationError
from expenses_ai_agent.storage.models import (
    Category,
    Currency,
    Expense,
    ExpenseCategory,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def first_workflow() -> None:
    """Demonstrates a simple workflow of creating and displaying an expense category and an expense."""
    # Create a new expense category
    category = ExpenseCategory.create(name=Category.FOOD)
    logger.info("Category created %s", category)
    logger.info("Adding category to the database...")
    engine = create_engine("sqlite:///expenses.db")
    with Session(engine) as session:
        session.add(category)
        session.commit()
        session.refresh(category)
    logger.info("Category added to the database.")

    # Create a new expense

    try:
        expense = Expense.create(
            amount=Decimal(25.50),
            currency=Currency.USD,
            description="Lunch at a restaurant",
            category=category,
        )
    except ExpenseCreationError as e:
        logger.error("Error creating expense: %s", e)
        return

    logger.info("Expense created: %s", expense)
    logger.info("Adding expense to the database...")
    with Session(engine) as session:
        session.add(expense)
        session.commit()
        session.refresh(expense)
    logger.info("Expense added to the database.")


if __name__ == "__main__":
    logger.info("Starting first workflow...")
    first_workflow()
    logger.info("First workflow completed.")
