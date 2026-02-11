"""Tests for Groq Assistant implementation."""

from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from expenses_ai_agent.llms.base import LLMProvider


class MockMessage:
    """Mock for Groq message object."""

    def __init__(self, content: str) -> None:
        self.content = content


class MockChoice:
    """Mock for Groq choice object."""

    def __init__(self, message: MockMessage) -> None:
        self.message = message


class MockCompletion:
    """Mock for Groq chat completion response."""

    def __init__(self, choices: list[MockChoice]) -> None:
        self.choices = choices


class MockModel:
    """Mock for Groq model object."""

    def __init__(self, model_id: str) -> None:
        self.id = model_id


class MockModelList:
    """Mock for Groq model list response."""

    def __init__(self, models: list[MockModel]) -> None:
        self.data = models


@pytest.fixture
def mock_groq_client() -> MagicMock:
    """Create a mock Groq client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def assistant_kwargs() -> dict[str, Any]:
    """Common assistant initialization kwargs."""
    return {
        "api_key": "test-groq-api-key",
        "model": "llama-3.3-70b-versatile",
        "provider": LLMProvider.GROQ,
        "max_response_tokens": 1000,
        "temperature": 0.7,
        "top_p": 1.0,
    }


class TestGroqAssistantInit:
    """Tests for Groq Assistant initialization."""

    @patch("expenses_ai_agent.llms.groq.Groq")
    def test_assistant_init(
        self, mock_groq_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test that assistant initializes correctly."""
        from expenses_ai_agent.llms.groq import GroqAssistant

        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        assistant = GroqAssistant(**assistant_kwargs)

        mock_groq_class.assert_called_once_with(api_key="test-groq-api-key")
        assert assistant.client == mock_client
        assert assistant.provider == LLMProvider.GROQ
        assert assistant.model == "llama-3.3-70b-versatile"

    @patch("expenses_ai_agent.llms.groq.Groq")
    def test_assistant_sets_provider(
        self, mock_groq_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test that assistant sets provider to GROQ."""
        from expenses_ai_agent.llms.groq import GroqAssistant

        assistant = GroqAssistant(**assistant_kwargs)

        assert assistant.provider == LLMProvider.GROQ


class TestGroqAssistantCompletion:
    """Tests for Groq Assistant completion method."""

    @patch("expenses_ai_agent.llms.groq.Groq")
    def test_completion_returns_content(
        self, mock_groq_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test that completion returns message content."""
        from expenses_ai_agent.llms.groq import GroqAssistant

        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        # Setup mock response
        mock_response = MockCompletion(
            choices=[MockChoice(MockMessage("Test response content"))]
        )
        mock_client.chat.completions.create.return_value = mock_response

        assistant = GroqAssistant(**assistant_kwargs)

        messages = [{"role": "user", "content": "Test message"}]
        result = assistant.completion(messages)

        assert result == "Test response content"

    @patch("expenses_ai_agent.llms.groq.Groq")
    def test_completion_calls_api_correctly(
        self, mock_groq_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test that completion calls API with correct parameters."""
        from expenses_ai_agent.llms.groq import GroqAssistant

        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        mock_response = MockCompletion(
            choices=[MockChoice(MockMessage("Response"))]
        )
        mock_client.chat.completions.create.return_value = mock_response

        assistant = GroqAssistant(**assistant_kwargs)

        messages = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Classify this expense"},
        ]
        assistant.completion(messages)

        mock_client.chat.completions.create.assert_called_once_with(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=1000,
        )


class TestGroqAssistantCalculateCost:
    """Tests for Groq Assistant cost calculation."""

    @patch("expenses_ai_agent.llms.groq.Groq")
    def test_calculate_cost_returns_zero(
        self, mock_groq_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test that calculate_cost returns 0 (Groq has free tier)."""
        from expenses_ai_agent.llms.groq import GroqAssistant

        assistant = GroqAssistant(**assistant_kwargs)

        cost = assistant.calculate_cost(prompt_tokens=1000, completion_tokens=500)

        assert cost == Decimal(0)
        assert isinstance(cost, Decimal)

    @patch("expenses_ai_agent.llms.groq.Groq")
    def test_calculate_cost_with_zero_tokens(
        self, mock_groq_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test cost calculation with zero tokens."""
        from expenses_ai_agent.llms.groq import GroqAssistant

        assistant = GroqAssistant(**assistant_kwargs)

        cost = assistant.calculate_cost(prompt_tokens=0, completion_tokens=0)

        assert cost == Decimal(0)

    @patch("expenses_ai_agent.llms.groq.Groq")
    def test_calculate_cost_with_large_tokens(
        self, mock_groq_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test cost calculation with large token counts."""
        from expenses_ai_agent.llms.groq import GroqAssistant

        assistant = GroqAssistant(**assistant_kwargs)

        cost = assistant.calculate_cost(prompt_tokens=100000, completion_tokens=50000)

        # Should still return 0 as Groq returns hardcoded 0
        assert cost == Decimal(0)


class TestGroqAssistantGetAvailableModels:
    """Tests for Groq Assistant model listing."""

    @patch("expenses_ai_agent.llms.groq.Groq")
    def test_get_available_models_returns_list(
        self, mock_groq_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test that get_available_models returns model IDs."""
        from expenses_ai_agent.llms.groq import GroqAssistant

        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        # Setup mock models
        mock_models = MockModelList([
            MockModel("llama-3.3-70b-versatile"),
            MockModel("mixtral-8x7b-32768"),
            MockModel("gemma2-9b-it"),
        ])
        mock_client.models.list.return_value = mock_models

        assistant = GroqAssistant(**assistant_kwargs)

        models = assistant.get_available_models()

        assert len(models) == 3
        assert "llama-3.3-70b-versatile" in models
        assert "mixtral-8x7b-32768" in models
        assert "gemma2-9b-it" in models

    @patch("expenses_ai_agent.llms.groq.Groq")
    def test_get_available_models_empty_list(
        self, mock_groq_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test get_available_models with empty list."""
        from expenses_ai_agent.llms.groq import GroqAssistant

        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        mock_models = MockModelList([])
        mock_client.models.list.return_value = mock_models

        assistant = GroqAssistant(**assistant_kwargs)

        models = assistant.get_available_models()

        assert len(models) == 0
        assert isinstance(models, list)

    @patch("expenses_ai_agent.llms.groq.Groq")
    def test_get_available_models_returns_sequence(
        self, mock_groq_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test that get_available_models returns a sequence of strings."""
        from expenses_ai_agent.llms.groq import GroqAssistant

        mock_client = MagicMock()
        mock_groq_class.return_value = mock_client

        mock_models = MockModelList([MockModel("test-model")])
        mock_client.models.list.return_value = mock_models

        assistant = GroqAssistant(**assistant_kwargs)

        models = assistant.get_available_models()

        assert all(isinstance(m, str) for m in models)
