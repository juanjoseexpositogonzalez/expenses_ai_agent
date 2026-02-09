# Expense AI Agent - Cohort Curriculum

Welcome to the Expense AI Agent Cohort! This 6-week curriculum teaches you to build a production-ready AI-powered expense tracking system using Python.

## Overview

You will build an intelligent expense classification agent that:

- Classifies expenses into 12 categories using LLMs (OpenAI/Groq)
- Provides multiple interfaces: CLI, Telegram bot, REST API, Web dashboard
- Implements human-in-the-loop (HITL) for category confirmation
- Persists data to SQLite with the Repository pattern
- Deploys with Docker and CI/CD

## Curriculum Structure

```
curriculum/
+-- README.md              # This file
+-- week1/
|   +-- README.md          # Week 1 overview and build guide
|   +-- tests/
|       +-- test_week1_models.py
|       +-- test_week1_repos.py
+-- week2/
|   +-- README.md
|   +-- tests/
|       +-- test_week2_llm.py
|       +-- test_week2_utils.py
+-- week3/
|   +-- README.md
|   +-- tests/
|       +-- test_week3_prompts.py
|       +-- test_week3_service.py
|       +-- test_week3_db_repos.py
|       +-- test_week3_cli.py
+-- week4/
|   +-- README.md
|   +-- tests/
|       +-- test_week4_preprocessing.py
|       +-- test_week4_keyboards.py
|       +-- test_week4_handlers.py
+-- week5/
|   +-- README.md
|   +-- tests/
|       +-- test_week5_api.py
|       +-- test_week5_streamlit.py
+-- week6/
    +-- README.md
    +-- tests/
        +-- test_week6_docker.py
        +-- test_week6_coverage.py
```

## Weekly Progression

| Week | Topic | Key Concepts |
|------|-------|--------------|
| 1 | Scaffolding | Project setup, SQLModel, Repository pattern |
| 2 | Assistant Setup | LLM Protocol, OpenAI client, tools, Pydantic |
| 3 | Tools for the Agent | Classification service, prompts, CLI |
| 4 | Telegram Integration | Bot handlers, HITL, preprocessing |
| 5 | Web Interface | FastAPI, Streamlit, dependency injection |
| 6 | Deploy + Docs | Docker, CI/CD, documentation |


## Test-Driven Coaching (TDC)

This curriculum uses **Test-Driven Coaching** methodology:

```
+--------------------------------------------------------------+
|                   Test-Driven Coaching (TDC)                 |
|                                                              |
|   curriculum provides      ->    student receives            |
|   +------------------+           +------------------+        |
|   |  Complete pytest  |           |  Test files       |        |
|   |  test files       |---------->|  (all RED)        |        |
|   +------------------+           +--------+---------+        |
|                                           |                  |
|                                  student writes              |
|                                  production code             |
|                                           |                  |
|                                  +--------v---------+        |
|                                  |  Tests pass       |        |
|                                  |  (all GREEN)      |        |
|                                  +------------------+        |
|                                                              |
|   "Tests are the assignment. Code is the answer."           |
+--------------------------------------------------------------+
```

**How it works:**
1. Each week provides complete, runnable pytest files
2. You write production code to make those tests pass
3. "Done" = all tests green (`pytest` exits 0)
4. You NEVER write tests - you write the code UNDER test


## Weekly Workflow

For each week:

1. **Read** the week's README.md for concepts and build guide
2. **Copy** test files from `curriculum/weekN/tests/` to your `tests/unit/`
3. **Run** `pytest tests/unit/test_weekN_*.py -v` - see all RED
4. **Write** production code until all GREEN
5. **Verify** with `ruff format --check .` and `ruff check .`
6. **Done** when all tests pass and no linting errors


## Prerequisites

- Python 3.12+
- UV package manager
- Git
- OpenAI API key
- (Week 4+) Telegram Bot Token


## Getting Started

```bash
# Clone and setup
git clone <your-repo>
cd expenses_ai_agent

# Install dependencies
uv pip install -e ".[dev]"

# Copy .env.example to .env and add your API keys
cp .env.example .env

# Start with Week 1
cp curriculum/week1/tests/*.py tests/unit/
pytest tests/unit/test_week1_*.py -v

# All tests should be RED - now write code to make them GREEN!
```


## Test Counts by Week

| Week | Test Files | Test Count | Focus Area |
|------|------------|------------|------------|
| 1 | 2 | 26 | Models, In-Memory Repos |
| 2 | 2 | 18 | LLM Protocol, Utils |
| 3 | 4 | 30 | Service, DB Repos, CLI |
| 4 | 3 | 28 | Preprocessing, Telegram |
| 5 | 2 | 24 | FastAPI, Streamlit |
| 6 | 2 | 10 | Docker, Coverage |
| **Total** | **15** | **136** | |


## Quality Commands

```bash
# Run all curriculum tests
pytest tests/unit/test_week*.py -v

# Check formatting
ruff format --check .

# Check linting
ruff check .

# Run with coverage (Week 6 target: 95%+)
pytest --cov=src --cov-fail-under=95
```


## Architecture Overview

```
+-------------------------------------------------------------------------+
|                    EXPENSE AI AGENT ARCHITECTURE                         |
+-------------------------------------------------------------------------+

    CLI (Typer+Rich) --+
                       |
    Telegram Bot ------+---> Services Layer ---> LLM Assistants ---> Tools
                       |           |
    FastAPI REST API --+           |
           ^                       v
    Streamlit Dashboard     Storage (Repository Pattern)
                                   |
                                   v
                               SQLite DB
```


## Key Patterns You Will Learn

1. **Protocol Pattern** - Structural typing for LLM providers
2. **Repository Pattern** - Abstract data access
3. **Service Layer** - Business logic encapsulation
4. **Dependency Injection** - Testable, modular code
5. **Human-in-the-Loop (HITL)** - AI + human collaboration
6. **Conversation Handlers** - Multi-step bot interactions


## Support

- Read the week's README carefully - it contains all the guidance you need
- Run tests frequently - they tell you exactly what to build
- Use `--help` on CLI commands
- Check FastAPI docs at http://localhost:8000/docs


## License

This curriculum is provided for educational purposes as part of the Expense AI Agent project.

---

**Remember**: Tests are the assignment. Code is the answer. Happy coding!
