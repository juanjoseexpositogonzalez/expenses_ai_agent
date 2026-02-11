# Week 3 Implementation: Classification Pipeline

This implementation exercise teaches you to build the complete classification pipeline with prompts, service layer, database repositories, and CLI.


## Learning Goals

By the end of this implementation, you will:

- Design system and user prompts for LLM classification
- Implement ClassificationService with dependency injection
- Build database-backed repositories with session management
- Create a CLI with Typer and Rich formatting


## What You're Building

**Input:** CLI command with expense description

**Output:** Classified expense with optional database persistence

```bash
expenses-ai-agent classify "Coffee at Starbucks for $5.50"
expenses-ai-agent classify "Taxi to airport 45 EUR" --db
```


## Test Suite

Copy these tests to your `tests/unit/test_week3.py` file:

```python
"""
Week 3 - Definition of Done: Classification Pipeline

Run: pytest tests/unit/test_week3.py -v
All tests must pass to complete Week 3.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from sqlmodel import Session, SQLModel, create_engine
from typer.testing import CliRunner


# ============================================================================
# PROMPTS TESTS
# ============================================================================

class TestClassificationPrompt:
    """Tests for the system prompt."""

    def test_classification_prompt_exists(self):
        """CLASSIFICATION_PROMPT should be defined as a string constant."""
        from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT

        assert isinstance(CLASSIFICATION_PROMPT, str)
        assert len(CLASSIFICATION_PROMPT) > 100

    def test_classification_prompt_contains_categories(self):
        """System prompt should mention all 12 expense categories."""
        from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT

        required_categories = [
            "Food", "Transport", "Entertainment", "Shopping", "Health",
            "Bills", "Education", "Travel", "Services", "Gifts",
            "Investments", "Other",
        ]

        prompt_lower = CLASSIFICATION_PROMPT.lower()
        for category in required_categories:
            assert category.lower() in prompt_lower, f"Category '{category}' not found"

    def test_classification_prompt_mentions_json_output(self):
        """System prompt should mention JSON output format."""
        from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT

        assert "json" in CLASSIFICATION_PROMPT.lower()


class TestUserPrompt:
    """Tests for the user prompt template."""

    def test_user_prompt_exists(self):
        """USER_PROMPT should be defined."""
        from expenses_ai_agent.prompts.user import USER_PROMPT

        assert isinstance(USER_PROMPT, str)

    def test_user_prompt_has_placeholder(self):
        """USER_PROMPT should have a placeholder."""
        from expenses_ai_agent.prompts.user import USER_PROMPT

        assert "{" in USER_PROMPT and "}" in USER_PROMPT

    def test_user_prompt_can_be_formatted(self):
        """USER_PROMPT should be formattable."""
        from expenses_ai_agent.prompts.user import USER_PROMPT

        try:
            formatted = USER_PROMPT.format(expense_description="Coffee $5.50")
            assert "Coffee" in formatted or "5.50" in formatted
        except KeyError as e:
            assert "expense" in str(e).lower()


# ============================================================================
# SERVICE TESTS
# ============================================================================

class TestClassificationResult:
    """Tests for ClassificationResult dataclass."""

    def test_classification_result_has_response(self):
        """ClassificationResult should contain the LLM response."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.services.classification import ClassificationResult
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("10.00"),
            currency=Currency.EUR,
            confidence=0.9,
            cost=Decimal("0.001"),
        )

        result = ClassificationResult(response=response, persisted=False)

        assert result.response == response
        assert result.persisted is False

    def test_classification_result_tracks_persistence(self):
        """ClassificationResult should track persistence status."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.services.classification import ClassificationResult
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Transport",
            total_amount=Decimal("25.00"),
            currency=Currency.USD,
            confidence=0.85,
            cost=Decimal("0.002"),
        )

        result_persisted = ClassificationResult(response=response, persisted=True)
        result_not = ClassificationResult(response=response, persisted=False)

        assert result_persisted.persisted is True
        assert result_not.persisted is False


class TestClassificationService:
    """Tests for ClassificationService."""

    @pytest.fixture
    def mock_assistant(self):
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        assistant = MagicMock()
        assistant.completion.return_value = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("5.50"),
            currency=Currency.USD,
            confidence=0.95,
            cost=Decimal("0.001"),
        )
        return assistant

    @pytest.fixture
    def mock_category_repo(self):
        from expenses_ai_agent.storage.models import ExpenseCategory

        repo = MagicMock()
        repo.get.return_value = ExpenseCategory(id=1, name="Food")
        return repo

    @pytest.fixture
    def mock_expense_repo(self):
        return MagicMock()

    def test_service_initialization(self, mock_assistant):
        from expenses_ai_agent.services.classification import ClassificationService

        service = ClassificationService(assistant=mock_assistant)
        assert service.assistant == mock_assistant

    def test_classify_calls_assistant(self, mock_assistant):
        from expenses_ai_agent.services.classification import ClassificationService

        service = ClassificationService(assistant=mock_assistant)
        result = service.classify("Coffee at Starbucks $5.50")

        mock_assistant.completion.assert_called_once()
        assert result.response.category == "Food"

    def test_classify_without_persistence(self, mock_assistant):
        from expenses_ai_agent.services.classification import ClassificationService

        service = ClassificationService(assistant=mock_assistant)
        result = service.classify("Test expense", persist=False)

        assert result.persisted is False

    def test_classify_with_persistence(self, mock_assistant, mock_category_repo, mock_expense_repo):
        from expenses_ai_agent.services.classification import ClassificationService

        service = ClassificationService(
            assistant=mock_assistant,
            category_repo=mock_category_repo,
            expense_repo=mock_expense_repo,
        )

        result = service.classify("Coffee $5.50", persist=True)

        assert result.persisted is True
        mock_expense_repo.add.assert_called_once()

    def test_persist_with_category_override(self, mock_assistant, mock_category_repo, mock_expense_repo):
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.services.classification import ClassificationService
        from expenses_ai_agent.storage.models import Currency

        service = ClassificationService(
            assistant=mock_assistant,
            category_repo=mock_category_repo,
            expense_repo=mock_expense_repo,
        )

        response = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("10.00"),
            currency=Currency.EUR,
            confidence=0.6,
            cost=Decimal("0.001"),
        )

        service.persist_with_category(
            expense_description="Movie snacks",
            category_name="Entertainment",
            response=response,
        )

        mock_expense_repo.add.assert_called_once()

    def test_service_builds_correct_messages(self, mock_assistant):
        from expenses_ai_agent.services.classification import ClassificationService

        service = ClassificationService(assistant=mock_assistant)
        service.classify("Test expense")

        call_args = mock_assistant.completion.call_args
        messages = call_args[0][0]

        assert len(messages) >= 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"


# ============================================================================
# DATABASE REPOSITORY TESTS
# ============================================================================

@pytest.fixture
def db_engine():
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture
def db_session(db_engine):
    with Session(db_engine) as session:
        yield session


class TestDBCategoryRepo:
    """Tests for DBCategoryRepo."""

    def test_db_category_repo_with_injected_session(self, db_session):
        from expenses_ai_agent.storage.models import ExpenseCategory
        from expenses_ai_agent.storage.repo import DBCategoryRepo

        repo = DBCategoryRepo(db_url="sqlite:///:memory:", session=db_session)

        category = ExpenseCategory.create(name="Food")
        repo.add(category)

        result = repo.get("Food")
        assert result is not None
        assert result.name == "Food"

    def test_db_category_repo_list(self, db_session):
        from expenses_ai_agent.storage.models import ExpenseCategory
        from expenses_ai_agent.storage.repo import DBCategoryRepo

        repo = DBCategoryRepo(db_url="sqlite:///:memory:", session=db_session)

        repo.add(ExpenseCategory.create(name="Food"))
        repo.add(ExpenseCategory.create(name="Transport"))

        names = repo.list()

        assert len(names) == 2
        assert "Food" in names

    def test_db_category_repo_delete(self, db_session):
        from expenses_ai_agent.storage.models import ExpenseCategory
        from expenses_ai_agent.storage.repo import DBCategoryRepo

        repo = DBCategoryRepo(db_url="sqlite:///:memory:", session=db_session)

        repo.add(ExpenseCategory.create(name="ToDelete"))
        repo.delete("ToDelete")

        assert repo.get("ToDelete") is None

    def test_db_category_repo_delete_nonexistent_raises(self, db_session):
        from expenses_ai_agent.storage.exceptions import CategoryNotFoundError
        from expenses_ai_agent.storage.repo import DBCategoryRepo

        repo = DBCategoryRepo(db_url="sqlite:///:memory:", session=db_session)

        with pytest.raises(CategoryNotFoundError):
            repo.delete("NonExistent")


class TestDBExpenseRepo:
    """Tests for DBExpenseRepo."""

    @pytest.fixture
    def category_in_db(self, db_session):
        from expenses_ai_agent.storage.models import ExpenseCategory

        category = ExpenseCategory.create(name="Food")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    def test_db_expense_repo_add_and_get(self, db_session, category_in_db):
        from expenses_ai_agent.storage.models import Currency, Expense
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        expense = Expense(
            amount=Decimal("42.50"),
            currency=Currency.EUR,
            description="Lunch",
            category=category_in_db,
        )
        repo.add(expense)

        result = repo.get(expense.id)
        assert result is not None
        assert result.amount == Decimal("42.50")

    def test_db_expense_repo_list(self, db_session):
        from expenses_ai_agent.storage.models import Currency, Expense
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        repo.add(Expense(amount=Decimal("10.00"), currency=Currency.EUR))
        repo.add(Expense(amount=Decimal("20.00"), currency=Currency.USD))

        expenses = repo.list()
        assert len(expenses) == 2

    def test_db_expense_repo_delete(self, db_session):
        from expenses_ai_agent.storage.models import Currency, Expense
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        expense = Expense(amount=Decimal("15.00"), currency=Currency.EUR)
        repo.add(expense)
        expense_id = expense.id

        repo.delete(expense_id)
        assert repo.get(expense_id) is None

    def test_db_expense_repo_delete_nonexistent_raises(self, db_session):
        from expenses_ai_agent.storage.exceptions import ExpenseNotFoundError
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        with pytest.raises(ExpenseNotFoundError):
            repo.delete(99999)

    def test_db_expense_repo_search_by_category(self, db_session, category_in_db):
        from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        transport = ExpenseCategory.create(name="Transport")
        db_session.add(transport)
        db_session.commit()
        db_session.refresh(transport)

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        repo.add(Expense(amount=Decimal("10"), currency=Currency.EUR, category=category_in_db))
        repo.add(Expense(amount=Decimal("20"), currency=Currency.EUR, category=category_in_db))
        repo.add(Expense(amount=Decimal("30"), currency=Currency.EUR, category=transport))

        food_expenses = repo.search_by_category(category_in_db)
        assert len(food_expenses) == 2

    def test_db_expense_repo_search_by_dates(self, db_session):
        from expenses_ai_agent.storage.models import Currency, Expense
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        now = datetime.now(timezone.utc)
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)

        repo.add(Expense(amount=Decimal("10"), currency=Currency.EUR, date=now))
        repo.add(Expense(amount=Decimal("20"), currency=Currency.EUR, date=yesterday))
        repo.add(Expense(amount=Decimal("30"), currency=Currency.EUR, date=last_week))

        start = now - timedelta(days=3)
        results = repo.search_by_dates(start, now)

        assert len(results) == 2

    def test_db_expense_repo_list_by_user(self, db_session):
        from expenses_ai_agent.storage.models import Currency, Expense
        from expenses_ai_agent.storage.repo import DBExpenseRepo

        repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

        repo.add(Expense(amount=Decimal("10"), currency=Currency.EUR, telegram_user_id=100))
        repo.add(Expense(amount=Decimal("20"), currency=Currency.EUR, telegram_user_id=100))
        repo.add(Expense(amount=Decimal("30"), currency=Currency.EUR, telegram_user_id=200))

        user_100_expenses = repo.list_by_user(telegram_user_id=100)
        assert len(user_100_expenses) == 2


# ============================================================================
# CLI TESTS
# ============================================================================

@pytest.fixture
def cli_runner():
    return CliRunner()


@pytest.fixture
def mock_classification_response():
    from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
    from expenses_ai_agent.storage.models import Currency

    return ExpenseCategorizationResponse(
        category="Food",
        total_amount=Decimal("5.50"),
        currency=Currency.USD,
        confidence=0.95,
        cost=Decimal("0.001"),
        comments="Coffee purchase",
    )


class TestCLIApp:
    """Tests for CLI application."""

    def test_cli_app_exists(self):
        from expenses_ai_agent.cli.cli import app

        assert app is not None

    def test_classify_command_exists(self, cli_runner):
        from expenses_ai_agent.cli.cli import app

        result = cli_runner.invoke(app, ["classify", "--help"])
        assert result.exit_code == 0

    def test_classify_requires_description(self, cli_runner):
        from expenses_ai_agent.cli.cli import app

        result = cli_runner.invoke(app, ["classify"])
        assert result.exit_code != 0 or "missing" in result.output.lower()

    def test_classify_with_mocked_service(self, cli_runner, mock_classification_response):
        from expenses_ai_agent.cli.cli import app

        with patch("expenses_ai_agent.cli.cli.ClassificationService") as mock_service_cls:
            mock_service = MagicMock()
            mock_result = MagicMock()
            mock_result.response = mock_classification_response
            mock_result.persisted = False
            mock_service.classify.return_value = mock_result
            mock_service_cls.return_value = mock_service

            with patch("expenses_ai_agent.cli.cli.OpenAIAssistant"):
                result = cli_runner.invoke(app, ["classify", "Coffee at Starbucks $5.50"])
                assert result.exit_code == 0 or "Food" in result.output

    def test_classify_db_option_exists(self, cli_runner):
        from expenses_ai_agent.cli.cli import app

        result = cli_runner.invoke(app, ["classify", "--help"])
        assert "--db" in result.output or "database" in result.output.lower()

    def test_cli_outputs_category_info(self, cli_runner, mock_classification_response):
        from expenses_ai_agent.cli.cli import app

        with patch("expenses_ai_agent.cli.cli.ClassificationService") as mock_service_cls:
            mock_service = MagicMock()
            mock_result = MagicMock()
            mock_result.response = mock_classification_response
            mock_result.persisted = False
            mock_service.classify.return_value = mock_result
            mock_service_cls.return_value = mock_service

            with patch("expenses_ai_agent.cli.cli.OpenAIAssistant"):
                result = cli_runner.invoke(app, ["classify", "Test expense"])
                output = result.output
                assert "Food" in output or "5.50" in output or "Category" in output
```


## Implementation Strategy

### Step 1: Create Prompts

Build `prompts/system.py` and `prompts/user.py`:

**Target tests:** `TestClassificationPrompt`, `TestUserPrompt` (6 tests)

### Step 2: Implement ClassificationService

Build `services/classification.py` with `ClassificationResult` and `ClassificationService`:

**Target tests:** `TestClassificationResult`, `TestClassificationService` (8 tests)

### Step 3: Implement Database Repositories

Add `DBCategoryRepo` and `DBExpenseRepo` to `storage/repo.py`:

**Target tests:** `TestDBCategoryRepo`, `TestDBExpenseRepo` (12 tests)

### Step 4: Create CLI

Build `cli/cli.py` with Typer and Rich:

**Target tests:** `TestCLIApp` (6 tests)


## Validation Checklist

Before moving on, verify:

- [ ] All 30 tests pass: `pytest tests/unit/test_week3.py -v`
- [ ] No linting errors: `ruff check src/`
- [ ] Code is formatted: `ruff format .`
- [ ] CLI works: `expenses-ai-agent classify "Test"`


## Step Hints


### Step 1: Prompts Hint

Your system prompt needs:
- All 12 categories with examples
- Instructions to output JSON
- Extraction requirements (category, amount, currency, confidence)


### Step 2: Service Hint

Use dataclasses for simple data structures:

```python
from dataclasses import dataclass

@dataclass
class ClassificationResult:
    response: ExpenseCategorizationResponse
    persisted: bool
```


### Step 3: DB Repos Hint

Remember session ownership:

```python
if session:
    self._session = session
    self._owns_session = False
else:
    # Create own session
    self._owns_session = True
```


### Step 4: CLI Hint

Register the entry point in `pyproject.toml`:

```toml
[project.scripts]
expenses-ai-agent = "expenses_ai_agent.cli.cli:app"
```

---

Your Week 3 classification pipeline is complete when all 30 tests pass.
