"""Tests for OpenAI Assistant implementation."""

import json
from decimal import Decimal
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from expenses_ai_agent.llms.output import ExpenseCategorizationResponse


class MockToolCall:
    """Mock for OpenAI tool call object."""

    def __init__(self, tool_id: str, name: str, arguments: str) -> None:
        self.id = tool_id
        self.function = MagicMock()
        self.function.name = name
        self.function.arguments = arguments


class MockMessage:
    """Mock for OpenAI message object."""

    def __init__(
        self, content: str | None = None, tool_calls: list[MockToolCall] | None = None
    ) -> None:
        self.content = content
        self.tool_calls = tool_calls


class MockChoice:
    """Mock for OpenAI choice object."""

    def __init__(self, message: MockMessage) -> None:
        self.message = message


class MockUsage:
    """Mock for OpenAI usage object."""

    def __init__(
        self, prompt_tokens: int, completion_tokens: int, total_tokens: int
    ) -> None:
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens


class MockCompletion:
    """Mock for OpenAI chat completion response."""

    def __init__(self, choices: list[MockChoice], usage: MockUsage) -> None:
        self.choices = choices
        self.usage = usage


class MockModel:
    """Mock for OpenAI model object."""

    def __init__(self, model_id: str) -> None:
        self.id = model_id


class MockModelList:
    """Mock for OpenAI model list response."""

    def __init__(self, models: list[MockModel]) -> None:
        self.data = models


@pytest.fixture
def mock_openai_client() -> MagicMock:
    """Create a mock OpenAI client."""
    mock_client = MagicMock()
    return mock_client


@pytest.fixture
def assistant_kwargs() -> dict[str, Any]:
    """Common assistant initialization kwargs."""
    from expenses_ai_agent.llms.base import LLMProvider

    return {
        "api_key": "test-api-key",
        "model": "gpt-4.1-nano-2025-04-14",
        "provider": LLMProvider.OPENAI,
        "max_response_tokens": 1000,
        "temperature": 0.7,
        "top_p": 1.0,
    }


class TestOpenAIAssistantInit:
    """Tests for OpenAI Assistant initialization."""

    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_assistant_init(
        self, mock_openai_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test assistant initializes with correct parameters."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        assistant = OpenAIAssistant(**assistant_kwargs)

        assert assistant.api_key == "test-api-key"
        assert assistant.model == "gpt-4.1-nano-2025-04-14"
        assert assistant.prompt_tokens == 0
        assert assistant.completion_tokens == 0
        mock_openai_class.assert_called_once_with(api_key="test-api-key")


class TestOpenAIAssistantCompletion:
    """Tests for OpenAI Assistant completion method."""

    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_completion_with_structured_output(
        self, mock_openai_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test completion with structured output parses JSON correctly."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        # Mock the completion response with JSON in the content
        json_response = json.dumps(
            {
                "Category": "Food & Dining",
                "Total Amount": "25.50",
                "Currency": "EUR",
                "Confidence": 0.95,
                "Cost": "0.001",
                "Comments": "Restaurant expense",
                "Timestamp": "2024-01-15T12:00:00Z",
            }
        )
        mock_message = MockMessage(content=f"Here's the result: {json_response}")
        mock_completion = MockCompletion(
            choices=[MockChoice(mock_message)],
            usage=MockUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        )

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        assistant = OpenAIAssistant(
            **assistant_kwargs, structured_output=ExpenseCategorizationResponse
        )

        messages = [{"role": "user", "content": "Classify this expense"}]
        result = assistant.completion(messages)

        assert isinstance(result, ExpenseCategorizationResponse)
        assert result.category == "Food & Dining"
        assert result.total_amount == Decimal("25.50")
        assert str(result.currency) == "EUR"
        assert result.confidence == 0.95

    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_completion_without_structured_output(
        self, mock_openai_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test completion without structured output returns message."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        mock_message = MockMessage(content="The expense has been classified.")
        mock_completion = MockCompletion(
            choices=[MockChoice(mock_message)],
            usage=MockUsage(prompt_tokens=50, completion_tokens=30, total_tokens=80),
        )

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        assistant = OpenAIAssistant(**assistant_kwargs)  # No structured_output

        messages = [{"role": "user", "content": "Hello"}]
        result = assistant.completion(messages)

        assert result == mock_message

    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_completion_json_parse_error(
        self, mock_openai_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test completion raises error on malformed JSON."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        # Malformed JSON - has braces but invalid JSON content
        mock_message = MockMessage(content='{"invalid": json content without quotes}')
        mock_completion = MockCompletion(
            choices=[MockChoice(mock_message)],
            usage=MockUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        )

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        assistant = OpenAIAssistant(
            **assistant_kwargs, structured_output=ExpenseCategorizationResponse
        )

        messages = [{"role": "user", "content": "Test"}]
        with pytest.raises(ValueError, match="Failed to parse JSON response"):
            assistant.completion(messages)

    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_completion_no_json_found(
        self, mock_openai_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test completion raises error when no JSON found in response."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        # No JSON braces in content
        mock_message = MockMessage(content="Just plain text with no braces")
        mock_completion = MockCompletion(
            choices=[MockChoice(mock_message)],
            usage=MockUsage(prompt_tokens=100, completion_tokens=50, total_tokens=150),
        )

        mock_client = MagicMock()
        mock_client.chat.completions.create.return_value = mock_completion
        mock_openai_class.return_value = mock_client

        assistant = OpenAIAssistant(
            **assistant_kwargs, structured_output=ExpenseCategorizationResponse
        )

        messages = [{"role": "user", "content": "Test"}]
        with pytest.raises(ValueError, match="No valid JSON found"):
            assistant.completion(messages)


class TestOpenAIAssistantToolCalling:
    """Tests for OpenAI Assistant tool calling."""

    @patch("expenses_ai_agent.llms.openai.convert_currency")
    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_completion_with_currency_tool(
        self,
        mock_openai_class: MagicMock,
        mock_convert: MagicMock,
        assistant_kwargs: dict[str, Any],
    ) -> None:
        """Test completion handles convert_currency tool call."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        # First call returns a tool call
        tool_call = MockToolCall(
            tool_id="call_123",
            name="convert_currency",
            arguments=json.dumps(
                {"amount": "100", "from_currency": "USD", "to_currency": "EUR"}
            ),
        )
        first_message = MockMessage(content=None, tool_calls=[tool_call])
        first_completion = MockCompletion(
            choices=[MockChoice(first_message)],
            usage=MockUsage(prompt_tokens=100, completion_tokens=20, total_tokens=120),
        )

        # Second call after tool execution
        final_message = MockMessage(content="The converted amount is 85 EUR")
        final_completion = MockCompletion(
            choices=[MockChoice(final_message)],
            usage=MockUsage(prompt_tokens=150, completion_tokens=30, total_tokens=180),
        )

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            first_completion,
            final_completion,
        ]
        mock_openai_class.return_value = mock_client

        mock_convert.return_value = Decimal("85.00")

        # Add tools to the assistant
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "convert_currency",
                    "parameters": {"type": "object"},
                },
            }
        ]
        assistant = OpenAIAssistant(**assistant_kwargs, tools=tools)

        messages = [{"role": "user", "content": "Convert 100 USD to EUR"}]
        result = assistant.completion(messages)

        assert result == final_message
        mock_convert.assert_called_once()

    @patch("expenses_ai_agent.llms.openai.format_datetime")
    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_completion_with_datetime_tool(
        self,
        mock_openai_class: MagicMock,
        mock_format_dt: MagicMock,
        assistant_kwargs: dict[str, Any],
    ) -> None:
        """Test completion handles format_datetime tool call."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        # First call returns a tool call
        tool_call = MockToolCall(
            tool_id="call_456",
            name="format_datetime",
            arguments=json.dumps(
                {"dt": "2024-01-15T10:00:00Z", "output_tz": "Europe/Madrid"}
            ),
        )
        first_message = MockMessage(content=None, tool_calls=[tool_call])
        first_completion = MockCompletion(
            choices=[MockChoice(first_message)],
            usage=MockUsage(prompt_tokens=100, completion_tokens=20, total_tokens=120),
        )

        # Second call after tool execution
        final_message = MockMessage(content="The formatted datetime is 15/01/2024 11:00")
        final_completion = MockCompletion(
            choices=[MockChoice(final_message)],
            usage=MockUsage(prompt_tokens=150, completion_tokens=30, total_tokens=180),
        )

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            first_completion,
            final_completion,
        ]
        mock_openai_class.return_value = mock_client

        mock_format_dt.return_value = "15/01/2024 11:00"

        tools = [
            {"type": "function", "function": {"name": "format_datetime", "parameters": {}}}
        ]
        assistant = OpenAIAssistant(**assistant_kwargs, tools=tools)

        messages = [{"role": "user", "content": "Format this date"}]
        result = assistant.completion(messages)

        assert result == final_message
        mock_format_dt.assert_called_once_with(
            dt="2024-01-15T10:00:00Z", output_tz="Europe/Madrid"
        )

    @patch("expenses_ai_agent.llms.openai.convert_currency")
    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_currency_tool_with_enum_name_fallback(
        self,
        mock_openai_class: MagicMock,
        mock_convert: MagicMock,
        assistant_kwargs: dict[str, Any],
    ) -> None:
        """Test currency tool falls back to enum name when value lookup fails."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        # Currency provided as "usd" instead of "USD" - needs fallback
        tool_call = MockToolCall(
            tool_id="call_789",
            name="convert_currency",
            arguments=json.dumps({"amount": "50", "from_currency": "usd"}),
        )
        first_message = MockMessage(content=None, tool_calls=[tool_call])
        first_completion = MockCompletion(
            choices=[MockChoice(first_message)],
            usage=MockUsage(prompt_tokens=100, completion_tokens=20, total_tokens=120),
        )

        final_message = MockMessage(content="Converted successfully")
        final_completion = MockCompletion(
            choices=[MockChoice(final_message)],
            usage=MockUsage(prompt_tokens=150, completion_tokens=30, total_tokens=180),
        )

        mock_client = MagicMock()
        mock_client.chat.completions.create.side_effect = [
            first_completion,
            final_completion,
        ]
        mock_openai_class.return_value = mock_client

        mock_convert.return_value = Decimal("42.50")

        tools = [
            {"type": "function", "function": {"name": "convert_currency", "parameters": {}}}
        ]
        assistant = OpenAIAssistant(**assistant_kwargs, tools=tools)

        messages = [{"role": "user", "content": "Convert"}]
        result = assistant.completion(messages)

        assert result == final_message
        mock_convert.assert_called_once()


class TestOpenAIAssistantCostCalculation:
    """Tests for OpenAI Assistant cost calculation."""

    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_calculate_cost_known_model(
        self, mock_openai_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test cost calculation for a known model."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        assistant = OpenAIAssistant(**assistant_kwargs)

        # gpt-4.1-nano: input=0.10, output=0.40 per 1M tokens
        cost = assistant.calculate_cost(prompt_tokens=1000, completion_tokens=500)

        # Expected: (1000 * 0.10 / 1_000_000) + (500 * 0.40 / 1_000_000)
        # = 0.0001 + 0.0002 = 0.0003
        expected = Decimal("0.0001") + Decimal("0.0002")
        assert cost == expected

    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_calculate_cost_unknown_model(
        self, mock_openai_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test cost calculation returns 0 for unknown model."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        assistant_kwargs["model"] = "unknown-model-xyz"
        assistant = OpenAIAssistant(**assistant_kwargs)

        cost = assistant.calculate_cost(prompt_tokens=1000, completion_tokens=500)

        assert cost == Decimal("0.0")


class TestOpenAIAssistantModels:
    """Tests for OpenAI Assistant model listing."""

    @patch("expenses_ai_agent.llms.openai.OpenAI")
    def test_get_available_models(
        self, mock_openai_class: MagicMock, assistant_kwargs: dict[str, Any]
    ) -> None:
        """Test retrieving available models from OpenAI."""
        from expenses_ai_agent.llms.openai import OpenAIAssistant

        mock_models = MockModelList(
            [
                MockModel("gpt-4o"),
                MockModel("gpt-4o-mini"),
                MockModel("gpt-3.5-turbo"),
            ]
        )

        mock_client = MagicMock()
        mock_client.models.list.return_value = mock_models
        mock_openai_class.return_value = mock_client

        assistant = OpenAIAssistant(**assistant_kwargs)
        models = assistant.get_available_models()

        assert len(models) == 3
        assert "gpt-4o" in models
        assert "gpt-4o-mini" in models
        assert "gpt-3.5-turbo" in models
