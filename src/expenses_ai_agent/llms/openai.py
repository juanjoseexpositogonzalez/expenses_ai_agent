import json
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any, Dict, Sequence

from openai import OpenAI

from expenses_ai_agent.llms.base import MESSAGES, Assistant, LLMProvider
from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
from expenses_ai_agent.storage.models import Currency
from expenses_ai_agent.utils.currency import convert_currency
from expenses_ai_agent.utils.date_formatter import format_datetime


@dataclass
class OpenAIAssistant(Assistant):
    """OpenAI LLM Assistant implementation."""

    structured_output: Any | None = None
    tools: Sequence[Dict[str, Any]] | None = None

    prompt_tokens: int = field(default=0, init=False)
    completion_tokens: int = field(default=0, init=False)
    total_tokens: int = field(default=0, init=False)

    def __post_init__(self):
        self.provider: LLMProvider = LLMProvider.OPENAI
        self.client = OpenAI(api_key=self.api_key)
        self.models_cost = {  # type: ignore
            "gpt-5-2025-08-07": [
                Decimal("1.25"),
                Decimal("0.125"),
                Decimal("10.0"),
            ],  # [input, cached input, output] per 1M tokens
            "gpt-5-mini-2025-08-07": [
                Decimal("0.25"),
                Decimal("0.025"),
                Decimal("2.0"),
            ],
            "gpt-5-nano-2025-08-07": [
                Decimal("0.05"),
                Decimal("0.005"),
                Decimal("0.4"),
            ],
            "gpt-4.1-2025-04-141": [Decimal("3"), Decimal("0.75"), Decimal("12.0")],
            "gpt-4.1-mini-2025-04-14": [
                Decimal("0.80"),
                Decimal("0.20"),
                Decimal("3.2"),
            ],
            "gpt-4.1-nano-2025-04-14": [
                Decimal("0.20"),
                Decimal("0.05"),
                Decimal("0.80"),
            ],
            "o4-mini-2025-04-16": [Decimal("4.0"), Decimal("1.0"), Decimal("16.0")],
            "gpt-oss-120b": [Decimal("0.00"), Decimal("0.0"), Decimal("0.0")],
            "gpt-oss-20b": [Decimal("0.00"), Decimal("0.0"), Decimal("0.0")],
        }

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
            temperature=self.temperature,
            top_p=self.top_p,
            tools=self.tools,
            tool_choice="auto" if self.tools else None,
        )
        # Update token usage
        self.prompt_tokens = chat_completion.usage.prompt_tokens  # type: ignore
        self.completion_tokens = chat_completion.usage.completion_tokens  # type: ignore
        self.total_tokens = chat_completion.usage.total_tokens  # type: ignore

        msg = chat_completion.choices[0].message  # type: ignore

        if msg.tool_calls:  # type: ignore
            tool_messages: MESSAGES = []
            for tc in msg.tool_calls:  # type: ignore
                if tc.function.name == "convert_currency":
                    args = json.loads(tc.function.arguments)  # type: ignore
                    amount: Decimal = Decimal(args["amount"])
                    try:
                        from_cur = Currency(args["from_currency"].upper())
                    except (KeyError, ValueError):
                        from_cur = Currency[args["from_currency"].upper()]
                    if "to_currency" in args:
                        try:
                            to_cur = Currency(args["to_currency"].upper())
                        except (KeyError, ValueError):
                            to_cur = Currency[args["to_currency"].upper()]
                    else:
                        to_cur = Currency.EUR

                    result = convert_currency(
                        amount=amount, from_currency=from_cur, to_currency=to_cur
                    )

                    tool_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,  # type: ignore
                            "name": tc.function.name,
                            "content": f"The result is {result} {to_cur.value}",
                        }
                    )

                elif tc.function.name == "format_datetime":
                    args = json.loads(tc.function.arguments)  # type: ignore
                    dt: str = args["dt"]
                    output_tz: str = args.get("output_tz", "Europe/Madrid")

                    result = format_datetime(dt=dt, output_tz=output_tz)

                    tool_messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tc.id,  # type: ignore
                            "name": tc.function.name,
                            "content": f"The formatted datetime is: {result}",
                        }
                    )

            messages.extend(
                [
                    {
                        "role": "assistant",
                        "content": "None",
                        "tool_calls": msg.tool_calls,
                    },
                    *tool_messages,
                ]
            )

            final = self.client.chat.completions.create(
                model=self.model,
                messages=messages,  # type:ignore
            )
        else:
            final = chat_completion

        return final.choices[0].message  # type: ignore

    def calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> Decimal:
        """Calculate the cost of the provided messages.

        Args:
            prompt_tokens (int): Number of tokens in the prompt.
            completion_tokens (int): Number of tokens in the completion.

        Returns:
            Decimal: The calculated cost.
        """
        if self.model not in self.models_cost:
            return Decimal(0.0)
        input_cost, _, output_cost = self.models_cost[self.model]
        cost = (prompt_tokens * input_cost / 1_000_000) + (
            completion_tokens * output_cost / 1_000_000
        )
        return Decimal(cost)

    def get_available_models(self) -> Sequence[str]:
        """Retrieve a list of available models from the provider.

        Returns:
            Sequence[str]: A list of available model names.
        """
        data = self.client.models.list().data
        return [model.id for model in data]
