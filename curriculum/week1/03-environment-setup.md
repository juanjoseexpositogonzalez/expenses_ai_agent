# Environment Setup

This lesson walks you through setting up your complete Python development environment for the Expense AI Agent project.


## Prerequisites

Before you begin, ensure you have:

- Python 3.12 or higher
- Git for version control
- A code editor with Python support (VS Code with Python extension recommended)


## Step 1: Install UV Package Manager

UV is a fast Python package manager written in Rust. It replaces pip and virtualenv with better performance:

```bash
# Install UV (Linux/macOS)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with pip
pip install uv
```


## Step 2: Clone and Setup the Project

```bash
# Clone the repository
git clone <your-repo-url>
cd expenses_ai_agent

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```


## Step 3: Environment Configuration

Create your `.env` file from the template:

```bash
cp .env.example .env
```

For Week 1, you only need to set:

```bash
DATABASE_URL=sqlite:///expenses.db
```

You'll add API keys for LLM providers in later weeks.


## Step 4: Verify Installation

Run the following commands to verify everything is working:

```bash
# Check Python version
python --version  # Should be 3.12+

# Run tests (they should fail - that's expected!)
pytest tests/unit/test_week1.py -v

# Check code quality tools
ruff check src/
ruff format --check .
```


## Project Structure

Your project should look like this after Week 1:

```
expenses_ai_agent/
+-- src/
|   +-- expenses_ai_agent/
|       +-- __init__.py
|       +-- storage/
|           +-- __init__.py
|           +-- models.py          # Currency, ExpenseCategory, Expense
|           +-- exceptions.py      # CategoryNotFoundError, ExpenseNotFoundError
|           +-- repo.py            # Repository abstract classes + InMemory implementations
+-- tests/
|   +-- unit/
|       +-- test_week1.py          # Your Week 1 tests
+-- pyproject.toml
+-- .env
+-- .env.example
```


## IDE Setup

For VS Code, install these extensions:

- **Python** - Microsoft's Python extension
- **Pylance** - Fast type checking
- **Ruff** - Fast linting and formatting

Configure ruff as your formatter in `.vscode/settings.json`:

```json
{
    "editor.formatOnSave": true,
    "python.formatting.provider": "none",
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff"
    }
}
```


## Ready?

With your environment set up, you're ready to learn about the Repository pattern in the next lesson.
