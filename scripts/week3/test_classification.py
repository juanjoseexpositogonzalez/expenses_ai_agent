import logging
from typing import Final

from decouple import config
from sqlmodel import Session, create_engine

from expenses_ai_agent.llms.base import LLMProvider
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT
from expenses_ai_agent.prompts.user import USER_PROMPT
from expenses_ai_agent.storage.exceptions import CategoryNotFoundError
from expenses_ai_agent.storage.models import Expense, ExpenseCategory
from expenses_ai_agent.storage.repo import DBCategoryRepo

DB_URL = config("DB_URL", default="sqlite:///expenses.db")  # type: ignore
engine = create_engine(DB_URL)  # type: ignore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY: Final[str] = config("OPENAI_API_KEY")  # type: ignore


def main() -> None:
    openai_assistant = OpenAIAssistant(
        provider=LLMProvider.OPENAI,
        api_key=OPENAI_API_KEY,
        model="gpt-4.1-nano-2025-04-14",
        max_response_tokens=500,
        temperature=0.7,
        top_p=1.0,
        structured_output=ExpenseCategorizationResponse,
    )  # type: ignore

    test_expenses = [
        "Lunch at a restaurant for $25.50",
        "Taxi fare to the airport for 45 euros",
        "Office supplies purchase. It costed AUD 120",
        "Client entertainment dinner for 100 yens",
        "Monthly software subscription for $29.99",
    ]

    # Test: Classification task
    logger.info("=== Test: Classification Task ===")
    for test_expense in test_expenses:
        messages = [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT.format(expense_description=test_expense),
            },
        ]

        completion: ExpenseCategorizationResponse = openai_assistant.completion(
            messages=messages
        )
        logger.info("Classification result")
        logger.info('Expense: "%s"', test_expense)
        logger.info("  Category: %s", completion.category)  # type: ignore
        logger.info(
            "  Amount: %s %s", completion.total_amount, completion.currency.value
        )  # type: ignore
        logger.info("  Confidence: %.2f", completion.confidence)  # type: ignore
        logger.info("  Cost: $%.6f", completion.cost)  # type: ignore
        if completion.comments:  # type: ignore
            logger.info("  Comments: %s", completion.comments)  # type: ignore

        # Add it to the database
        logger.info("-----------------------------------")
        logger.info("Adding classified expense to the database...")
        category: ExpenseCategory = ExpenseCategory(
            name=completion.category.strip()  # type: ignore
        )
        expense: Expense = Expense(
            amount=completion.total_amount,  # type: ignore
            currency=completion.currency,  # type: ignore
            description=test_expense,
            category=category,
        )
        logger.info("Expense instance created: %s", expense)
        breakpoint()

        # Try to get the category, if it doesn't exist, create it
        with Session(engine) as session:
            repo = DBCategoryRepo(str(DB_URL), session)  # type: ignore
            try:
                category = repo.get(name=completion.category.strip())  # type: ignore
                logger.info("Category '%s' already exists", category.name)  # type: ignore

            except CategoryNotFoundError:
                logger.info(
                    "Category '%s' not found, creating it...",
                    completion.category.strip(),
                )  # type: ignore
                category = ExpenseCategory.create(name=completion.category.strip())  # type: ignore
                repo.add(category)
                session.refresh(category)
                logger.info("Category '%s' created successfully", category.name)  # type: ignore


if __name__ == "__main__":
    logger.info("===================================")
    logger.info("Starting classification tests...")
    logger.info("===================================")
    main()
    logger.info("===================================")
    logger.info("Ending classification tests.")
    logger.info("===================================")
