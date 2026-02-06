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
from expenses_ai_agent.services.classification import ClassificationService
from expenses_ai_agent.services.preprocessing import InputPreprocessor
from expenses_ai_agent.storage.repo import DBCategoryRepo, DBExpenseRepo

DB_URL = config("DATABASE_URL", default="sqlite:///./expenses.db")  # type: ignore
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
    preprocessor = InputPreprocessor()
    preprocessing = preprocessor.preprocess(expense)

    if not preprocessing.is_valid:
        console.print("[red]Invalid input:[/red]")
        for error in preprocessing.validation_errors:
            console.print(f"  [red]{error}[/red]")
        raise typer.Exit(1)

    for warning in preprocessing.warnings:
        console.print(f"  [yellow]{warning}[/yellow]")

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

        if add_to_db:
            with Session(engine) as session:
                category_repo = DBCategoryRepo(DB_URL, session=session)
                expense_repo = DBExpenseRepo(DB_URL, session=session)

                service = ClassificationService(
                    assistant=openai_assistant,
                    category_repo=category_repo,
                    expense_repo=expense_repo,
                )
                result = service.classify(
                    expense_description=preprocessing.cleaned_text,
                    persist=True,
                )
                console.print(
                    "Expense added to the database successfully!",
                    style="bold green",
                )
        else:
            service = ClassificationService(assistant=openai_assistant)
            result = service.classify(
                expense_description=preprocessing.cleaned_text,
                persist=False,
            )

        console.print(
            Panel(
                "Expense classified successfully!",
                title="Success",
                box=box.ROUNDED,
            )
        )

    completion = result.response

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
        completion.category,
        str(completion.total_amount),
        completion.currency.value,
        f"{completion.confidence:.2f}",
        f"${completion.cost:.6f}",
    )

    console.print(table)
