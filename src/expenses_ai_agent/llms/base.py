from abc import abstractmethod
from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum
from typing import Any, Dict, List, Protocol, Sequence

from expenses_ai_agent.llms.output import ExpenseCategorizationResponse

MESSAGES = List[Dict[str, str]]
COST = Dict[str, List[Decimal]]  # e.g., {"gpt-4": [0.03, 0.06]}


class LLMProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    META = "meta"
    GOOGLE = "google"
    GROQ = "groq"
    PLAYAI = "playai"
    ALIBABA = "alibaba"


# class ModelName(StrEnum):
#     GPT_5 = "gpt-5"
#     CLAUDE_OPUS_41 = "claude-opus-4-1"
#     CLAUDE_OPUS_40 = "claude-opus-4-0"
#     CLAUDE_SONNET_40 = "claude-sonnet-4-0"
#     CLAUDE_SONNET_37 = "claude-3-7-sonnet-latest"
#     CLAUDE_HAIKU_35 = "claude-3-5-haiku-latest"
#     LLAMA_31_8B_INSTANT = "llama-3.1-8b-instant"
#     LLAMA_33_70B_VERSATILE = "llama-3.3-70b-versatile"
#     META_LLAMA_GUARD_4_12B = "meta-llama/llama-guard-4-12b"
#     OPENAI_GPT_OSS_120B = "openai/gpt-oss-120b"
#     OPENAI_GPT_OSS_20B = "openai/gpt-oss-20b"
#     WHISPER_LARGE_V3 = "whisper-large-v3"
#     WHISPER_LARGE_V3_TURBO = "whisper-large-v3-turbo"
#     GROQ_COMPOUND = "groq/compound"
#     GROQ_COMPOUND_MINI = "groq/compound-mini"


@dataclass
class Assistant(Protocol):
    """Contract class for LLM Assistant implementations."""

    api_key: str
    model: str
    provider: LLMProvider
    client: Any = field(init=False)
    max_response_tokens: int = 1000
    max_completion_tokens: int | None = None
    temperature: float = 0.7
    top_p: float = 1.0
    models_cost: COST = field(default_factory=dict)  # e.g., {"gpt-4": [0.03, 0.06]}

    @abstractmethod
    def completion(self, messages: MESSAGES) -> ExpenseCategorizationResponse:
        """Generate a response based on the messages provided.

        Args:
            messages (MESSAGES): A list of message dictionaries.

        Returns:
            ExpenseCategorizationResponse: The response containing the expense categorization.
        """

    @abstractmethod
    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        """Calculate the cost of the provided messages.

        Args:
            prompt_tokes (int): Number of tokens in the prompt.
            completion_tokens (int): Number of tokens in the completion.

        Returns:
            Decimal: The calculated cost.
        """

    @abstractmethod
    def get_available_models(self) -> Sequence[str]:
        """Retrieve a list of available models from the provider.

        Returns:
            Sequence[str]: A list of available model names.
        """
