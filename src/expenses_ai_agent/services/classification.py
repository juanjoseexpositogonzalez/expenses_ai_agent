import logging
from dataclasses import dataclass
from datetime import datetime, timezone

from expenses_ai_agent.llms.base import MESSAGES, Assistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT
from expenses_ai_agent.prompts.user import USER_PROMPT
from expenses_ai_agent.storage.exceptions import CategoryNotFoundError
from expenses_ai_agent.storage.models import Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import CategoryRepository, ExpenseRepository

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of an expense classification operation."""

    response: ExpenseCategorizationResponse
    expense: Expense | None = None
    category: ExpenseCategory | None = None
    is_persisted: bool = False


class ClassificationService:
    """Service for classifying and persisting expenses.

    Encapsulates the classification pipeline so both the CLI and
    the Telegram bot can share the same business logic.
    """

    def __init__(
        self,
        assistant: Assistant,
        category_repo: CategoryRepository | None = None,
        expense_repo: ExpenseRepository | None = None,
    ) -> None:
        self.assistant = assistant
        self.category_repo = category_repo
        self.expense_repo = expense_repo

    def classify(
        self,
        expense_description: str,
        persist: bool = False,
        telegram_user_id: int | None = None,
    ) -> ClassificationResult:
        """Classify an expense description using the LLM.

        Args:
            expense_description: The raw expense text.
            persist: Whether to save the result to the database.
            telegram_user_id: Optional Telegram user ID for multiuser support.

        Returns:
            ClassificationResult containing the LLM response and,
            if persisted, the created database objects.

        Raises:
            ValueError: If expense_description is blank.
            RuntimeError: If persist is True but repos are not set.
        """
        if not expense_description.strip():
            raise ValueError("Expense description cannot be empty")

        logger.info("Classifying expense: %s", expense_description[:80])

        messages: MESSAGES = [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT.format(expense_description=expense_description),
            },
        ]

        response: ExpenseCategorizationResponse = self.assistant.completion(messages)
        logger.info(
            "Classified as: %s (confidence: %.2f)",
            response.category,
            response.confidence,
        )

        result = ClassificationResult(response=response)

        if persist:
            self._ensure_repos()
            category, expense = self._persist_expense(
                response=response,
                description=expense_description,
                telegram_user_id=telegram_user_id,
            )
            result.category = category
            result.expense = expense
            result.is_persisted = True

        return result

    def persist_with_category(
        self,
        expense_description: str,
        llm_response: ExpenseCategorizationResponse,
        selected_category: str,
        telegram_user_id: int | None = None,
    ) -> ClassificationResult:
        """Persist an expense with a user-selected category (HITL override).

        If *selected_category* matches the LLM suggestion the original
        response is persisted unchanged.  Otherwise a modified response
        with confidence=1.0 is stored.

        Args:
            expense_description: Original expense text.
            llm_response: The original LLM classification.
            selected_category: The category the user chose.

        Returns:
            ClassificationResult with persisted expense.

        Raises:
            RuntimeError: If repos are not set.
        """
        self._ensure_repos()

        if selected_category == llm_response.category:
            response = llm_response
        else:
            logger.info(
                "Category override: %s -> %s",
                llm_response.category,
                selected_category,
            )
            response = ExpenseCategorizationResponse(
                category=selected_category,
                total_amount=llm_response.total_amount,
                currency=llm_response.currency,
                confidence=1.0,
                cost=llm_response.cost,
                comments=f"User override from '{llm_response.category}'",
                timestamp=datetime.now(timezone.utc),
            )

        category, expense = self._persist_expense(
            response=response,
            description=expense_description,
            telegram_user_id=telegram_user_id,
        )

        return ClassificationResult(
            response=response,
            expense=expense,
            category=category,
            is_persisted=True,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _ensure_repos(self) -> None:
        if self.category_repo is None or self.expense_repo is None:
            raise RuntimeError(
                "Cannot persist without both category_repo and expense_repo"
            )

    def _persist_expense(
        self,
        response: ExpenseCategorizationResponse,
        description: str,
        telegram_user_id: int | None = None,
    ) -> tuple[ExpenseCategory, Expense]:
        """Get-or-create the category and persist the expense."""
        assert self.category_repo is not None  # noqa: S101
        assert self.expense_repo is not None  # noqa: S101

        category_name = response.category.strip()

        try:
            category = self.category_repo.get(name=category_name)
            logger.debug("Reusing existing category: %s", category_name)
        except CategoryNotFoundError:
            category = ExpenseCategory(name=category_name)
            self.category_repo.add(category)
            logger.info("Created new category: %s", category_name)

        expense = Expense(
            amount=response.total_amount,
            currency=response.currency,
            description=description,
            category=category,
            telegram_user_id=telegram_user_id,
        )
        self.expense_repo.add(expense)
        logger.info("Persisted expense id=%s", expense.id)

        return category, expense
