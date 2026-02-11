import logging
import re
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class PreprocessingResult:
    """Result of input preprocessing."""

    cleaned_text: str
    is_valid: bool
    validation_errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class InputPreprocessor:
    """Preprocess and validate user expense descriptions."""

    MIN_LENGTH = 3
    MAX_LENGTH = 500
    SUSPICIOUS_PATTERNS = [
        r"<script",
        r"javascript:",
        r"onerror=",
    ]

    def preprocess(self, text: str) -> PreprocessingResult:
        """Clean and validate expense text.

        Args:
            text: Raw user input.

        Returns:
            PreprocessingResult with cleaned text and validation status.
        """
        errors: list[str] = []
        warnings: list[str] = []

        if not text or not text.strip():
            errors.append("Input cannot be empty")
            return PreprocessingResult(
                cleaned_text="",
                is_valid=False,
                validation_errors=errors,
                warnings=warnings,
            )

        stripped = text.strip()

        if len(stripped) < self.MIN_LENGTH:
            errors.append(f"Input too short (min {self.MIN_LENGTH} characters)")

        if len(stripped) > self.MAX_LENGTH:
            errors.append(f"Input too long (max {self.MAX_LENGTH} characters)")

        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, stripped, re.IGNORECASE):
                errors.append("Suspicious input detected")
                logger.warning("Blocked suspicious input: %s", stripped[:50])

        cleaned = re.sub(r"\s+", " ", stripped)
        cleaned = self._normalize_currency(cleaned)

        if not re.search(r"\d", cleaned):
            warnings.append("No amount detected - expense amount may be missing")

        is_valid = len(errors) == 0

        return PreprocessingResult(
            cleaned_text=cleaned,
            is_valid=is_valid,
            validation_errors=errors,
            warnings=warnings,
        )

    def _normalize_currency(self, text: str) -> str:
        """Normalize common currency symbols to their ISO codes."""
        replacements = {
            "\u20ac": "EUR",
            "\u00a3": "GBP",
            "\u00a5": "JPY",
        }
        for symbol, code in replacements.items():
            text = text.replace(symbol, f" {code} ")

        return re.sub(r"\s+", " ", text).strip()
