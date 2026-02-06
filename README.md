# 💰 Expenses AI Agent

An intelligent expense categorization and management system powered by Large Language Models (LLMs). This project demonstrates how to build an AI-powered application that automatically classifies expenses, manages financial data, and provides structured outputs using modern Python development practices.

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Project Structure](#-project-structure)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Core Components](#-core-components)
- [Development](#-development)
- [Testing](#-testing)
- [API Reference](#-api-reference)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

**Expenses AI Agent** is a sophisticated Python application that leverages the power of Large Language Models to automate expense tracking and categorization. The system uses AI to:

- **Automatically classify expenses** into predefined categories (Food & Dining, Transportation, Healthcare, etc.)
- **Extract financial data** from natural language descriptions
- **Convert currencies** using real-time exchange rates
- **Format datetime** information consistently across timezones
- **Store and manage** expense records with SQLModel/SQLite

This project is ideal for:
- Learning how to integrate LLMs into real-world applications
- Understanding structured outputs from AI models
- Building financial management tools
- Exploring multi-provider LLM architectures (OpenAI, Groq, Anthropic)

---

## ✨ Features

### 🤖 AI-Powered Classification
- **Multi-provider support**: OpenAI, Groq, and Anthropic (extensible)
- **Structured outputs**: Pydantic models for type-safe AI responses
- **Smart categorization**: 12+ predefined expense categories with intelligent classification
- **Confidence scoring**: Each classification includes a confidence metric (0.0 to 1.0)
- **Cost tracking**: Automatic API cost calculation per request

### 🛠️ Utility Functions
- **Currency conversion**: Real-time FX rates via ExchangeRate-API
- **Multi-currency support**: USD, EUR, GBP, JPY, AUD, CAD, CHF, CNY, SEK, NZD
- **Datetime formatting**: Timezone-aware formatting (DD/MM/YYYY HH:MM)
- **Tool calling**: Function calling capabilities for enhanced AI interactions

### 💾 Data Management
- **Repository pattern**: Abstract interfaces for flexible storage backends
- **SQLModel integration**: Type-safe ORM with SQLAlchemy under the hood
- **Multiple implementations**: In-memory and database-backed repositories
- **Relationship management**: Expenses linked to categories with proper foreign keys
- **Session handling**: Context manager support for safe database operations

### 🔧 Developer Experience
- **Type safety**: Full type hints throughout the codebase
- **Modern Python**: Python 3.13+ with latest features
- **uv integration**: Fast, reliable dependency management
- **Structured logging**: Comprehensive logging for debugging
- **Testing suite**: Unit tests with pytest and coverage reporting

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Application                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                  LLM Assistant Layer                         │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────┐       │
│  │  OpenAI    │  │   Groq     │  │   Anthropic     │       │
│  │ Assistant  │  │ Assistant  │  │   Assistant     │       │
│  └────────────┘  └────────────┘  └─────────────────┘       │
│         (Protocol-based abstraction via Assistant)          │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                    Tools & Utilities                         │
│  ┌──────────────────┐  ┌─────────────────────────┐         │
│  │  Currency        │  │  Datetime Formatter     │         │
│  │  Converter       │  │                         │         │
│  └──────────────────┘  └─────────────────────────┘         │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│                  Storage Layer                               │
│  ┌────────────────────┐  ┌──────────────────────┐          │
│  │  Category Repo     │  │   Expense Repo       │          │
│  │  (DB/In-Memory)    │  │   (DB/In-Memory)     │          │
│  └────────────────────┘  └──────────────────────┘          │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              Database (SQLite/PostgreSQL)                    │
└─────────────────────────────────────────────────────────────┘
```

### Design Patterns Used

1. **Protocol Pattern**: `Assistant` protocol defines a contract for all LLM implementations
2. **Repository Pattern**: Abstract storage interfaces for flexible data persistence
3. **Factory Pattern**: Different repository implementations (In-Memory, Database)
4. **Strategy Pattern**: Swappable LLM providers with consistent interfaces
5. **Dependency Injection**: Constructor-based injection of API keys and configurations

---

## 📁 Project Structure

```
expenses_ai_agent/
├── src/
│   └── expenses_ai_agent/
│       ├── __init__.py              # Package entry point
│       ├── cli/                     # Command-line interface
│       │   ├── __init__.py
│       │   └── cli.py               # Typer CLI with classify/greet commands
│       ├── llms/                    # LLM integrations
│       │   ├── __init__.py
│       │   ├── base.py              # Assistant protocol & base types
│       │   ├── openai.py            # OpenAI implementation
│       │   ├── groq.py              # Groq implementation
│       │   └── output.py            # Pydantic response models
│       ├── prompts/                 # System & user prompts
│       │   ├── __init__.py
│       │   ├── system.py            # Classification system prompt
│       │   └── user.py              # User prompt templates
│       ├── services/                # Business logic layer
│       │   ├── __init__.py
│       │   ├── classification.py    # ClassificationService
│       │   └── preprocessing.py     # InputPreprocessor (validation, XSS)
│       ├── storage/                 # Data persistence layer
│       │   ├── __init__.py
│       │   ├── models.py            # SQLModel entities
│       │   ├── repo.py              # Repository implementations
│       │   └── exceptions.py        # Custom exceptions
│       ├── telegram/                # Telegram bot
│       │   ├── __init__.py
│       │   ├── bot.py               # ExpenseTelegramBot main class
│       │   ├── handlers.py          # Conversation handlers (HITL flow)
│       │   ├── keyboards.py         # Inline keyboard builders
│       │   └── exceptions.py        # Telegram-specific exceptions
│       ├── tools/                   # LLM function calling tools
│       │   ├── __init__.py
│       │   └── tools.py             # Tool schemas
│       └── utils/                   # Utility functions
│           ├── __init__.py
│           ├── currency.py          # Currency conversion
│           ├── date_formatter.py    # Datetime formatting
│           └── logging_config.py    # Centralized logging setup
├── scripts/                         # Example scripts & tests
│   ├── week1/
│   │   ├── currency_test.py
│   │   └── first_workflow.py
│   ├── week2/
│   │   ├── test_groq_client.py
│   │   ├── test_openai_client.py
│   │   └── test_openai_tools.py
│   └── week3/
│       ├── test_classification.py   # Main classification demo
│       └── test_expense_repo.py
├── tests/                           # Test suite (96% coverage)
│   ├── unit/                        # Unit tests
│   │   ├── test_bot.py
│   │   ├── test_classification_service.py
│   │   ├── test_cli.py
│   │   ├── test_db_repos.py
│   │   ├── test_keyboards.py
│   │   ├── test_model.py
│   │   ├── test_openai_assistant.py
│   │   ├── test_preprocessing.py
│   │   ├── test_repo.py
│   │   ├── test_telegram_exceptions.py
│   │   ├── test_telegram_handlers.py
│   │   └── test_utils.py
│   └── integration/                 # Integration tests (real API calls)
│       ├── test_currency_integration.py
│       └── test_openai_integration.py
├── .env.example                     # Environment variables template
├── pyproject.toml                   # Project configuration & dependencies
├── LICENSE                          # MIT License
└── README.md                        # This file
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.13+**: This project requires Python 3.13 or higher
- **uv**: Modern Python package installer and resolver ([Install uv](https://github.com/astral-sh/uv))

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a blazing-fast Python package installer and resolver written in Rust. It's significantly faster than pip and provides better dependency resolution.

```bash
# 1. Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone the repository
git clone https://github.com/juanjoseexpositogonzalez/expenses_ai_agent.git
cd expenses_ai_agent

# 3. Create a virtual environment with uv
uv venv

# 4. Activate the virtual environment
# On Windows (Git Bash)
source .venv/Scripts/activate
# On macOS/Linux
source .venv/bin/activate

# 5. Install dependencies with uv
uv pip install -e .

# 6. Install development dependencies (optional)
uv pip install -e ".[dev]"
```

### Alternative: Using pip

```bash
# 1. Clone the repository
git clone https://github.com/juanjoseexpositogonzalez/expenses_ai_agent.git
cd expenses_ai_agent

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate the virtual environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate

# 4. Install the package
pip install -e .

# 5. Install development dependencies (optional)
pip install -e ".[dev]"
```

### Why uv?

- **⚡ Speed**: 10-100x faster than pip for dependency resolution
- **🔒 Reliability**: Better dependency resolution with conflict detection
- **🎯 Modern**: Built for modern Python workflows
- **🔄 Compatible**: Drop-in replacement for pip commands
- **📦 Lightweight**: Single binary, no Python installation required

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root (use `.env.example` as a template):

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your credentials:

```bash
# Database URLs
EXPENSES_DATABASE_URL="sqlite:///./expenses.db"
AGENT_DATABASE_URL="sqlite:///./agent.db"

# LLM API Keys (get at least one)
OPENAI_API_KEY="sk-your-openai-api-key-here"
GROQ_API_KEY="gsk_your-groq-api-key-here"
ANTHROPIC_API_KEY="sk-ant-your-anthropic-key-here"

# Currency Conversion API
EXCHANGE_RATE_API_KEY="your-exchange-rate-api-key"

# Telegram Bot (optional - for expenses-telegram-bot)
TELEGRAM_BOT_TOKEN="your-telegram-bot-token"
```

### Getting API Keys

| Provider | Sign Up | Free Tier | Notes |
|----------|---------|-----------|-------|
| **OpenAI** | [platform.openai.com](https://platform.openai.com/signup) | $5 credit | GPT-4, GPT-5 models available |
| **Groq** | [console.groq.com](https://console.groq.com/) | ✅ Free | Ultra-fast inference, Llama models |
| **Anthropic** | [console.anthropic.com](https://console.anthropic.com/) | $5 credit | Claude models (Opus, Sonnet, Haiku) |
| **ExchangeRate-API** | [exchangerate-api.com](https://www.exchangerate-api.com/) | 1,500 requests/month | Real-time FX rates |
| **Telegram** | [@BotFather](https://t.me/botfather) | ✅ Free | Create bot, get token |

### Database Configuration

By default, the project uses SQLite for simplicity:

```python
# SQLite (default - no setup required)
DATABASE_URL = "sqlite:///./expenses.db"

# PostgreSQL (for production)
DATABASE_URL = "postgresql://user:password@localhost:5432/expenses"

# MySQL
DATABASE_URL = "mysql://user:password@localhost:3306/expenses"
```

---

## 💻 Usage

### Quick Start Example

```python
from decimal import Decimal
from decouple import config
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT
from expenses_ai_agent.prompts.user import USER_PROMPT

# Initialize the OpenAI assistant
assistant = OpenAIAssistant(
    api_key=config("OPENAI_API_KEY"),
    model="gpt-4.1-nano-2025-04-14",
    max_response_tokens=500,
    temperature=0.7,
    structured_output=ExpenseCategorizationResponse,
)

# Classify an expense
expense_description = "Coffee at Starbucks for $5.50"
messages = [
    {"role": "system", "content": CLASSIFICATION_PROMPT},
    {"role": "user", "content": USER_PROMPT.format(expense_description=expense_description)},
]

result: ExpenseCategorizationResponse = assistant.completion(messages)

print(f"Category: {result.category}")
print(f"Amount: {result.total_amount} {result.currency.value}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Cost: ${result.cost:.6f}")
```

### Running the Classification Demo

```bash
# Run the complete classification workflow
python scripts/week3/test_classification.py
```

This demo will:
1. Classify several test expenses using OpenAI
2. Extract amounts, currencies, and categories
3. Store results in the SQLite database
4. Display confidence scores and API costs

### Using Different LLM Providers

```python
# OpenAI
from expenses_ai_agent.llms.openai import OpenAIAssistant
assistant = OpenAIAssistant(api_key=api_key, model="gpt-4.1-nano-2025-04-14")

# Groq (faster, free tier available)
from expenses_ai_agent.llms.groq import GroqAssistant
assistant = GroqAssistant(api_key=api_key, model="llama-3.3-70b-versatile")
```

### Working with the Database

```python
from sqlmodel import Session, create_engine
from expenses_ai_agent.storage.models import Expense, ExpenseCategory, Currency
from expenses_ai_agent.storage.repo import DBExpenseRepo, DBCategoryRepo

# Create database connection
engine = create_engine("sqlite:///expenses.db")

with Session(engine) as session:
    # Create repositories
    expense_repo = DBExpenseRepo(db_url="sqlite:///expenses.db", session=session)
    category_repo = DBCategoryRepo(db_url="sqlite:///expenses.db", session=session)

    # Create a category
    food_category = ExpenseCategory.create(name="Food & Dining")
    category_repo.add(food_category)

    # Create an expense
    expense = Expense.create(
        amount=Decimal("25.50"),
        currency=Currency.USD,
        description="Lunch at restaurant",
        category=food_category
    )
    expense_repo.add(expense)

    # Query expenses
    all_expenses = expense_repo.list()
    for exp in all_expenses:
        print(exp)
```

### Currency Conversion

```python
from decimal import Decimal
from expenses_ai_agent.utils.currency import convert_currency
from expenses_ai_agent.storage.models import Currency

# Convert 100 USD to EUR
result = convert_currency(
    amount=Decimal("100.00"),
    from_currency=Currency.USD,
    to_currency=Currency.EUR
)
print(f"100 USD = {result} EUR")
```

### Datetime Formatting

```python
from expenses_ai_agent.utils.date_formatter import format_datetime

# Format ISO datetime to DD/MM/YYYY HH:MM
formatted = format_datetime(
    dt="2025-10-17T14:30:00+02:00",
    output_tz="Europe/Madrid"
)
print(formatted)  # Output: 17/10/2025 14:30
```

### Telegram Bot

The project includes a Telegram bot for mobile expense tracking with human-in-the-loop (HITL) category confirmation.

```bash
# Start the Telegram bot (requires TELEGRAM_BOT_TOKEN in .env)
expenses-telegram-bot
```

**Bot Commands:**
- `/start` - Welcome message and usage instructions
- `/help` - Show available commands
- `/cancel` - Cancel current operation

**Usage Flow:**
1. Send an expense description (e.g., "Coffee at Starbucks $5.50")
2. Bot classifies and shows suggested category with confidence
3. Confirm or override the category using inline buttons
4. Expense is saved to database with your selection

**Environment Variables:**
```bash
TELEGRAM_BOT_TOKEN=your-bot-token-from-botfather
OPENAI_API_KEY=your-openai-key
DB_URL=sqlite:///expenses.db
OPENAI_MODEL=gpt-4.1-nano-2025-04-14  # optional
```

### CLI Commands

```bash
# Classify an expense (display only)
expenses-ai-agent classify "Lunch at restaurant for $25"

# Classify and save to database
expenses-ai-agent classify "Taxi to airport 45 EUR" --db

# Greet command
expenses-ai-agent greet -g "Your Name"
```

---

## 🧩 Core Components

### LLM Assistants (`src/expenses_ai_agent/llms/`)

#### `base.py` - Assistant Protocol
Defines the contract that all LLM implementations must follow:

```python
class Assistant(Protocol):
    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse: ...
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal: ...
    def get_available_models(self) -> Sequence[str]: ...
```

#### `openai.py` - OpenAI Implementation
- Supports **structured outputs** with Pydantic models
- **Function calling** with custom tools
- **Token tracking** and cost calculation
- Support for GPT-4, GPT-5, and specialized models

#### `groq.py` - Groq Implementation
- Ultra-fast inference with Llama models
- Free tier with generous limits
- Compatible with OpenAI-style API

#### `output.py` - Response Models
Pydantic models ensuring type-safe AI responses:

```python
class ExpenseCategorizationResponse(BaseModel):
    category: str
    total_amount: Decimal
    currency: Currency
    confidence: float
    cost: Decimal
    comments: str | None = None
    timestamp: datetime
```

### Storage Layer (`src/expenses_ai_agent/storage/`)

#### `models.py` - Database Models
SQLModel entities with full type safety:

- **`ExpenseCategory`**: Expense categories (Food, Transport, etc.)
- **`Expense`**: Individual expense records with relationships
- **`Currency`**: Enum for supported currencies

#### `repo.py` - Repository Pattern
Abstract repositories with multiple implementations:

- **`CategoryRepository`**: CRUD operations for categories
- **`ExpenseRepository`**: CRUD operations for expenses
- **Implementations**:
  - `InMemoryCategoryRepository` - For testing
  - `DBCategoryRepo` - SQLite/PostgreSQL backend
  - `InMemoryExpenseRepository` - For testing
  - `DBExpenseRepo` - SQLite/PostgreSQL backend

#### `exceptions.py` - Custom Exceptions
Domain-specific exceptions for better error handling:

- `CategoryNotFoundError`
- `CategoryCreationError`
- `ExpenseNotFoundError`
- `ExpenseCreationError`

### Utilities (`src/expenses_ai_agent/utils/`)

#### `currency.py` - Currency Conversion
Real-time FX conversion using ExchangeRate-API:

```python
def convert_currency(
    amount: Decimal,
    from_currency: Currency,
    to_currency: Currency = Currency.EUR
) -> Decimal
```

#### `date_formatter.py` - Datetime Formatting
Timezone-aware datetime formatting:

```python
def format_datetime(
    dt: str,
    output_tz: str = "Europe/Madrid"
) -> str
```

### Tools (`src/expenses_ai_agent/tools/`)

Function calling schemas for LLM tool use:

- **`convert_currency_tool_schema()`**: Currency conversion tool
- **`format_datetime_tool_schema()`**: Datetime formatting tool

These enable LLMs to call Python functions during conversations.

---

## 🔬 Development

### Project Management with uv

```bash
# Add a new dependency
uv pip install package-name

# Add a development dependency
uv pip install --dev pytest-cov

# Update all dependencies
uv pip install --upgrade -r requirements.txt

# Sync dependencies from pyproject.toml
uv pip sync
```

### Code Quality Tools

```bash
# Run tests with coverage
poe test
# or manually:
pytest -vv --cov=src

# Format code (if you add black)
uv pip install black
black src/ tests/ scripts/

# Type checking (if you add mypy)
uv pip install mypy
mypy src/

# Linting (if you add ruff)
uv pip install ruff
ruff check src/
```

### Running Scripts

The `scripts/` directory contains example workflows organized by week:

```bash
# Week 1: Basic currency and workflow tests
python scripts/week1/currency_test.py
python scripts/week1/first_workflow.py

# Week 2: LLM client testing
python scripts/week2/test_openai_client.py
python scripts/week2/test_groq_client.py
python scripts/week2/test_openai_tools.py

# Week 3: Complete classification workflow
python scripts/week3/test_classification.py
python scripts/week3/test_expense_repo.py
```

### Database Management

```bash
# Create database and tables
python -c "from expenses_ai_agent.storage.models import create_db_and_tables; create_db_and_tables()"

# Or programmatically:
python -m expenses_ai_agent.storage.models
```

---

## 🧪 Testing

### Running Tests

```bash
# Run all tests with coverage (96% coverage)
pytest -vv --cov=src

# Run unit tests only (skip integration tests)
pytest -vv --cov=src -m "not integration"

# Run integration tests (requires API keys)
pytest -m integration

# Run specific test file
pytest tests/unit/test_model.py -v

# Run with coverage report
pytest --cov=src --cov-report=html

# Run tests in watch mode (requires pytest-watch)
uv pip install pytest-watch
ptw
```

### Test Structure

```
tests/
├── unit/                              # 147 unit tests
│   ├── test_bot.py                   # Telegram bot setup
│   ├── test_classification_service.py # Classification service
│   ├── test_cli.py                   # CLI commands
│   ├── test_db_repos.py              # DB repositories
│   ├── test_keyboards.py             # Inline keyboards
│   ├── test_model.py                 # SQLModel entities
│   ├── test_openai_assistant.py      # OpenAI client (mocked)
│   ├── test_preprocessing.py         # Input validation
│   ├── test_repo.py                  # Repository pattern
│   ├── test_telegram_exceptions.py   # Exception hierarchy
│   ├── test_telegram_handlers.py     # Conversation flow
│   └── test_utils.py                 # Utilities
├── integration/                       # 5 integration tests
│   ├── test_currency_integration.py  # Real ExchangeRate API
│   └── test_openai_integration.py    # Real OpenAI API
└── __init__.py
```

**Coverage:** 96% (152 total tests)

### Writing Tests

Example test with pytest and mock:

```python
import pytest
from decimal import Decimal
from expenses_ai_agent.storage.models import Expense, Currency, ExpenseCategory

def test_expense_creation():
    category = ExpenseCategory.create(name="Food & Dining")
    expense = Expense.create(
        amount=Decimal("25.50"),
        currency=Currency.USD,
        description="Lunch",
        category=category
    )

    assert expense.amount == Decimal("25.50")
    assert expense.currency == Currency.USD
    assert expense.category.name == "Food & Dining"
```

---

## 📚 API Reference

### Assistant Protocol

```python
class Assistant(Protocol):
    api_key: str
    model: str
    provider: LLMProvider
    max_response_tokens: int = 1000
    temperature: float = 0.7
    top_p: float = 1.0

    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal
    def get_available_models(self) -> Sequence[str]
```

### Repository Interfaces

```python
class CategoryRepository(ABC):
    def add(self, category: ExpenseCategory) -> None
    def update(self, category: ExpenseCategory) -> None
    def get(self, name: str) -> ExpenseCategory | None
    def delete(self, name: str) -> None
    def list(self) -> Sequence[str]

class ExpenseRepository(ABC):
    def add(self, expense: Expense) -> None
    def get(self, expense_id: int) -> Expense | None
    def search_by_dates(self, from_date: datetime, to_date: datetime) -> Sequence[Expense]
    def search_by_category(self, category: ExpenseCategory) -> Sequence[Expense]
    def update(self, expense: Expense) -> None
    def delete(self, expense_id: int) -> None
    def list(self) -> Sequence[Expense]
```

### Supported Expense Categories

1. **Food & Dining** - Groceries, restaurants, cafes, food delivery
2. **Transportation** - Gas, rideshare, parking, vehicle maintenance
3. **Utilities** - Electricity, internet, phone bills
4. **Entertainment** - Streaming, movies, hobbies, gaming
5. **Healthcare** - Medical, prescriptions, insurance
6. **Shopping** - Clothing, electronics, home goods
7. **Housing** - Rent, mortgage, home repairs
8. **Education** - Tuition, courses, books
9. **Travel** - Hotels, flights, vacation expenses
10. **Personal Care** - Salon, cosmetics, grooming
11. **Subscriptions** - Digital services, memberships
12. **Other** - Uncategorized expenses

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** with proper tests
4. **Run tests**: `pytest -vv --cov=src`
5. **Commit your changes**: `git commit -m 'Add amazing feature'`
6. **Push to the branch**: `git push origin feature/amazing-feature`
7. **Open a Pull Request**

### Development Guidelines

- Follow PEP 8 style guidelines
- Add type hints to all functions
- Write docstrings for public APIs
- Maintain test coverage above 80%
- Update documentation for new features

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 Juan José Expósito González

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## 🙏 Acknowledgments

- **OpenAI** for GPT models and excellent API documentation
- **Groq** for lightning-fast LLM inference
- **Anthropic** for Claude models
- **Astral** for creating uv, the amazing Python package manager
- **Pydantic** for data validation and settings management
- **SQLModel** for the elegant ORM layer
- **ExchangeRate-API** for reliable currency conversion

---

## 📞 Contact & Support

**Author**: Juan José Expósito González
**Email**: expositogonzalez.juanjose@gmail.com
**GitHub**: [@juanjoseexpositogonzalez](https://github.com/juanjoseexpositogonzalez)

### Issues & Questions

- 🐛 **Bug Reports**: [Open an issue](https://github.com/juanjoseexpositogonzalez/expenses_ai_agent/issues)
- 💡 **Feature Requests**: [Suggest a feature](https://github.com/juanjoseexpositogonzalez/expenses_ai_agent/issues/new)
- 💬 **Discussions**: [Join the discussion](https://github.com/juanjoseexpositogonzalez/expenses_ai_agent/discussions)

---

## 🗺️ Roadmap

- [ ] Add Anthropic Claude integration
- [ ] Implement batch expense processing
- [ ] Add web interface (FastAPI + React)
- [ ] Support for receipt image OCR
- [ ] Multi-language support
- [ ] Export to CSV/Excel
- [ ] Advanced analytics and reporting
- [ ] Budget tracking and alerts
- [ ] Mobile app integration
- [ ] GraphQL API

---

## 📊 Project Stats

![GitHub stars](https://img.shields.io/github/stars/juanjoseexpositogonzalez/expenses_ai_agent?style=social)
![GitHub forks](https://img.shields.io/github/forks/juanjoseexpositogonzalez/expenses_ai_agent?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/juanjoseexpositogonzalez/expenses_ai_agent?style=social)

---

<div align="center">

**⭐ If you find this project useful, please consider giving it a star! ⭐**

Made with ❤️ by [Juan José Expósito González](https://github.com/juanjoseexpositogonzalez)

</div>
