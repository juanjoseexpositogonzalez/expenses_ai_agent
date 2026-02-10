# Building a CLI with Typer and Rich

Typer creates beautiful command-line interfaces with minimal code. Rich adds formatted tables and colors. This lesson covers building the `expenses-ai-agent` CLI.


## Why Typer?

Traditional CLIs require lots of boilerplate:

```python
# argparse - verbose
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("description", help="Expense description")
parser.add_argument("--db", action="store_true", help="Persist to database")
args = parser.parse_args()
```

Typer uses Python type hints:

```python
# Typer - clean
import typer

app = typer.Typer()

@app.command()
def classify(
    description: str = typer.Argument(..., help="Expense description"),
    db: bool = typer.Option(False, "--db", help="Persist to database"),
):
    """Classify an expense using AI."""
    ...
```


## Creating the App

```python
# cli/cli.py
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="expenses-ai-agent",
    help="AI-powered expense classification",
)
console = Console()


@app.command()
def classify(
    description: str = typer.Argument(..., help="Expense description to classify"),
    db: bool = typer.Option(False, "--db", help="Persist to database"),
):
    """Classify an expense using AI."""
    service = build_classification_service(persist=db)
    result = service.classify(description, persist=db)

    # Display results
    display_result(result)
```


## Rich Tables for Output

```python
from rich.table import Table

def display_result(result: ClassificationResult) -> None:
    """Display classification result in a formatted table."""
    table = Table(title="Classification Result")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="green")

    response = result.response
    table.add_row("Category", response.category)
    table.add_row("Amount", f"{response.total_amount}")
    table.add_row("Currency", str(response.currency))
    table.add_row("Confidence", f"{response.confidence:.0%}")
    table.add_row("Persisted", "Yes" if result.persisted else "No")

    console.print(table)
```

Output:

```
+------------------+----------------------------+
|      Field       |           Value            |
+------------------+----------------------------+
| Category         | Food                       |
| Amount           | 5.50                       |
| Currency         | USD                        |
| Confidence       | 95%                        |
| Persisted        | No                         |
+------------------+----------------------------+
```


## Registering the Entry Point

In `pyproject.toml`:

```toml
[project.scripts]
expenses-ai-agent = "expenses_ai_agent.cli.cli:app"
```

After installing with `uv pip install -e ".[dev]"`:

```bash
expenses-ai-agent --help
expenses-ai-agent classify "Coffee $5.50"
expenses-ai-agent classify "Taxi 45 EUR" --db
```


## Error Handling

```python
@app.command()
def classify(description: str, db: bool = False):
    try:
        service = build_classification_service(persist=db)
        result = service.classify(description, persist=db)
        display_result(result)
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(code=1)
```


## Python Comparison

| argparse | Typer |
|----------|-------|
| Explicit parser setup | Decorators |
| Manual type conversion | Type hints |
| Verbose help text | Auto-generated help |
| No formatting | Rich integration |


## CLI in Our Project

The CLI provides:

| Command | Purpose |
|---------|---------|
| `classify <desc>` | Classify an expense |
| `classify <desc> --db` | Classify and persist |
| `greet -g <name>` | Test greeting (example) |


## Further Reading

- [Typer Documentation](https://typer.tiangolo.com/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Python Entry Points](https://packaging.python.org/en/latest/specifications/entry-points/)
