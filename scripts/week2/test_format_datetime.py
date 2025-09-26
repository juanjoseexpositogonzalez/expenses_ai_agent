import logging
from typing import Final

from decouple import config

from expenses_ai_agent.llms.base import LLMProvider
from expenses_ai_agent.llms.openai import OpenAIAssistant
from expenses_ai_agent.tools.tools import TOOLS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

OPENAI_API_KEY: Final[str] = config("OPENAI_API_KEY")  # type: ignore


def main() -> None:
    openai_assistant = OpenAIAssistant(
        provider=LLMProvider.OPENAI,
        api_key=OPENAI_API_KEY,
        model="gpt-4.1-nano-2025-04-14",
        max_response_tokens=500,
        temperature=0.7,
        top_p=1.0,
        tools=TOOLS,
    )  # type: ignore

    # Test format_datetime tool
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Format this datetime: '2025-09-26T14:30:00' to Europe/Madrid timezone.",
        },
    ]

    logger.info("Testing format_datetime tool...")
    completion = openai_assistant.completion(messages=messages)

    logger.info("Completion: %s", completion)

    logger.info(
        "Total Cost: $%s",
        openai_assistant.calculate_cost(
            prompt_tokens=openai_assistant.prompt_tokens,
            completion_tokens=openai_assistant.completion_tokens,
        ),
    )


if __name__ == "__main__":
    main()
