# Python Enums with StrEnum

Enumerations provide type-safe constants. This lesson covers Python's `StrEnum` and why it's ideal for currencies and categories.


## Why Enums Exist

Without enums, you might use strings:

```python
# Fragile - typos go unnoticed
currency = "UDS"  # Oops, meant "USD"
if currency == "USD":
    # Never runs due to typo
    pass
```

With enums, the type system catches errors:

```python
from enum import StrEnum

class Currency(StrEnum):
    USD = "USD"
    EUR = "EUR"

# IDE catches this immediately
currency = Currency.UDS  # AttributeError: UDS not found
```


## StrEnum vs Regular Enum

Python offers several enum types:

```python
from enum import Enum, StrEnum

# Regular Enum - values need explicit conversion
class ColorEnum(Enum):
    RED = "red"

str(ColorEnum.RED)  # "ColorEnum.RED" - not the value!
ColorEnum.RED.value  # "red" - need .value


# StrEnum - values work as strings directly
class ColorStrEnum(StrEnum):
    RED = "red"

str(ColorStrEnum.RED)  # "red" - works directly!
ColorStrEnum.RED == "red"  # True
```

**When to use StrEnum:** When enum values need to work as strings (in JSON, databases, APIs).


## Defining a Currency Enum

```python
from enum import StrEnum, verify, UNIQUE

@verify(UNIQUE)
class Currency(StrEnum):
    """Supported currencies for expense tracking."""

    EUR = "EUR"
    USD = "USD"
    GBP = "GBP"
    JPY = "JPY"
    CHF = "CHF"
    CAD = "CAD"
    AUD = "AUD"
    CNY = "CNY"
    INR = "INR"
    MXN = "MXN"
```

Key features:

- `@verify(UNIQUE)` ensures no duplicate values
- Values match ISO 4217 currency codes
- Works directly as strings in JSON and SQL


## Enum Features

**Iteration:**

```python
for currency in Currency:
    print(f"{currency.name}: {currency.value}")
# EUR: EUR
# USD: USD
# ...
```

**Membership testing:**

```python
"EUR" in [c.value for c in Currency]  # True
Currency.EUR in Currency  # True
```

**Access by name or value:**

```python
Currency["EUR"]  # Currency.EUR (by name)
Currency("EUR")  # Currency.EUR (by value)
```


## Python Comparison

| Regular strings | StrEnum |
|-----------------|---------|
| No type safety | Type-safe constants |
| Typos cause runtime bugs | Errors caught at edit time |
| No IDE autocomplete | Full autocomplete support |
| Hard to discover valid values | All values visible in definition |


## Enums in Our Project

We use `StrEnum` for currencies because:

1. Currency codes are stored in the database as strings
2. They're serialized to JSON in API responses
3. They're compared in classification logic

```python
from expenses_ai_agent.storage.models import Currency, Expense

expense = Expense(
    amount=Decimal("42.50"),
    currency=Currency.EUR,  # Type-safe
)

# Works in JSON
expense.model_dump_json()  # {"currency": "EUR", ...}

# Works in comparisons
if expense.currency == Currency.EUR:
    print("Euro expense")
```


## Further Reading

- [Python Enum Documentation](https://docs.python.org/3/library/enum.html)
- [PEP 435 - Adding an Enum type](https://peps.python.org/pep-0435/)
- [PEP 663 - StrEnum](https://peps.python.org/pep-0663/)
