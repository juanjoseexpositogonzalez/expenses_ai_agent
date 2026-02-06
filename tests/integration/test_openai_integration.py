"""Integration tests for OpenAI API.

These tests require real API keys and make actual API calls.
Run with: pytest -m integration

To skip in CI: pytest -m "not integration"
"""

import pytest
from decouple import config

from expenses_ai_agent.llms.base import LLMProvider
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT
from expenses_ai_agent.prompts.user import USER_PROMPT


# Check if API key is available
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
SKIP_REASON = "OPENAI_API_KEY not configured"


@pytest.mark.integration
@pytest.mark.skipif(not OPENAI_API_KEY, reason=SKIP_REASON)
class TestOpenAIIntegration:
    """Integration tests for OpenAI API calls."""

    def test_classify_expense_with_structured_output(self) -> None:
        """Test real expense classification with structured output."""
        assistant = OpenAIAssistant(
            provider=LLMProvider.OPENAI,
            api_key=OPENAI_API_KEY,
            model="gpt-4.1-nano-2025-04-14",
            max_response_tokens=500,
            temperature=0.3,
            top_p=1.0,
            structured_output=ExpenseCategorizationResponse,
        )

        messages = [
            {"role": "system", "content": CLASSIFICATION_PROMPT},
            {"role": "user", "content": USER_PROMPT.format(expense_description="Coffee at Starbucks for $5.50")},
        ]

        result = assistant.completion(messages)

        assert isinstance(result, ExpenseCategorizationResponse)
        assert result.category in [
            "Food & Dining",
            "Transportation",
            "Shopping",
            "Entertainment",
            "Healthcare",
            "Utilities",
            "Housing",
            "Education",
            "Travel",
            "Personal Care",
            "Subscriptions",
            "Other",
        ]
        assert result.confidence > 0
        assert result.cost > 0

    def test_get_available_models(self) -> None:
        """Test retrieving available models from OpenAI."""
        assistant = OpenAIAssistant(
            provider=LLMProvider.OPENAI,
            api_key=OPENAI_API_KEY,
            model="gpt-4.1-nano-2025-04-14",
        )

        models = assistant.get_available_models()

        assert len(models) > 0
        # At least some known models should be present
        model_ids = set(models)
        assert any("gpt" in m.lower() for m in model_ids)
