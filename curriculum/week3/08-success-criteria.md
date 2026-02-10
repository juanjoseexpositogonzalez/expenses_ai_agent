# Week 3 Success Criteria

Use this checklist to verify you've completed all Week 3 requirements.


## Validation Commands

All of these commands must succeed:

| Command | Expected Result |
|---------|-----------------|
| `pytest tests/unit/test_week3.py -v` | All 30 tests pass |
| `ruff format --check .` | No formatting issues |
| `ruff check .` | No linting errors |
| `expenses-ai-agent classify "Coffee $5" --help` | Shows help text |


## Technical Checklist

### Prompts (`prompts/`)

- [ ] `CLASSIFICATION_PROMPT` in `system.py` with all 12 categories
- [ ] Categories include: Food, Transport, Entertainment, Shopping, Health, Bills, Education, Travel, Services, Gifts, Investments, Other
- [ ] Prompt mentions JSON output format
- [ ] `USER_PROMPT` in `user.py` with `{expense_description}` placeholder

### Classification Service (`services/classification.py`)

- [ ] `ClassificationResult` dataclass with `response` and `persisted` fields
- [ ] `ClassificationService` class with `assistant` and optional repos
- [ ] `classify()` method that calls assistant and optionally persists
- [ ] `persist_with_category()` for HITL overrides
- [ ] Service builds correct messages (system + user)

### Database Repositories (`storage/repo.py`)

- [ ] `DBCategoryRepo` with injected session support
- [ ] `DBCategoryRepo.add()`, `get()`, `list()`, `delete()`
- [ ] `DBExpenseRepo` with injected session support
- [ ] `DBExpenseRepo.add()`, `get()`, `list()`, `delete()`
- [ ] `DBExpenseRepo.search_by_category()`
- [ ] `DBExpenseRepo.search_by_dates()`
- [ ] `DBExpenseRepo.list_by_user()`

### CLI (`cli/cli.py`)

- [ ] Typer app with `classify` command
- [ ] `--db` option for persistence
- [ ] Rich table output
- [ ] Error handling


## Conceptual Understanding

You should be able to answer:

1. **Why use a Service layer?**
   - Centralizes business logic
   - Reusable by CLI, bot, API
   - Easy to test with mocks

2. **Why design prompts carefully?**
   - Consistent, structured outputs
   - Clear categories reduce confusion
   - JSON format enables parsing

3. **Why support session injection?**
   - Testing with in-memory databases
   - Transactions across multiple repos
   - Flexibility for different contexts

4. **Why use Typer over argparse?**
   - Type hints define arguments
   - Auto-generated help
   - Rich integration for formatting


## You Are Done When

- All 30 tests pass (green)
- No ruff warnings
- `expenses-ai-agent classify "Test expense"` shows results
- You can explain the Service layer pattern


## Common Issues and Solutions

| Issue | Solution |
|-------|----------|
| "No module named expenses_ai_agent" | Run `uv pip install -e ".[dev]"` |
| Session already closed | Check `_owns_session` logic |
| "Table has no column named X" | Call `SQLModel.metadata.create_all(engine)` |
| Rich not formatting | Use `Console()` not `print()` |
| Typer command not found | Check `[project.scripts]` in pyproject.toml |
