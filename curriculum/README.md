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

Each week contains multiple lesson files:

```
curriculum/
+-- README.md                      # This file
+-- agentic_ai_sales_strategy.md   # Sales enablement guide
+-- week1/
|   +-- 01-welcome.md              # Week overview, objectives
|   +-- 02-join-the-community.md   # Community onboarding
|   +-- 03-environment-setup.md    # Dev environment setup
|   +-- 04-repository-pattern.md   # Concept: Repository pattern
|   +-- 05-sqlmodel-entities.md    # Concept: SQLModel
|   +-- 06-python-enums.md         # Concept: StrEnum
|   +-- 07-week1-implementation.md # Implementation with tests
|   +-- 08-success-criteria.md     # Validation checklist
|   +-- 09-looking-ahead.md        # Preview of next week
+-- week2/
|   +-- 01-welcome.md
|   +-- ... (9 lesson files)
+-- week3/
|   +-- ... (9 lesson files)
+-- week4/
|   +-- ... (9 lesson files)
+-- week5/
|   +-- ... (9 lesson files)
+-- week6/
    +-- ... (9 lesson files)
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
1. Each week's implementation lesson contains complete, runnable pytest code
2. You copy the test code to your `tests/unit/` directory
3. You write production code to make those tests pass
4. "Done" = all tests green (`pytest` exits 0)


## Weekly Workflow

For each week:

1. **Read** the welcome file (`01-welcome.md`) for the big picture
2. **Study** concept lessons (`02-*.md` through `06-*.md`)
3. **Copy** tests from the implementation lesson to your `tests/unit/`
4. **Run** `pytest tests/unit/test_weekN.py -v` - see all RED
5. **Write** production code until all GREEN
6. **Verify** with `ruff format --check .` and `ruff check .`
7. **Review** success criteria before moving on


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
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Copy .env.example to .env and add your API keys
cp .env.example .env

# Start with Week 1
# Read 01-welcome.md, then copy tests from 07-week1-implementation.md
pytest tests/unit/test_week1.py -v

# All tests should be RED - now write code to make them GREEN!
```


## Test Counts by Week

| Week | Test Count | Focus Area |
|------|------------|------------|
| 1 | 26 | Models, In-Memory Repos |
| 2 | 18 | LLM Protocol, Utils |
| 3 | 30 | Service, DB Repos, CLI |
| 4 | 28 | Preprocessing, Telegram |
| 5 | 24 | FastAPI, Streamlit |
| 6 | 10 | Docker, Coverage |
| **Total** | **136** | |


## Quality Commands

```bash
# Run all tests
pytest tests/unit/ -v

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


## Lesson Types

Each week contains three types of lessons:

| Type | Purpose | Key Sections |
|------|---------|--------------|
| Welcome | Week introduction | Mental Model Shift, What Success Looks Like, Milestones |
| Concept | Teach a pattern | Why It Exists, Core Usage, Python Comparison, Further Reading |
| Implementation | Hands-on coding | Test Suite, Implementation Strategy, Step Hints |


## Support

- Read the week's lessons carefully - they contain all the guidance you need
- Run tests frequently - they tell you exactly what to build
- Join the cohort community for help and discussion
- Use `--help` on CLI commands
- Check FastAPI docs at http://localhost:8000/docs


## License

This curriculum is provided for educational purposes as part of the Expense AI Agent project.

---

**Remember**: Tests are the assignment. Code is the answer. Happy coding!
