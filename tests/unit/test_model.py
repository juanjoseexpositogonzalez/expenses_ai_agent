from datetime import datetime
from decimal import Decimal
from typing import Any, Final

import pytest
import sqlalchemy.exc
from sqlmodel import Session, SQLModel, create_engine

from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory

DATABASE_URL: Final[str] = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create a new engine for each test
    engine = create_engine(DATABASE_URL, echo=True)

    # Drop tables if they exist
    SQLModel.metadata.drop_all(engine, checkfirst=True)
    # Create tables, catching any index duplicate errors
    try:
        SQLModel.metadata.create_all(engine, checkfirst=True)
    except sqlalchemy.exc.OperationalError as e:
        if "already exists" in str(e) and "index" in str(e):
            # Index already exists, continue anyway
            pass
        else:
            raise

    with Session(engine) as session:
        yield session

    # Clean up after test
    SQLModel.metadata.drop_all(engine, checkfirst=True)
    engine.dispose()


def test_create_category(db_session: Any):
    category = ExpenseCategory(name="Food")

    db_session.add(category)
    db_session.commit()

    assert category.id is not None
    assert category.name == "Food"


def test_create_expense(db_session: Any):
    category = ExpenseCategory(name="Transportation")
    expense = Expense(
        amount=Decimal(100),
        currency=Currency.USD,
        description="Train tickets",
        date=datetime(2025, 8, 31, 20, 0, 0),
        category=category,
        created_at=None,
        updated_at=None,
    )

    db_session.add(category)
    db_session.add(expense)
    db_session.commit()

    assert expense.id is not None
    assert expense.category_id is not None
    assert expense.category == category
    assert expense.currency == Currency.USD
    assert expense.description == "Train tickets"
    assert expense.date == datetime(2025, 8, 31, 20, 0, 0)
    assert isinstance(expense.created_at, datetime)
    assert isinstance(expense.updated_at, datetime)
