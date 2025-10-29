import logging
from typing import Final

import typer
from decouple import config
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
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

# Initialize Typer app and Rich console
app = typer.Typer(
    name="expenses-ai-agent",
    help="A command-line interface for managing expenses with AI assistance.",
    add_completion=False,
)

console = Console()


@app.command()
def greet(
    name: str = typer.Option(
        ...,
        "--greet",
        "-g",
        help="Greets the user with their name.",
    ),
):
    """Greet the user with their name."""
    console.print(
        Panel(
            f"Hello, [bold green]{name}[/bold green]!",
            title="Greeting",
            box=box.ROUNDED,
        )
    )


@app.command()
def classify(
    expense: str = typer.Argument(
        None,
        help="The expense description to classify.",
    ),
    add_to_db: bool = typer.Option(
        False,
        "--db/--no-db",
        help="Whether to add the classified expense to the database.",
    ),
):
    """Classify an expense using AI assistance."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(description="Classifying expense...", total=None)

        openai_assistant = OpenAIAssistant(
            provider=LLMProvider.OPENAI,
            api_key=OPENAI_API_KEY,
            model="gpt-4.1-nano-2025-04-14",
            max_response_tokens=500,
            temperature=0.3,
            top_p=1.0,
            structured_output=ExpenseCategorizationResponse,
        )  # type: ignore

        messages = [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {
                "role": "user",
                "content": USER_PROMPT.format(expense_description=expense),
            },
        ]

        completion: ExpenseCategorizationResponse = openai_assistant.completion(
            messages=messages
        )

        if add_to_db:
            console.print(
                "Adding classified expense to the database...", style="bold blue"
            )
            category: ExpenseCategory = ExpenseCategory(
                name=completion.category.strip()  # type: ignore
            )
            expense_instance: Expense = Expense(
                amount=completion.total_amount,  # type: ignore
                currency=completion.currency,  # type: ignore
                description=expense,
                category=category,
            )

            with Session(engine) as session:
                category_repo = DBCategoryRepo(session)  # type: ignore
                try:
                    existing_category = category_repo.get(
                        name=completion.category.strip()
                    )  # type: ignore
                    expense_instance.category = existing_category
                except CategoryNotFoundError:
                    session.add(category)
                    session.commit()
                    session.refresh(category)
                    expense_instance.category = category

                session.add(expense_instance)
                session.commit()
                console.print(
                    "Expense added to the database successfully!", style="bold green"
                )

        console.print(
            Panel("Expense classified successfully!", title="Success", box=box.ROUNDED)
        )

    # Display classification result
    table = Table(title="Expense Classification Result", box=box.ROUNDED)
    table.add_column("Description", style="cyan", no_wrap=True)
    table.add_column("Category", style="magenta")
    table.add_column("Amount", style="green")
    table.add_column("Currency", style="yellow")
    table.add_column("Confidence", style="blue")
    table.add_column("Classification Cost (USD)", style="red")

    table.add_row(
        expense,
        completion.category,  # type: ignore
        str(completion.total_amount),  # type: ignore
        completion.currency.value,  # type: ignore
        f"{completion.confidence:.2f}",  # type: ignore
        f"${completion.cost:.6f}",  # type: ignore
    )

    console.print(table)
