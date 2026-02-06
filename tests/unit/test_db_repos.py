"""Comprehensive tests for repository implementations."""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Final

import pytest
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine

from expenses_ai_agent.storage.exceptions import (
    CategoryCreationError,
    CategoryNotFoundError,
    ExpenseNotFoundError,
)
from expenses_ai_agent.storage.models import Currency, Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import (
    DBCategoryRepo,
    DBExpenseRepo,
    InMemoryCategoryRepository,
    InMemoryExpenseRepository,
)

DATABASE_URL: Final[str] = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    engine = create_engine(DATABASE_URL, echo=False)
    SQLModel.metadata.drop_all(engine, checkfirst=True)
    try:
        SQLModel.metadata.create_all(engine, checkfirst=True)
    except OperationalError as e:
        if "already exists" in str(e) and "index" in str(e):
            pass
        else:
            raise
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine, checkfirst=True)
    engine.dispose()


class TestInMemoryCategoryRepository:
    """Tests for InMemoryCategoryRepository."""

    def test_add_category(self) -> None:
        """Test adding a category."""
        repo = InMemoryCategoryRepository()
        category = ExpenseCategory(name="Food")
        repo.add(category)
        assert len(repo.list()) == 1
        assert "Food" in repo.list()

    def test_add_duplicate_category_raises_error(self) -> None:
        """Test that adding duplicate category raises error."""
        repo = InMemoryCategoryRepository()
        category = ExpenseCategory(name="Food")
        repo.add(category)
        with pytest.raises(CategoryCreationError, match="Category already exists"):
            repo.add(ExpenseCategory(name="Food"))

    def test_get_category(self) -> None:
        """Test retrieving a category."""
        repo = InMemoryCategoryRepository()
        category = ExpenseCategory(name="Transport")
        repo.add(category)
        retrieved = repo.get("Transport")
        assert retrieved is not None
        assert retrieved.name == "Transport"

    def test_get_nonexistent_category_raises_error(self) -> None:
        """Test that getting nonexistent category raises error."""
        repo = InMemoryCategoryRepository()
        with pytest.raises(CategoryNotFoundError):
            repo.get("NonExistent")

    def test_update_category(self) -> None:
        """Test updating a category."""
        repo = InMemoryCategoryRepository()
        category = ExpenseCategory(name="Food")
        repo.add(category)
        updated = ExpenseCategory(name="Food")
        repo.update(updated)
        assert repo.get("Food") is not None

    def test_update_nonexistent_category_raises_error(self) -> None:
        """Test that updating nonexistent category raises error."""
        repo = InMemoryCategoryRepository()
        with pytest.raises(CategoryNotFoundError):
            repo.update(ExpenseCategory(name="NonExistent"))

    def test_delete_category(self) -> None:
        """Test deleting a category."""
        repo = InMemoryCategoryRepository()
        repo.add(ExpenseCategory(name="ToDelete"))
        repo.delete("ToDelete")
        assert len(repo.list()) == 0

    def test_delete_nonexistent_category_raises_error(self) -> None:
        """Test that deleting nonexistent category raises error."""
        repo = InMemoryCategoryRepository()
        with pytest.raises(CategoryNotFoundError):
            repo.delete("NonExistent")

    def test_list_categories(self) -> None:
        """Test listing all categories."""
        repo = InMemoryCategoryRepository()
        repo.add(ExpenseCategory(name="Food"))
        repo.add(ExpenseCategory(name="Transport"))
        repo.add(ExpenseCategory(name="Entertainment"))
        categories = repo.list()
        assert len(categories) == 3
        assert set(categories) == {"Food", "Transport", "Entertainment"}


class TestInMemoryExpenseRepository:
    """Tests for InMemoryExpenseRepository."""

    @pytest.fixture
    def category(self) -> ExpenseCategory:
        """Create a test category."""
        return ExpenseCategory(id=1, name="Food")

    @pytest.fixture
    def expense(self, category: ExpenseCategory) -> Expense:
        """Create a test expense."""
        return Expense(
            amount=Decimal("25.50"),
            currency=Currency.EUR,
            description="Lunch",
            date=datetime.now(),
            category=category,
        )

    def test_add_expense(self, expense: Expense) -> None:
        """Test adding an expense."""
        repo = InMemoryExpenseRepository()
        repo.add(expense)
        assert len(repo.list()) == 1
        assert expense.id == 1

    def test_add_multiple_expenses_assigns_ids(self, category: ExpenseCategory) -> None:
        """Test that multiple expenses get unique IDs."""
        repo = InMemoryExpenseRepository()
        expense1 = Expense(
            amount=Decimal("10"),
            currency=Currency.EUR,
            description="Test 1",
            date=datetime.now(),
            category=category,
        )
        expense2 = Expense(
            amount=Decimal("20"),
            currency=Currency.EUR,
            description="Test 2",
            date=datetime.now(),
            category=category,
        )
        repo.add(expense1)
        repo.add(expense2)
        assert expense1.id == 1
        assert expense2.id == 2

    def test_get_expense(self, expense: Expense) -> None:
        """Test retrieving an expense by ID."""
        repo = InMemoryExpenseRepository()
        repo.add(expense)
        retrieved = repo.get(1)
        assert retrieved is not None
        assert retrieved.description == "Lunch"

    def test_get_nonexistent_expense_raises_error(self) -> None:
        """Test that getting nonexistent expense raises error."""
        repo = InMemoryExpenseRepository()
        with pytest.raises(ExpenseNotFoundError, match="Expense not found"):
            repo.get(999)

    def test_search_by_dates(self, category: ExpenseCategory) -> None:
        """Test searching expenses by date range."""
        repo = InMemoryExpenseRepository()
        now = datetime.now()
        expense1 = Expense(
            amount=Decimal("10"),
            currency=Currency.EUR,
            description="Yesterday",
            date=now - timedelta(days=1),
            category=category,
        )
        expense2 = Expense(
            amount=Decimal("20"),
            currency=Currency.EUR,
            description="Today",
            date=now,
            category=category,
        )
        expense3 = Expense(
            amount=Decimal("30"),
            currency=Currency.EUR,
            description="Last week",
            date=now - timedelta(days=7),
            category=category,
        )
        repo.add(expense1)
        repo.add(expense2)
        repo.add(expense3)

        results = repo.search_by_dates(now - timedelta(days=2), now)
        assert len(results) == 2

    def test_search_by_dates_no_results_raises_error(self) -> None:
        """Test that no results raises error."""
        repo = InMemoryExpenseRepository()
        with pytest.raises(ExpenseNotFoundError, match="No expenses found"):
            repo.search_by_dates(datetime.now(), datetime.now() + timedelta(days=1))

    def test_search_by_category(self, category: ExpenseCategory) -> None:
        """Test searching expenses by category."""
        repo = InMemoryExpenseRepository()
        other_category = ExpenseCategory(id=2, name="Transport")
        expense1 = Expense(
            amount=Decimal("10"),
            currency=Currency.EUR,
            description="Food expense",
            date=datetime.now(),
            category=category,
        )
        expense2 = Expense(
            amount=Decimal("20"),
            currency=Currency.EUR,
            description="Transport expense",
            date=datetime.now(),
            category=other_category,
        )
        repo.add(expense1)
        repo.add(expense2)

        results = repo.search_by_category(category)
        assert len(results) == 1
        assert results[0].description == "Food expense"

    def test_search_by_category_no_results_raises_error(
        self, category: ExpenseCategory
    ) -> None:
        """Test that no results for category raises error."""
        repo = InMemoryExpenseRepository()
        with pytest.raises(ExpenseNotFoundError, match="No expenses found"):
            repo.search_by_category(category)

    def test_update_expense(self, expense: Expense) -> None:
        """Test updating an expense."""
        repo = InMemoryExpenseRepository()
        repo.add(expense)
        expense.amount = Decimal("100.00")
        repo.update(expense)
        updated = repo.get(expense.id)
        assert updated is not None
        assert updated.amount == Decimal("100.00")

    def test_update_nonexistent_expense_raises_error(self, expense: Expense) -> None:
        """Test that updating nonexistent expense raises error."""
        repo = InMemoryExpenseRepository()
        expense.id = 999
        with pytest.raises(ExpenseNotFoundError, match="Expense not found"):
            repo.update(expense)

    def test_delete_expense(self, expense: Expense) -> None:
        """Test deleting an expense."""
        repo = InMemoryExpenseRepository()
        repo.add(expense)
        repo.delete(expense.id)
        assert len(repo.list()) == 0

    def test_delete_nonexistent_expense_raises_error(self) -> None:
        """Test that deleting nonexistent expense raises error."""
        repo = InMemoryExpenseRepository()
        with pytest.raises(ExpenseNotFoundError, match="Expense not found"):
            repo.delete(999)

    def test_list_expenses(self, category: ExpenseCategory) -> None:
        """Test listing all expenses."""
        repo = InMemoryExpenseRepository()
        for i in range(3):
            expense = Expense(
                amount=Decimal(str(i * 10)),
                currency=Currency.EUR,
                description=f"Expense {i}",
                date=datetime.now(),
                category=category,
            )
            repo.add(expense)
        assert len(repo.list()) == 3


class TestDBExpenseRepo:
    """Tests for DBExpenseRepo with injected session."""

    @pytest.fixture
    def category(self, db_session: Session) -> ExpenseCategory:
        """Create and persist a test category."""
        category = ExpenseCategory(name="Food")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        return category

    @pytest.fixture
    def expense(self, category: ExpenseCategory) -> Expense:
        """Create a test expense (not persisted)."""
        return Expense(
            amount=Decimal("25.50"),
            currency=Currency.EUR,
            description="Lunch",
            date=datetime.now(),
            category_id=category.id,
        )

    def test_add_expense(self, db_session: Session, expense: Expense) -> None:
        """Test adding an expense to database."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        repo.add(expense)
        assert expense.id is not None

    def test_get_expense(self, db_session: Session, expense: Expense) -> None:
        """Test retrieving an expense by ID."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        repo.add(expense)
        retrieved = repo.get(expense.id)
        assert retrieved is not None
        assert retrieved.description == "Lunch"

    def test_get_nonexistent_expense_raises_error(self, db_session: Session) -> None:
        """Test that getting nonexistent expense raises error."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        with pytest.raises(ExpenseNotFoundError):
            repo.get(999)

    def test_update_expense(self, db_session: Session, expense: Expense) -> None:
        """Test updating an expense."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        repo.add(expense)
        expense.amount = Decimal("100.00")
        expense.description = "Updated lunch"
        repo.update(expense)
        updated = repo.get(expense.id)
        assert updated is not None
        assert updated.amount == Decimal("100.00")
        assert updated.description == "Updated lunch"

    def test_update_nonexistent_expense_raises_error(
        self, db_session: Session, expense: Expense
    ) -> None:
        """Test that updating nonexistent expense raises error."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        expense.id = 999
        with pytest.raises(ExpenseNotFoundError):
            repo.update(expense)

    def test_delete_expense(self, db_session: Session, expense: Expense) -> None:
        """Test deleting an expense."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        repo.add(expense)
        expense_id = expense.id
        repo.delete(expense_id)
        with pytest.raises(ExpenseNotFoundError):
            repo.get(expense_id)

    def test_delete_nonexistent_expense_raises_error(self, db_session: Session) -> None:
        """Test that deleting nonexistent expense raises error."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        with pytest.raises(ExpenseNotFoundError):
            repo.delete(999)

    def test_list_expenses(
        self, db_session: Session, category: ExpenseCategory
    ) -> None:
        """Test listing all expenses."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        for i in range(3):
            expense = Expense(
                amount=Decimal(str(i * 10)),
                currency=Currency.EUR,
                description=f"Expense {i}",
                date=datetime.now(),
                category_id=category.id,
            )
            repo.add(expense)
        expenses = repo.list()
        assert len(expenses) == 3

    def test_search_by_dates(
        self, db_session: Session, category: ExpenseCategory
    ) -> None:
        """Test searching expenses by date range."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        now = datetime.now()
        expense1 = Expense(
            amount=Decimal("10"),
            currency=Currency.EUR,
            description="Yesterday",
            date=now - timedelta(days=1),
            category_id=category.id,
        )
        expense2 = Expense(
            amount=Decimal("20"),
            currency=Currency.EUR,
            description="Today",
            date=now,
            category_id=category.id,
        )
        repo.add(expense1)
        repo.add(expense2)

        results = repo.search_by_dates(now - timedelta(days=2), now + timedelta(days=1))
        assert len(results) == 2

    def test_search_by_dates_no_results_raises_error(
        self, db_session: Session
    ) -> None:
        """Test that no results raises error."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        with pytest.raises(ExpenseNotFoundError):
            repo.search_by_dates(datetime.now(), datetime.now() + timedelta(days=1))

    def test_search_by_category(
        self, db_session: Session, category: ExpenseCategory
    ) -> None:
        """Test searching expenses by category."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        expense = Expense(
            amount=Decimal("10"),
            currency=Currency.EUR,
            description="Food expense",
            date=datetime.now(),
            category_id=category.id,
        )
        repo.add(expense)
        results = repo.search_by_category(category)
        assert len(results) == 1

    def test_search_by_category_no_results_raises_error(
        self, db_session: Session, category: ExpenseCategory
    ) -> None:
        """Test that no results for category raises error."""
        repo = DBExpenseRepo(DATABASE_URL, session=db_session)
        with pytest.raises(ExpenseNotFoundError):
            repo.search_by_category(category)


class TestDBCategoryRepoUpdate:
    """Additional tests for DBCategoryRepo update functionality."""

    def test_update_category(self, db_session: Session) -> None:
        """Test updating a category."""
        repo = DBCategoryRepo(DATABASE_URL, session=db_session)
        category = ExpenseCategory(name="Original")
        repo.add(category)
        # Get the category to have its ID
        retrieved = repo.get("Original")
        assert retrieved is not None
        retrieved.name = "Original"  # Same name, just testing the flow
        repo.update(retrieved)

    def test_update_nonexistent_category_raises_error(self, db_session: Session) -> None:
        """Test that updating nonexistent category raises error."""
        repo = DBCategoryRepo(DATABASE_URL, session=db_session)
        fake_category = ExpenseCategory(id=999, name="NonExistent")
        with pytest.raises(CategoryNotFoundError):
            repo.update(fake_category)


class TestDBReposOwnsSession:
    """Tests for DB repos with _owns_session=True (no session injection)."""

    @pytest.fixture(scope="function")
    def temp_db_url(self, tmp_path) -> str:
        """Create a temporary database URL."""
        db_path = tmp_path / "test_owns_session.db"
        return f"sqlite:///{db_path}"

    def test_category_repo_owns_session_crud(self, temp_db_url: str) -> None:
        """Test category repo creates and manages its own session."""
        from sqlmodel import SQLModel, create_engine

        # Create tables
        engine = create_engine(temp_db_url)
        SQLModel.metadata.create_all(engine)

        # Create repo without injecting session
        repo = DBCategoryRepo(temp_db_url)
        assert repo._owns_session is True

        # Add and retrieve
        category = ExpenseCategory(name="TestCategory")
        repo.add(category)
        categories = repo.list()
        assert "TestCategory" in categories

    def test_expense_repo_owns_session_crud(self, temp_db_url: str) -> None:
        """Test expense repo creates and manages its own session."""
        from sqlmodel import SQLModel, create_engine

        # Create tables
        engine = create_engine(temp_db_url)
        SQLModel.metadata.create_all(engine)

        # First create a category
        cat_repo = DBCategoryRepo(temp_db_url)
        category = ExpenseCategory(name="Food")
        cat_repo.add(category)

        # Get the category with its ID
        saved_category = cat_repo.get("Food")
        assert saved_category is not None

        # Create expense repo
        expense_repo = DBExpenseRepo(temp_db_url)
        assert expense_repo._owns_session is True

        # Add expense
        expense = Expense(
            amount=Decimal("10.00"),
            currency=Currency.EUR,
            description="Test expense",
            date=datetime.now(),
            category_id=saved_category.id,
        )
        expense_repo.add(expense)

        # List and verify
        expenses = expense_repo.list()
        assert len(expenses) == 1

    def test_category_repo_get_owns_session(self, temp_db_url: str) -> None:
        """Test category repo get with owns_session."""
        from sqlmodel import SQLModel, create_engine

        engine = create_engine(temp_db_url)
        SQLModel.metadata.create_all(engine)

        repo = DBCategoryRepo(temp_db_url)
        repo.add(ExpenseCategory(name="MyCategory"))

        # Get with new repo instance
        repo2 = DBCategoryRepo(temp_db_url)
        result = repo2.get("MyCategory")
        assert result is not None
        assert result.name == "MyCategory"

    def test_category_repo_delete_owns_session(self, temp_db_url: str) -> None:
        """Test category repo delete with owns_session."""
        from sqlmodel import SQLModel, create_engine

        engine = create_engine(temp_db_url)
        SQLModel.metadata.create_all(engine)

        repo = DBCategoryRepo(temp_db_url)
        repo.add(ExpenseCategory(name="ToDelete"))

        # Delete
        repo2 = DBCategoryRepo(temp_db_url)
        repo2.delete("ToDelete")

        # Verify deleted
        repo3 = DBCategoryRepo(temp_db_url)
        with pytest.raises(CategoryNotFoundError):
            repo3.get("ToDelete")

    def test_category_repo_update_owns_session(self, temp_db_url: str) -> None:
        """Test category repo update with owns_session."""
        from sqlmodel import SQLModel, create_engine

        engine = create_engine(temp_db_url)
        SQLModel.metadata.create_all(engine)

        repo = DBCategoryRepo(temp_db_url)
        repo.add(ExpenseCategory(name="Original"))

        # Get and update
        repo2 = DBCategoryRepo(temp_db_url)
        category = repo2.get("Original")
        assert category is not None
        # Just verifying the update path runs without error
        repo2.update(category)

    def test_expense_repo_get_owns_session(self, temp_db_url: str) -> None:
        """Test expense repo get with owns_session."""
        from sqlmodel import SQLModel, create_engine

        engine = create_engine(temp_db_url)
        SQLModel.metadata.create_all(engine)

        # Create category first
        cat_repo = DBCategoryRepo(temp_db_url)
        cat_repo.add(ExpenseCategory(name="Test"))
        category = cat_repo.get("Test")

        # Add expense
        expense_repo = DBExpenseRepo(temp_db_url)
        expense = Expense(
            amount=Decimal("50.00"),
            currency=Currency.USD,
            description="Test get",
            date=datetime.now(),
            category_id=category.id,
        )
        expense_repo.add(expense)

        # Get with new repo
        repo2 = DBExpenseRepo(temp_db_url)
        result = repo2.get(1)
        assert result is not None
        assert result.description == "Test get"

    def test_expense_repo_search_by_dates_owns_session(self, temp_db_url: str) -> None:
        """Test expense repo search_by_dates with owns_session."""
        from sqlmodel import SQLModel, create_engine

        engine = create_engine(temp_db_url)
        SQLModel.metadata.create_all(engine)

        # Create category
        cat_repo = DBCategoryRepo(temp_db_url)
        cat_repo.add(ExpenseCategory(name="Search"))
        category = cat_repo.get("Search")

        # Add expense
        now = datetime.now()
        expense_repo = DBExpenseRepo(temp_db_url)
        expense = Expense(
            amount=Decimal("25.00"),
            currency=Currency.EUR,
            description="Dated expense",
            date=now,
            category_id=category.id,
        )
        expense_repo.add(expense)

        # Search
        repo2 = DBExpenseRepo(temp_db_url)
        results = repo2.search_by_dates(now - timedelta(days=1), now + timedelta(days=1))
        assert len(results) == 1

    def test_expense_repo_search_by_category_owns_session(self, temp_db_url: str) -> None:
        """Test expense repo search_by_category with owns_session."""
        from sqlmodel import SQLModel, create_engine

        engine = create_engine(temp_db_url)
        SQLModel.metadata.create_all(engine)

        # Create category
        cat_repo = DBCategoryRepo(temp_db_url)
        cat_repo.add(ExpenseCategory(name="CatSearch"))
        category = cat_repo.get("CatSearch")

        # Add expense
        expense_repo = DBExpenseRepo(temp_db_url)
        expense = Expense(
            amount=Decimal("75.00"),
            currency=Currency.GBP,
            description="Category search",
            date=datetime.now(),
            category_id=category.id,
        )
        expense_repo.add(expense)

        # Search
        repo2 = DBExpenseRepo(temp_db_url)
        results = repo2.search_by_category(category)
        assert len(results) == 1

    def test_expense_repo_update_owns_session(self, temp_db_url: str) -> None:
        """Test expense repo update with owns_session."""
        from sqlmodel import SQLModel, create_engine

        engine = create_engine(temp_db_url)
        SQLModel.metadata.create_all(engine)

        # Create category
        cat_repo = DBCategoryRepo(temp_db_url)
        cat_repo.add(ExpenseCategory(name="UpdateTest"))
        category = cat_repo.get("UpdateTest")

        # Add expense
        expense_repo = DBExpenseRepo(temp_db_url)
        expense = Expense(
            amount=Decimal("100.00"),
            currency=Currency.EUR,
            description="Original",
            date=datetime.now(),
            category_id=category.id,
        )
        expense_repo.add(expense)

        # Get and update
        repo2 = DBExpenseRepo(temp_db_url)
        to_update = repo2.get(1)
        assert to_update is not None
        to_update.amount = Decimal("200.00")
        to_update.description = "Updated"
        repo2.update(to_update)

        # Verify
        repo3 = DBExpenseRepo(temp_db_url)
        result = repo3.get(1)
        assert result.amount == Decimal("200.00")
        assert result.description == "Updated"

    def test_expense_repo_delete_owns_session(self, temp_db_url: str) -> None:
        """Test expense repo delete with owns_session."""
        from sqlmodel import SQLModel, create_engine

        engine = create_engine(temp_db_url)
        SQLModel.metadata.create_all(engine)

        # Create category
        cat_repo = DBCategoryRepo(temp_db_url)
        cat_repo.add(ExpenseCategory(name="DeleteTest"))
        category = cat_repo.get("DeleteTest")

        # Add expense
        expense_repo = DBExpenseRepo(temp_db_url)
        expense = Expense(
            amount=Decimal("50.00"),
            currency=Currency.EUR,
            description="To delete",
            date=datetime.now(),
            category_id=category.id,
        )
        expense_repo.add(expense)

        # Delete
        repo2 = DBExpenseRepo(temp_db_url)
        repo2.delete(1)

        # Verify deleted
        repo3 = DBExpenseRepo(temp_db_url)
        with pytest.raises(ExpenseNotFoundError):
            repo3.get(1)
