from typing import Any, Final

import pytest
from sqlalchemy.exc import OperationalError
from sqlmodel import Session, SQLModel, create_engine

from expenses_ai_agent.storage.exceptions import (
    CategoryNotFoundError,
)
from expenses_ai_agent.storage.models import ExpenseCategory
from expenses_ai_agent.storage.repo import CategoryRepository, DBCategoryRepo

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
    except OperationalError as e:
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


@pytest.fixture(scope="function")
def example_category() -> ExpenseCategory:
    return ExpenseCategory(name="Utilities")


@pytest.fixture(scope="function")
def example_categories() -> list[ExpenseCategory]:
    return [
        ExpenseCategory(name="Food"),
        ExpenseCategory(name="Transportation"),
        ExpenseCategory(name="Entertainment"),
    ]


@pytest.fixture(scope="function")
def add_snippets(db_session: Any, example_categories: list[ExpenseCategory]) -> None:
    for category in example_categories:
        db_session.add(category)
    db_session.commit()


def test_cannot_instantiate_abstract_repo():
    with pytest.raises(TypeError) as excinfo:
        CategoryRepository()  # type: ignore
    assert (
        "Can't instantiate abstract class CategoryRepository without an implementation for abstract methods 'add', 'delete', 'get', 'list', 'update'"
        in str(excinfo.value)
    )


def test_cannot_subclass_without_all_methods_implemented():
    class IncompleteRepo(CategoryRepository):
        def add(self, category: ExpenseCategory) -> None:
            pass

    with pytest.raises(TypeError) as excinfo:
        IncompleteRepo()  # type: ignore
    assert (
        "Can't instantiate abstract class IncompleteRepo without an implementation for abstract methods 'delete', 'get', 'list', 'update'"
        in str(excinfo.value)
    )


def test_category_db_implementation(db_session: Any, example_category: ExpenseCategory):
    # Use the new session parameter to provide the test database session
    repo = DBCategoryRepo(DATABASE_URL, session=db_session)

    repo.add(example_category)
    fetched = repo.get(example_category.name)
    assert fetched is not None
    assert len(repo.list()) == 1
    assert repo.get(example_category.name).name == "Utilities"  # type: ignore
    repo.delete(example_category.name)
    with pytest.raises(CategoryNotFoundError):
        repo.get(example_category.name)
    with pytest.raises(CategoryNotFoundError):
        repo.delete(example_category.name)
