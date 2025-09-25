import logging
from datetime import datetime, timezone
from decimal import Decimal
from enum import UNIQUE, StrEnum, verify
from typing import List, Self

from decouple import config
from sqlmodel import Field, Relationship, SQLModel, create_engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@verify(UNIQUE)
class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"
    GBP = "GBP"
    JPY = "JPY"
    AUD = "AUD"
    CAD = "CAD"
    CHF = "CHF"
    CNY = "CNY"
    SEK = "SEK"
    NZD = "NZD"


class ExpenseCategory(SQLModel, table=True):
    """Model represnting an expense category."""

    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)

    expenses: List["Expense"] = Relationship(back_populates="category")

    def __str__(self) -> str:
        return f"Category: {self.name}"

    @classmethod
    def create(cls, name: str) -> Self:
        """Create a new ExpenseCategory instance.

        Args:
            name (str): name for the category.

        Returns:
            ExpenseCategory: A new instance of ExpenseCategory.
        """
        return cls(name=name)


class Expense(SQLModel, table=True):
    """Model representing an expense entry."""

    __table_args__ = {"extend_existing": True}

    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal
    currency: Currency = Field(default=Currency.EUR)
    description: str | None = None
    date: datetime = Field(default=datetime.now(timezone.utc))
    created_at: datetime = Field(default=datetime.now(timezone.utc))
    updated_at: datetime = Field(default=datetime.now(timezone.utc))

    category_id: int | None = Field(default=None, foreign_key="expensecategory.id")
    category: ExpenseCategory | None = Relationship(back_populates="expenses")

    def __str__(self) -> str:
        """String representation of the Expense instance."""
        return f"Expense: {self.amount} {self.currency} - {self.description or 'No description'} on {self.date} in category {self.category.name if self.category else 'No category'}"

    @classmethod
    def create(
        cls,
        amount: Decimal,
        currency: Currency = Currency.EUR,
        description: str | None = None,
        date: datetime | None = None,
        category: ExpenseCategory | None = None,
    ) -> Self:
        """Create a new Expense instance.

        Args:
            amount (Decimal): The amount of the expense.
            currency (Currency, optional): The currency of the expense. Defaults to Currency.EUR.
            description (str | None, optional): A description of the expense. Defaults to None.
            date (datetime | None, optional): The date of the expense. Defaults to current UTC time.
            category (ExpenseCategory | None, optional): The category of the expense. Defaults to None.

        Returns:
            Expense: A new instance of Expense.
        """
        return cls(
            amount=amount,
            currency=currency,
            description=description,
            date=date or datetime.now(timezone.utc),
            category=category,
        )


def create_db_and_tables():
    """Create the database and tables if they do not exist."""
    database_url = config("DATABASE_URL", default="sqlite:///./expenses.db", cast=str)
    engine = create_engine(database_url, echo=True)  # type: ignore
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_db_and_tables()
    logger.info("Database and tables created successfully.")
