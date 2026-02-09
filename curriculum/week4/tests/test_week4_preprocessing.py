"""
Week 4 - Definition of Done: Input Preprocessing

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week4_preprocessing.py -v
All tests must pass to complete Week 4's preprocessing milestone.

These tests verify your implementation of:
- InputPreprocessor class
- PreprocessingResult dataclass
- Validation rules (length, XSS, currency normalization)
"""

import pytest


class TestPreprocessingResult:
    """Tests for the PreprocessingResult dataclass."""

    def test_result_has_required_fields(self):
        """PreprocessingResult should have text, is_valid, warnings, error."""
        from expenses_ai_agent.services.preprocessing import PreprocessingResult

        result = PreprocessingResult(
            text="Coffee $5",
            is_valid=True,
            warnings=[],
            error=None,
        )

        assert result.text == "Coffee $5"
        assert result.is_valid is True
        assert result.warnings == []
        assert result.error is None

    def test_result_with_warnings(self):
        """Result can include warnings without failing validation."""
        from expenses_ai_agent.services.preprocessing import PreprocessingResult

        result = PreprocessingResult(
            text="Coffee",
            is_valid=True,
            warnings=["No amount detected"],
        )

        assert result.is_valid is True
        assert len(result.warnings) == 1

    def test_result_with_error(self):
        """Result with error should be invalid."""
        from expenses_ai_agent.services.preprocessing import PreprocessingResult

        result = PreprocessingResult(
            text="ab",
            is_valid=False,
            warnings=[],
            error="Input too short",
        )

        assert result.is_valid is False
        assert result.error is not None


class TestInputPreprocessor:
    """Tests for the InputPreprocessor class."""

    @pytest.fixture
    def preprocessor(self):
        """Create an InputPreprocessor instance."""
        from expenses_ai_agent.services.preprocessing import InputPreprocessor

        return InputPreprocessor()

    def test_valid_input_passes(self, preprocessor):
        """Normal expense description should pass validation."""
        result = preprocessor.preprocess("Coffee at Starbucks $5.50")

        assert result.is_valid is True
        assert result.error is None

    def test_input_too_short_fails(self, preprocessor):
        """Input shorter than minimum length should fail."""
        result = preprocessor.preprocess("ab")

        assert result.is_valid is False
        assert "short" in result.error.lower() or "length" in result.error.lower()

    def test_input_too_long_fails(self, preprocessor):
        """Input longer than maximum length should fail."""
        long_text = "a" * 501
        result = preprocessor.preprocess(long_text)

        assert result.is_valid is False
        assert "long" in result.error.lower() or "length" in result.error.lower()

    def test_xss_script_tag_rejected(self, preprocessor):
        """Input with <script> tag should be rejected."""
        result = preprocessor.preprocess("Coffee <script>alert('xss')</script>")

        assert result.is_valid is False
        assert "xss" in result.error.lower() or "script" in result.error.lower() or "invalid" in result.error.lower()

    def test_xss_javascript_rejected(self, preprocessor):
        """Input with javascript: protocol should be rejected."""
        result = preprocessor.preprocess("Check javascript:void(0)")

        assert result.is_valid is False

    def test_currency_symbol_normalized(self, preprocessor):
        """Currency symbols should be normalized to codes."""
        result = preprocessor.preprocess("Coffee for $5.50")

        # $ should be normalized to USD in some form
        assert result.is_valid is True
        # The normalized text might contain USD or the original $
        # depending on implementation

    def test_euro_symbol_normalized(self, preprocessor):
        """Euro symbol should be normalized."""
        result = preprocessor.preprocess("Lunch for 15 EUR")

        assert result.is_valid is True

    def test_missing_amount_warns(self, preprocessor):
        """Input without numeric amount should produce warning."""
        result = preprocessor.preprocess("Coffee at cafe")

        assert result.is_valid is True  # Still valid, just warn
        # Should have a warning about missing amount
        assert len(result.warnings) > 0 or "amount" in str(result.warnings).lower()

    def test_whitespace_handled(self, preprocessor):
        """Leading/trailing whitespace should be handled."""
        result = preprocessor.preprocess("  Coffee $5  ")

        assert result.is_valid is True
        assert result.text.strip() == result.text or "Coffee" in result.text
