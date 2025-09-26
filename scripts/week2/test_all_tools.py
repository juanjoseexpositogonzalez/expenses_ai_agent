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

    # Test 1: Currency conversion
    logger.info("=== Test 1: Currency Conversion ===")
    messages1 = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Convert 100 EUR to USD."},
    ]

    completion1 = openai_assistant.completion(messages=messages1)
    logger.info("Currency conversion result: %s", completion1.content)  # type: ignore

    # Test 2: Datetime formatting
    logger.info("=== Test 2: Datetime Formatting ===")
    messages2 = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Format this datetime: '2025-12-25T18:30:00' to UTC timezone.",
        },
    ]

    completion2 = openai_assistant.completion(messages=messages2)
    logger.info("Datetime formatting result: %s", completion2.content)  # type: ignore

    # Test 3: Both tools in same conversation
    logger.info("=== Test 3: Both Tools Combined ===")
    messages3 = [
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "Convert 50.75 GBP to EUR, and format this datetime: '2025-01-01T00:00:00' to Europe/Madrid timezone.",
        },
    ]

    completion3 = openai_assistant.completion(messages=messages3)
    logger.info("Combined tools result: %s", completion3.content)  # type: ignore

    logger.info(
        "Total Cost: $%s",
        openai_assistant.calculate_cost(
            prompt_tokens=openai_assistant.prompt_tokens,
            completion_tokens=openai_assistant.completion_tokens,
        ),
    )


if __name__ == "__main__":
    main()
