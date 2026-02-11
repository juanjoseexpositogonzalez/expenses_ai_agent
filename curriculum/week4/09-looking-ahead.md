# Looking Ahead: Week 5

Congratulations on completing Week 4! You now have a working Telegram bot with human-in-the-loop category confirmation.


## What's Next

In Week 5, you will build the REST API and web dashboard:

- **FastAPI REST API** - RESTful endpoints for expense management
- **Dependency Injection** - Clean service layer integration
- **Streamlit Dashboard** - Visual expense analytics
- **Data Visualization** - Charts with Plotly


## How Week 4 Connects to Week 5

Your components will be reused by the REST API:

```
Week 4 (Telegram)          Week 5 (API + Dashboard)
-----------------          ----------------------
InputPreprocessor    -->   Used by API validation
ClassificationService -->  Injected into FastAPI
DBExpenseRepo        -->   Powers API endpoints
DBCategoryRepo       -->   Category listing endpoint


     Telegram Bot (Week 4)
            |
            v
    +-------------------+
    | Classification-   |  <-- Shared service
    | Service           |
    +-------------------+
            ^
            |
     FastAPI API (Week 5)
            ^
            |
     Streamlit Dashboard (Week 5)
```


## Week 5 Architecture Preview

```
+------------------------------------------------------------------+
|                    WEEK 5: API + DASHBOARD                        |
+------------------------------------------------------------------+

    HTTP Request: POST /api/v1/expenses/classify
                              |
                              v
                    +-------------------+
                    | FastAPI Router    |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | Dependency        |
                    | Injection         |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | Classification-   |  <- Week 3 service
                    | Service           |
                    +-------------------+
                              |
                              v
                    +-------------------+
                    | JSON Response     |
                    +-------------------+

    Streamlit Dashboard
            |
            v
    +-------------------+
    | API Client        |  <- Calls FastAPI
    +-------------------+
            |
            v
    +-------------------+
    | Plotly Charts     |
    +-------------------+
```


## The Multi-Interface Pattern

After Week 5, you will have three interfaces to the same classification service:

| Interface | Use Case | Input Method |
|-----------|----------|--------------|
| CLI | Developer testing | Command line |
| Telegram Bot | Mobile users | Chat messages |
| REST API | Web/mobile apps | HTTP requests |
| Streamlit | Data analysis | Web browser |

All four share the same ClassificationService, repositories, and LLM integration.


## Prepare for Week 5

Before starting Week 5, make sure you:

1. Have all 25 Week 4 tests passing
2. Understand FastAPI basics (routes, dependencies)
3. Have Streamlit installed: `pip install streamlit`

See you in Week 5!
