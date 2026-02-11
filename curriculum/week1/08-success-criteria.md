# Week 1 Success Criteria

Use this checklist to verify you've completed all Week 1 requirements.


## Validation Commands

All of these commands must succeed:

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week1.py -v` | All 26 tests pass |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |


## Technical Checklist

### Models (`storage/models.py`)

- [ ] `Currency` StrEnum with 10 currency codes (EUR, USD, GBP, JPY, CHF, CAD, AUD, CNY, INR, MXN)
- [ ] `ExpenseCategory` SQLModel with id, name, `__str__`, `create()` classmethod
- [ ] `Expense` SQLModel with id, amount (Decimal), currency, description, date, category relationship
- [ ] `Expense` has `telegram_user_id` optional field for multiuser support

### Exceptions (`storage/exceptions.py`)

- [ ] `CategoryNotFoundError` with meaningful error message
- [ ] `ExpenseNotFoundError` with meaningful error message

### Repositories (`storage/repo.py`)

- [ ] `CategoryRepository` abstract base class with `add`, `get`, `list`, `update`, `delete`
- [ ] `ExpenseRepository` abstract base class with `add`, `get`, `list`, `delete`, `search_by_category`
- [ ] `InMemoryCategoryRepository` implementing CategoryRepository
- [ ] `InMemoryExpenseRepository` implementing ExpenseRepository with auto-increment IDs


## Conceptual Understanding

You should be able to answer these questions:

1. **Why use the Repository pattern?**
   - Abstracts data access for testability
   - Allows swapping storage backends (in-memory for tests, database for production)
   - Keeps business logic separate from database concerns

2. **Why use StrEnum instead of regular strings?**
   - Type safety catches typos at edit time
   - IDE autocomplete discovers valid values
   - Works directly as strings in JSON and databases

3. **Why use Decimal for money instead of float?**
   - Floats have precision errors (0.1 + 0.2 != 0.3)
   - Financial calculations require exact precision
   - Decimal("10.50") is exact

4. **What's the difference between ABC and Protocol?**
   - ABC requires explicit inheritance (nominal typing)
   - Protocol checks structure only (structural typing)
   - We'll use Protocol in Week 2 for the LLM layer


## You Are Done When

- All 26 tests pass (green)
- No ruff warnings
- You have NOT looked at the author's implementation
- You can explain what a Repository pattern is and why we use it


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "ModuleNotFoundError: expenses_ai_agent" | Run `uv pip install -e ".[dev]"` |
| "Table already exists" SQLModel error | Use `sqlite:///:memory:` for tests or delete `expenses.db` |
| Relationship not loading | Add `Relationship(back_populates="...")` on both sides |
| Decimal precision issues | Use `Decimal("10.50")` not `Decimal(10.50)` |
