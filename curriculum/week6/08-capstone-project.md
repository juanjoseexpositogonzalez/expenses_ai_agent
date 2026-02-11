# Capstone Project Ideas

You have built a complete AI-powered expense classification system over six weeks. The foundation is solid: clean architecture, comprehensive tests, and production-ready deployment. This document presents capstone project ideas for extending your system beyond the curriculum.


## Why Capstone Projects Matter

Building features independently solidifies your learning. The curriculum guided you step by step, but real-world development requires making architectural decisions, researching APIs, and debugging unforeseen issues. A capstone project exercises these skills.

Choose one or more projects based on your interests and time availability. Each project description includes objectives, technical approach, and extension ideas.


## Project 1: Receipt Image Processing

### Overview

Add OCR (Optical Character Recognition) to extract expense data from receipt photos. Users send a photo to the Telegram bot, and the system extracts vendor name, amount, and date automatically.

### Objectives

- Integrate an OCR service (Tesseract, Google Vision, or AWS Textract)
- Parse unstructured OCR output to extract expense data
- Handle image preprocessing (rotation, contrast enhancement)
- Extend the Telegram bot to accept photos

### Technical Approach

```python
# New handler in telegram/handlers.py
async def handle_receipt_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Download the photo
    photo = await update.message.photo[-1].get_file()
    image_bytes = await photo.download_as_bytearray()

    # Send to OCR service
    ocr_result = ocr_service.extract_text(image_bytes)

    # Parse the OCR result
    expense_data = receipt_parser.parse(ocr_result)

    # Classify using existing pipeline
    result = classification_service.classify(expense_data.description)
```

### Extension Ideas

- Support multiple receipt formats (grocery, restaurant, gas station)
- Store receipt images alongside expense records
- Implement duplicate detection (same receipt submitted twice)


## Project 2: Budget Alerts and Goals

### Overview

Allow users to set monthly budgets per category and receive alerts when approaching or exceeding limits.

### Objectives

- Create budget model and repository
- Implement budget check logic in classification service
- Send proactive alerts via Telegram when thresholds are crossed
- Add budget management to Streamlit dashboard

### Technical Approach

```python
# New model in storage/models.py
class Budget(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    telegram_user_id: int = Field(index=True)
    category: str
    monthly_limit: Decimal
    alert_threshold: float = Field(default=0.8)  # Alert at 80%

# Budget check after classification
def check_budget(user_id: int, category: str, amount: Decimal) -> BudgetStatus:
    budget = budget_repo.get_by_user_and_category(user_id, category)
    if budget is None:
        return BudgetStatus(within_budget=True)

    month_total = expense_repo.get_category_total_for_month(user_id, category)
    new_total = month_total + amount

    if new_total > budget.monthly_limit:
        return BudgetStatus(exceeded=True, over_by=new_total - budget.monthly_limit)
    elif new_total > budget.monthly_limit * budget.alert_threshold:
        return BudgetStatus(approaching=True, percent_used=float(new_total / budget.monthly_limit))

    return BudgetStatus(within_budget=True, percent_used=float(new_total / budget.monthly_limit))
```

### Extension Ideas

- Weekly budget summaries sent via Telegram
- Rollover unused budget to next month
- Shared family budgets


## Project 3: Natural Language Queries

### Overview

Enable users to ask questions about their expenses in natural language: "How much did I spend on food last month?" or "What was my biggest expense this week?"

### Objectives

- Integrate LLM for intent classification (query vs. expense)
- Parse date ranges from natural language
- Generate SQL or repository calls from parsed intent
- Return human-readable responses

### Technical Approach

```python
# Intent classification using structured output
class QueryIntent(BaseModel):
    intent: Literal["query", "expense"]
    query_type: Literal["total", "list", "comparison", "trend"] | None
    category: str | None
    date_range: DateRange | None

# Handle in Telegram bot
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Classify intent
    intent = await llm.parse_intent(text)

    if intent.intent == "expense":
        # Existing flow
        return await handle_expense_text(update, context)
    else:
        # Query flow
        result = query_service.execute(intent, user_id)
        await update.message.reply_text(result.format_response())
```

### Extension Ideas

- Support comparative queries ("Do I spend more on food or transport?")
- Trend analysis ("How has my spending changed over time?")
- Predictive queries ("At this rate, will I exceed my budget?")


## Project 4: Multi-LLM Provider Support

### Overview

Add support for multiple LLM providers (Anthropic Claude, Google Gemini, local Ollama models) with runtime switching based on cost, performance, or availability.

### Objectives

- Implement additional providers following the Assistant protocol
- Create provider selection logic (fallback, round-robin, cost-based)
- Add provider metrics (latency, cost, success rate)
- Enable user preference for provider

### Technical Approach

```python
# New provider implementation
class AnthropicAssistant:
    def __init__(self, model: str = "claude-3-haiku-20240307"):
        self.client = anthropic.Anthropic()
        self.model = model

    def completion(
        self,
        messages: MESSAGES,
        response_format: type[BaseModel],
    ) -> ExpenseCategorizationResponse:
        response = self.client.messages.create(
            model=self.model,
            messages=messages,
            # Parse structured output
        )
        return parse_response(response)

# Provider selector
class ProviderSelector:
    def __init__(self, providers: list[Assistant], strategy: str = "fallback"):
        self.providers = providers
        self.strategy = strategy

    def get_provider(self) -> Assistant:
        if self.strategy == "fallback":
            return self._get_first_available()
        elif self.strategy == "cheapest":
            return self._get_by_cost()
        elif self.strategy == "round_robin":
            return self._get_next()
```

### Extension Ideas

- A/B testing between providers
- Automatic fallback on rate limits or errors
- Cost optimization with caching for identical queries


## Project 5: Export and Reporting

### Overview

Add data export capabilities: CSV downloads, PDF reports, and integration with accounting software.

### Objectives

- Generate CSV exports of expenses
- Create PDF reports with charts
- Implement scheduled email reports
- Add export endpoints to API

### Technical Approach

```python
# Export service
class ExportService:
    def export_csv(self, user_id: int, date_range: DateRange) -> bytes:
        expenses = expense_repo.list_by_user_and_date(user_id, date_range)

        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=["date", "category", "amount", "currency", "description"])
        writer.writeheader()
        for expense in expenses:
            writer.writerow(expense.to_dict())

        return output.getvalue().encode()

    def generate_pdf_report(self, user_id: int, month: date) -> bytes:
        summary = analytics_service.get_monthly_summary(user_id, month)

        # Generate charts
        category_chart = self._create_pie_chart(summary.category_totals)
        trend_chart = self._create_line_chart(summary.daily_totals)

        # Build PDF
        return pdf_builder.build(summary, [category_chart, trend_chart])
```

### Extension Ideas

- Scheduled weekly/monthly reports via email
- Integration with QuickBooks or Xero
- Tax-ready annual summaries


## Project 6: Collaborative Expense Tracking

### Overview

Enable shared expense tracking for families, roommates, or teams. Users can create groups, share expenses, and split costs.

### Objectives

- Implement group and membership models
- Add expense sharing and splitting logic
- Create settlement/balance calculations
- Build group management in Telegram bot

### Technical Approach

```python
# Group models
class ExpenseGroup(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    created_by: int

class GroupMembership(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    group_id: int = Field(foreign_key="expensegroup.id")
    user_id: int
    share_ratio: Decimal = Field(default=Decimal("1.0"))

# Splitting logic
class SplitCalculator:
    def calculate_balances(self, group_id: int) -> dict[int, Decimal]:
        expenses = expense_repo.list_by_group(group_id)
        memberships = membership_repo.list_by_group(group_id)

        # Calculate each member's share and payments
        balances = {}
        for member in memberships:
            paid = sum(e.amount for e in expenses if e.paid_by == member.user_id)
            owed = sum(self._calculate_share(e, member) for e in expenses)
            balances[member.user_id] = paid - owed

        return balances
```

### Extension Ideas

- Settle debts via payment links
- Recurring shared expenses (rent, utilities)
- Group expense categories and budgets


## Evaluation Criteria

When working on a capstone project, evaluate your implementation against these criteria:

| Criterion | Points | Description |
|-----------|--------|-------------|
| Functionality | 40 | Does it work as intended? |
| Code Quality | 20 | Clean architecture, proper patterns, type hints |
| Test Coverage | 20 | Comprehensive tests, including edge cases |
| Documentation | 10 | Clear README, docstrings, usage examples |
| User Experience | 10 | Error messages, input validation, helpful responses |


## Getting Started

1. **Choose a project** based on your interests and available time
2. **Define scope** - start with minimum viable functionality
3. **Design first** - sketch the architecture before coding
4. **Test incrementally** - write tests as you implement
5. **Document as you go** - update README with new features

Remember: a completed small feature is more valuable than an incomplete ambitious one. Start simple and extend.


## Submitting Your Capstone

If you complete a capstone project:

1. Create a branch named `capstone/your-feature-name`
2. Implement the feature with tests
3. Update README with feature documentation
4. Create a pull request with summary of changes
5. Share your work with the cohort community

Your capstone demonstrates real-world development skills beyond the curriculum.
