# Test Coverage with pytest-cov

Test coverage measures which lines of your code are executed during testing. This lesson covers achieving and maintaining the 95%+ coverage target required for the expense tracker.


## Why Coverage Matters

Code coverage is not just a metric to satisfy CI pipelines. It provides concrete benefits:

**Confidence in Changes**: When you refactor the classification service, high coverage ensures your tests catch any regressions. Without coverage, you are guessing whether your tests actually exercise the code you changed.

**Discovery of Dead Code**: Coverage reports reveal code that is never executed - either untested logic or obsolete code that can be removed.

**Documentation**: Tests serve as executable documentation. High coverage means more of your codebase has documented, verified behavior.

**Deployment Safety**: Deploying code with 50% coverage means half your application could fail in production with no warning. At 95%, only edge cases slip through.


## Understanding Coverage Metrics

pytest-cov reports several metrics:

| Metric | Meaning |
|--------|---------|
| Stmts | Total executable statements |
| Miss | Statements not executed by tests |
| Cover | Percentage of statements executed |
| Branch | Branch coverage (if/else paths taken) |

```
---------- coverage: platform linux, python 3.12 ----------
Name                                    Stmts   Miss  Cover
-----------------------------------------------------------
src/expenses_ai_agent/__init__.py           0      0   100%
src/expenses_ai_agent/llms/base.py         15      0   100%
src/expenses_ai_agent/llms/openai.py       87      4    95%
src/expenses_ai_agent/services/...         54      2    96%
-----------------------------------------------------------
TOTAL                                    1247     62    95%
```


## Running Coverage Reports

Basic coverage command:

```bash
pytest --cov=src
```

Detailed terminal report:

```bash
pytest --cov=src --cov-report=term-missing
```

This shows which specific lines are not covered:

```
Name                              Stmts   Miss  Cover   Missing
---------------------------------------------------------------
src/expenses_ai_agent/cli/app.py     45      3    93%   78-80
```

Lines 78-80 are not tested. Inspect them to determine if they need tests.


## Coverage Configuration

Add to `pyproject.toml`:

```toml
[tool.coverage.run]
source = ["src"]
branch = true
omit = [
    "*/tests/*",
    "*/__init__.py",
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
    "@abstractmethod",
]
fail_under = 95
show_missing = true
```

This configuration:
- Measures coverage for `src/` directory
- Enables branch coverage (not just line coverage)
- Excludes test files and `__init__.py`
- Excludes type-checking blocks and abstract methods
- Fails CI if coverage drops below 95%


## Branch Coverage

Line coverage can miss logic errors. Consider:

```python
def process(value):
    if value > 0:
        return "positive"
    return "non-positive"
```

A test with only `process(5)` achieves 100% line coverage but never tests the else branch. Branch coverage requires testing both paths.

```bash
pytest --cov=src --cov-branch
```


## Common Coverage Gaps

### Error Handlers

Error paths often lack tests:

```python
try:
    result = await client.classify(text)
except OpenAIError as e:
    logger.error(f"OpenAI API error: {e}")
    raise ClassificationError(str(e))  # Often untested
```

Test the error path:

```python
def test_classify_handles_openai_error(mock_client):
    mock_client.classify.side_effect = OpenAIError("API unavailable")

    with pytest.raises(ClassificationError) as exc:
        service.classify("Coffee $5")

    assert "API unavailable" in str(exc.value)
```

### Configuration Branches

Default values and environment switches:

```python
def get_model():
    return config("OPENAI_MODEL", default="gpt-4o-mini")
```

Test both with and without the environment variable set.

### Type Guards and Validation

Input validation often has untested rejection paths:

```python
def validate_amount(value: str) -> Decimal:
    if not value:
        raise ValueError("Amount required")
    try:
        return Decimal(value)
    except InvalidOperation:
        raise ValueError(f"Invalid amount: {value}")
```

Test each validation failure:

```python
def test_validate_empty_amount():
    with pytest.raises(ValueError, match="Amount required"):
        validate_amount("")

def test_validate_invalid_amount():
    with pytest.raises(ValueError, match="Invalid amount"):
        validate_amount("not-a-number")
```


## Strategies for Reaching 95%

### 1. Prioritize by Impact

Focus first on:
- Business logic (classification, persistence)
- API endpoints
- Error handling paths

Deprioritize:
- Logging statements
- Debug utilities
- One-time scripts

### 2. Test Error Paths

For every `try/except`, write a test that triggers the exception:

```python
@pytest.mark.parametrize("error,expected", [
    (ConnectionError, "Connection failed"),
    (TimeoutError, "Request timed out"),
    (ValueError, "Invalid response"),
])
def test_api_client_handles_errors(error, expected, client):
    client.http.get.side_effect = error()

    with pytest.raises(APIError) as exc:
        client.fetch_data()

    assert expected in str(exc.value)
```

### 3. Use Parameterization

Cover multiple cases with single test functions:

```python
@pytest.mark.parametrize("currency,expected", [
    ("$", "USD"),
    ("EUR", "EUR"),
    ("GBP", "GBP"),
    ("JPY", "JPY"),
])
def test_currency_normalization(currency, expected):
    result = normalize_currency(currency)
    assert result == expected
```

### 4. Mock External Dependencies

External APIs and databases should be mocked:

```python
@pytest.fixture
def mock_openai(mocker):
    return mocker.patch("expenses_ai_agent.llms.openai.OpenAI")

def test_classification_with_mock(mock_openai):
    mock_openai.return_value.chat.completions.create.return_value = ...
```

### 5. Exclude Untestable Code

Some code genuinely cannot be tested (main entrypoints, CLI setup):

```python
if __name__ == "__main__":  # pragma: no cover
    app.run()
```

Use sparingly and only for truly untestable code.


## Coverage Report Formats

Generate multiple formats for different uses:

```bash
# Terminal with missing lines
pytest --cov=src --cov-report=term-missing

# HTML report (visual, browsable)
pytest --cov=src --cov-report=html

# XML for CI tools (Codecov, SonarQube)
pytest --cov=src --cov-report=xml

# All formats at once
pytest --cov=src --cov-report=term-missing --cov-report=html --cov-report=xml
```

The HTML report is particularly useful for identifying coverage gaps visually.


## Integration with CI

Fail the build if coverage drops:

```yaml
- name: Run tests with coverage
  run: pytest --cov=src --cov-fail-under=95 --cov-report=xml

- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    files: ./coverage.xml
```

The `--cov-fail-under=95` flag causes pytest to exit with a non-zero code if coverage is insufficient.


## Coverage for the Expense Tracker

Current coverage status: approximately 94%. To reach 95%+, focus on:

1. **API error handlers** - 500 response paths
2. **Repository edge cases** - Not found exceptions
3. **Telegram handler errors** - Classification failures, persistence errors
4. **Streamlit view edge cases** - Empty data states

Each component should have tests for both success and failure paths.


## What Coverage Does Not Measure

Coverage tells you code was executed, not that it was tested correctly:

```python
def add(a, b):
    return a + b

def test_add():
    add(1, 2)  # 100% coverage, but no assertions!
```

This test achieves full coverage but verifies nothing. Always:
- Assert expected outcomes
- Test edge cases
- Verify error handling


## Measuring Coverage Locally

Before pushing, verify coverage meets the threshold:

```bash
# Quick check
pytest --cov=src --cov-fail-under=95

# Detailed report to find gaps
pytest --cov=src --cov-report=term-missing
```

Fix gaps before they reach CI.


## Further Reading

- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py Configuration](https://coverage.readthedocs.io/en/latest/config.html)
- [Martin Fowler: Test Coverage](https://martinfowler.com/bliki/TestCoverage.html)
