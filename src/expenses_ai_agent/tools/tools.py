from typing import Any, Dict, Final, List

from expenses_ai_agent.storage.models import Currency


def convert_currency_tool_schema() -> Dict[str, Any]:
    enum_vals: List[str] = [c.value for c in Currency]
    return {
        "type": "function",
        "name": "convert_currency",
        "description": "Convert an amount from one currency to another using an external FX API.",
        "parameters": {
            "type": "object",
            "properties": {
                "amount": {
                    "type": "string",
                    "description": "Amount to convert as a decimal string to preserve precision.",
                    "pattern": r"^-?\d+(?:\.\d+)?$",
                },
                "from_currency": {
                    "type": "string",
                    "description": "ISO 4217 currency code (e.g., EUR, USD).",
                    "enum": enum_vals,
                },
                "to_currency": {
                    "type": "string",
                    "description": "Target ISO 4217 currency code. Defaults to EUR.",
                    "enum": enum_vals,
                    "default": "EUR",
                },
            },
            "required": ["amount", "from_currency"],
            "additionalProperties": False,
        },
    }


TOOLS: Final[List[Dict[str, Any]]] = [convert_currency_tool_schema()]
