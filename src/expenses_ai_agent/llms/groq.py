from dataclasses import dataclass
from decimal import Decimal
from typing import Sequence

from groq import Groq

from expenses_ai_agent.llms.base import MESSAGES, Assistant, LLMProvider
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse


@dataclass
class GroqAssistant(Assistant):
    """Groq LLM Assistant implementation."""

    provider: LLMProvider = LLMProvider.GROQ
    client: Groq

    def __post__init__(self):
        self.client = Groq(api_key=self.api_key)

    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        """Generate a response based on the messages provided.

        Args:
            messages (list[dict[str, str]]): A list of message dictionaries.

        Returns:
            dict: The response containing the expense categorization.
        """
        chat_completion = self.client.chat.completions.create(
            model=self.model,
            messages=messages,  # type:ignore
            max_tokens=self.max_response_tokens,
        )
        return chat_completion.choices[0].message.content  # type: ignore

    def calculate_cost(self, messages: MESSAGES) -> Decimal:
        """Calculate the cost of the provided messages.

        Args:
            messages (MESSAGES): A list of message dictionaries.

        Returns:
            Decimal: The calculated cost.
        """
        return Decimal(0.0)

    def get_available_models(self) -> Sequence[str]:
        """Retrieve a list of available models from the provider.

        Returns:
            Sequence[str]: A list of available model names.
        """
        data = self.client.models.list().data
        return [model.id for model in data]
