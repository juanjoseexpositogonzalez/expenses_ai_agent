import pytest

from expenses_ai_agent.services.preprocessing import (
    InputPreprocessor,
    PreprocessingResult,
)


@pytest.fixture()
def preprocessor() -> InputPreprocessor:
    return InputPreprocessor()


# ------------------------------------------------------------------
# Valid input
# ------------------------------------------------------------------


def test_valid_input_with_amount(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("Coffee at Starbucks $5.50")

    assert result.is_valid is True
    assert len(result.validation_errors) == 0
    assert "Coffee at Starbucks" in result.cleaned_text


def test_valid_input_no_warnings_when_amount_present(
    preprocessor: InputPreprocessor,
) -> None:
    result = preprocessor.preprocess("Groceries 42 USD")

    assert result.is_valid is True
    assert len(result.warnings) == 0


# ------------------------------------------------------------------
# Empty / blank input
# ------------------------------------------------------------------


def test_empty_string(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("")

    assert result.is_valid is False
    assert any("empty" in e.lower() for e in result.validation_errors)


def test_whitespace_only(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("   ")

    assert result.is_valid is False
    assert any("empty" in e.lower() for e in result.validation_errors)


# ------------------------------------------------------------------
# Length validation
# ------------------------------------------------------------------


def test_too_short(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("ab")

    assert result.is_valid is False
    assert any("short" in e.lower() for e in result.validation_errors)


def test_too_long(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("x" * 600)

    assert result.is_valid is False
    assert any("long" in e.lower() for e in result.validation_errors)


# ------------------------------------------------------------------
# Suspicious patterns
# ------------------------------------------------------------------


def test_script_tag_blocked(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("<script>alert('xss')</script>")

    assert result.is_valid is False
    assert any("suspicious" in e.lower() for e in result.validation_errors)


def test_javascript_protocol_blocked(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("javascript:void(0) expense $10")

    assert result.is_valid is False


# ------------------------------------------------------------------
# Cleaning
# ------------------------------------------------------------------


def test_whitespace_collapsed(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("Coffee    at    Starbucks   $5.50")

    assert result.is_valid is True
    assert "  " not in result.cleaned_text
    assert "Coffee at Starbucks" in result.cleaned_text


def test_leading_trailing_whitespace_stripped(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("  Coffee $5.50  ")

    assert result.is_valid is True
    assert result.cleaned_text == "Coffee $5.50"


# ------------------------------------------------------------------
# Currency normalization
# ------------------------------------------------------------------


def test_euro_symbol_normalized(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("Coffee \u20ac5.50")

    assert result.is_valid is True
    assert "EUR" in result.cleaned_text
    assert "\u20ac" not in result.cleaned_text


def test_pound_symbol_normalized(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("Lunch \u00a315.00")

    assert result.is_valid is True
    assert "GBP" in result.cleaned_text


def test_yen_symbol_normalized(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("Sushi \u00a52000")

    assert result.is_valid is True
    assert "JPY" in result.cleaned_text


# ------------------------------------------------------------------
# Warnings
# ------------------------------------------------------------------


def test_missing_amount_warning(preprocessor: InputPreprocessor) -> None:
    result = preprocessor.preprocess("Coffee at Starbucks")

    assert result.is_valid is True
    assert len(result.warnings) > 0
    assert any("amount" in w.lower() for w in result.warnings)


# ------------------------------------------------------------------
# Result dataclass
# ------------------------------------------------------------------


def test_preprocessing_result_defaults() -> None:
    result = PreprocessingResult(cleaned_text="test", is_valid=True)

    assert result.validation_errors == []
    assert result.warnings == []
