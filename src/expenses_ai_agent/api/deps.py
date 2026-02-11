"""FastAPI dependency injection."""

from collections.abc import Generator
from typing import Annotated

from decouple import config
from fastapi import Depends, Header
from sqlmodel import Session, create_engine

from expenses_ai_agent.llms.base import LLMProvider
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.services.classification import ClassificationService
from expenses_ai_agent.storage.repo import (
    DBCategoryRepo,
    DBExpenseRepo,
)

# Database setup
DATABASE_URL = config("DATABASE_URL", default="sqlite:///./expenses.db", cast=str)
engine = create_engine(DATABASE_URL)


def get_session() -> Generator[Session, None, None]:
    """Yield a database session."""
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def get_user_id(
    x_user_id: Annotated[int | None, Header(alias="X-User-ID")] = None,
) -> int:
    """Get user ID from header or use default.

    For demo purposes, defaults to a configured user ID if not provided.
    """
    if x_user_id is not None:
        return x_user_id
    default_user_id = config("DEFAULT_USER_ID", default=12345, cast=int)
    return default_user_id


UserIdDep = Annotated[int, Depends(get_user_id)]


def get_category_repo(session: SessionDep) -> DBCategoryRepo:
    """Get category repository with injected session."""
    return DBCategoryRepo(DATABASE_URL, session=session)


def get_expense_repo(session: SessionDep) -> DBExpenseRepo:
    """Get expense repository with injected session."""
    return DBExpenseRepo(DATABASE_URL, session=session)


CategoryRepoDep = Annotated[DBCategoryRepo, Depends(get_category_repo)]
ExpenseRepoDep = Annotated[DBExpenseRepo, Depends(get_expense_repo)]


def get_classification_service(
    category_repo: CategoryRepoDep,
    expense_repo: ExpenseRepoDep,
) -> ClassificationService:
    """Get classification service with dependencies."""
    api_key = config("OPENAI_API_KEY", cast=str)
    model = config("OPENAI_MODEL", default="gpt-4.1-nano-2025-04-14", cast=str)

    assistant = OpenAIAssistant(
        provider=LLMProvider.OPENAI,
        api_key=api_key,
        model=model,
        max_response_tokens=500,
        temperature=0.3,
        top_p=1.0,
        structured_output=ExpenseCategorizationResponse,
    )

    return ClassificationService(
        assistant=assistant,  # type: ignore[arg-type]
        category_repo=category_repo,
        expense_repo=expense_repo,
    )


ClassificationServiceDep = Annotated[
    ClassificationService, Depends(get_classification_service)
]
