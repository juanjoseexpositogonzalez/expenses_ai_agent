# SQLModel Entities

SQLModel combines the best of SQLAlchemy (ORM) and Pydantic (validation). This lesson explains how to define type-safe database models for our expense tracking system.


## Why SQLModel Exists

Traditionally, you need separate classes for database models and validation:

```python
# SQLAlchemy model (database)
class ExpenseDB(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True)
    amount = Column(Numeric)

# Pydantic model (validation)
class ExpenseSchema(BaseModel):
    id: int
    amount: Decimal
```

SQLModel unifies these:

```python
# SQLModel - one class for both
class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal
```


## Core Concepts

### Defining a Table

```python
from sqlmodel import Field, SQLModel

class ExpenseCategory(SQLModel, table=True):
    """A category for classifying expenses."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
```

Key points:

- `table=True` creates a database table
- `Field(primary_key=True)` marks the primary key
- `Field(index=True)` creates a database index for faster lookups
- Type hints become column types


### Relationships

SQLModel supports relationships between tables:

```python
from sqlmodel import Relationship

class ExpenseCategory(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)
    expenses: list["Expense"] = Relationship(back_populates="category")


class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal
    category_id: int | None = Field(default=None, foreign_key="expensecategory.id")
    category: ExpenseCategory | None = Relationship(back_populates="expenses")
```

**When to use:** Use `Relationship` when you need to navigate between related objects. The `back_populates` parameter ensures both sides of the relationship stay in sync.


### Default Values and Factory Functions

```python
from datetime import datetime, timezone

class Expense(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    amount: Decimal
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
```

Use `default_factory` for mutable defaults or computed values.


## Python Comparison

| Python dataclass | SQLModel |
|------------------|----------|
| `@dataclass` | `class X(SQLModel, table=True)` |
| `field(default=...)` | `Field(default=...)` |
| No validation | Automatic Pydantic validation |
| No ORM | Full SQLAlchemy ORM |


## Best Practices

**Use Decimal for money:**

```python
from decimal import Decimal

class Expense(SQLModel, table=True):
    # Good - precise financial calculations
    amount: Decimal = Field(default=Decimal("0.00"))

    # Bad - floating point errors
    # amount: float
```

**Add factory methods for convenience:**

```python
class Expense(SQLModel, table=True):
    # ... fields ...

    @classmethod
    def create(cls, amount: Decimal, currency: Currency, **kwargs) -> "Expense":
        """Factory method for creating expenses."""
        return cls(amount=amount, currency=currency, **kwargs)
```

**Implement `__str__` for debugging:**

```python
class Expense(SQLModel, table=True):
    def __str__(self) -> str:
        return f"{self.amount} {self.currency}"
```


## SQLModel in Our Project

We define three entities:

| Entity | Fields | Purpose |
|--------|--------|---------|
| `ExpenseCategory` | id, name | Store category names (Food, Transport, etc.) |
| `Expense` | id, amount, currency, description, date, category | Store expense records |
| `UserPreference` | id, telegram_user_id, preferred_currency | Store user settings |


## Further Reading

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/) - Official docs
- [Pydantic Documentation](https://docs.pydantic.dev/) - Validation details
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/orm/) - Underlying ORM concepts
