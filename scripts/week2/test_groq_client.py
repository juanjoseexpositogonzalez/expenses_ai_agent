import logging
from typing import Final, Sequence

from decouple import config

from expenses_ai_agent.llms.base import LLMProvider
from expenses_ai_agent.llms.groq import GroqAssistant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

GROQ_API_KEY: Final[str] = config("GROQ_API_KEY")  # type: ignore


def main() -> None:
    groq_assistant = GroqAssistant(
        provider=LLMProvider.GROQ,
        api_key=GROQ_API_KEY,
        model="openai/gpt-oss-20b",
        max_response_tokens=500,
    )  # type: ignore

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Hello, how can you assist me today?"},
    ]

    available_models: Sequence[str] = groq_assistant.get_available_models()
    logger.info(
        "There are %d available models: %s", len(available_models), available_models
    )
    completion = groq_assistant.completion(messages=messages)

    logger.info("Completion %s", completion)


if __name__ == "__main__":
    main()
