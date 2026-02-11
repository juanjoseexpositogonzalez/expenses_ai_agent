# Input Preprocessing

Input preprocessing is the first line of defense between user input and your LLM. It validates, sanitizes, and normalizes text before classification. Without preprocessing, malicious or malformed input can cause errors, security vulnerabilities, or wasted API calls.


## Why Input Preprocessing Exists

User input from Telegram is unpredictable. Consider these scenarios:

```python
# Too short - waste of API call
"ab"

# Too long - might exceed token limits
"a" * 5000

# Malicious - XSS attempt
"Coffee <script>alert('xss')</script>"

# Currency symbols that need normalization
"Lunch for 15 EUR" vs "Lunch for 15 euros"

# Missing amount - valid but should warn
"Coffee at the cafe"
```

Preprocessing catches these issues before they reach the LLM, saving API costs and preventing security issues.


## The PreprocessingResult Dataclass

The preprocessor returns a structured result instead of raising exceptions. This allows the caller to decide how to handle warnings versus errors:

```python
from dataclasses import dataclass, field


@dataclass
class PreprocessingResult:
    """Result of input preprocessing."""

    text: str
    is_valid: bool
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
```

**Design decision:** Using a dataclass instead of raising exceptions makes testing easier and allows the bot to show helpful error messages rather than crashing.


## Validation Rules

### Length Validation

Input must be between 3 and 500 characters:

```python
MIN_LENGTH = 3
MAX_LENGTH = 500

def _validate_length(self, text: str) -> str | None:
    """Return error message if length invalid, None if valid."""
    if len(text) < MIN_LENGTH:
        return f"Input too short (minimum {MIN_LENGTH} characters)"
    if len(text) > MAX_LENGTH:
        return f"Input too long (maximum {MAX_LENGTH} characters)"
    return None
```

**Why these limits?**
- 3 characters: Minimum for meaningful input ("gas", "tea")
- 500 characters: Practical limit to avoid token waste


### XSS Pattern Detection

Telegram messages should not contain HTML/JavaScript patterns:

```python
import re

XSS_PATTERNS = [
    re.compile(r"<script", re.IGNORECASE),
    re.compile(r"javascript:", re.IGNORECASE),
    re.compile(r"onerror\s*=", re.IGNORECASE),
    re.compile(r"onload\s*=", re.IGNORECASE),
]

def _detect_xss(self, text: str) -> bool:
    """Return True if XSS pattern detected."""
    return any(pattern.search(text) for pattern in XSS_PATTERNS)
```

**Why check for XSS in a bot?**
Even though Telegram escapes HTML, the expense description might be:
1. Displayed in a web dashboard (Week 5)
2. Stored in a database that serves web content
3. Included in reports or exports


### Currency Symbol Normalization

Users type currency in many ways. Normalize to standard codes:

```python
CURRENCY_SYMBOLS = {
    "$": "USD",
    "EUR": "EUR",
    "GBP": "GBP",
    "JPY": "JPY",
    "CHF": "CHF",
}

def _normalize_currency(self, text: str) -> str:
    """Normalize currency symbols to codes."""
    # Replace common symbols with codes
    result = text
    for symbol, code in self._symbol_to_code.items():
        result = result.replace(symbol, code)
    return result
```

**Note:** The LLM can handle most currency formats, but normalization ensures consistency in the database.


### Missing Amount Warning

Expenses without amounts are valid but suspicious:

```python
import re

AMOUNT_PATTERN = re.compile(r"\d+([.,]\d+)?")

def _check_amount(self, text: str) -> str | None:
    """Return warning if no amount detected."""
    if not AMOUNT_PATTERN.search(text):
        return "No amount detected in input"
    return None
```

This produces a warning, not an error. The user might add the amount later, or the LLM might extract it from context.


## The InputPreprocessor Class

Combining all validations:

```python
class InputPreprocessor:
    """Validates and normalizes user input before classification."""

    def preprocess(self, text: str) -> PreprocessingResult:
        """Validate and normalize input text."""
        # Strip whitespace
        cleaned = text.strip()

        # Check length
        if error := self._validate_length(cleaned):
            return PreprocessingResult(
                text=cleaned,
                is_valid=False,
                error=error,
            )

        # Check XSS
        if self._detect_xss(cleaned):
            return PreprocessingResult(
                text=cleaned,
                is_valid=False,
                error="Invalid input detected",
            )

        # Normalize currency
        normalized = self._normalize_currency(cleaned)

        # Check for amount (warning only)
        warnings = []
        if warning := self._check_amount(normalized):
            warnings.append(warning)

        return PreprocessingResult(
            text=normalized,
            is_valid=True,
            warnings=warnings,
        )
```


## Python Comparison: Validation Approaches

| Approach | Pros | Cons |
|----------|------|------|
| Raise exceptions | Simple, Pythonic | Caller must catch each exception type |
| Return tuple `(valid, text, error)` | Simple | No room for warnings |
| Return dataclass | Structured, extensible | Slightly more complex |

The dataclass approach works best when you need both errors (block) and warnings (inform).


## Preprocessing in Our Bot

The Telegram handler uses preprocessing before classification:

```python
async def handle_expense_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle incoming expense text."""
    # Preprocess input
    result = self._preprocessor.preprocess(update.message.text)

    if not result.is_valid:
        await update.message.reply_text(f"Invalid input: {result.error}")
        return ConversationHandler.END

    # Show warnings but continue
    if result.warnings:
        await update.message.reply_text(f"Note: {', '.join(result.warnings)}")

    # Classify the preprocessed text
    classification = self._service.classify(result.text)
    ...
```


## Testing Preprocessing

Preprocessing is highly testable because it has no external dependencies:

```python
def test_valid_input_passes(self):
    preprocessor = InputPreprocessor()
    result = preprocessor.preprocess("Coffee at Starbucks $5.50")

    assert result.is_valid is True
    assert result.error is None


def test_xss_pattern_rejected(self):
    preprocessor = InputPreprocessor()
    result = preprocessor.preprocess("Coffee <script>alert('xss')</script>")

    assert result.is_valid is False
    assert "invalid" in result.error.lower()
```


## Further Reading

- [OWASP XSS Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [Python dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [re module documentation](https://docs.python.org/3/library/re.html)
