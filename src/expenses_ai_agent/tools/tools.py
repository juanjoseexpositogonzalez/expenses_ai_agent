from typing import Any, Dict, Final, List

from expenses_ai_agent.storage.models import Currency


def convert_currency_tool_schema() -> Dict[str, Any]:
    enum_vals: List[str] = [c.value for c in Currency]
    return {
        "type": "function",
        "function": {
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
        },
    }


def format_datetime_tool_schema() -> Dict[str, Any]:
    return {
        "type": "function",
        "function": {
            "name": "format_datetime",
            "description": "Format a datetime into 'DD/MM/YYYY HH:MM'.",
            "parameters": {
                "type": "object",
                "properties": {
                    "dt": {
                        "type": "string",
                        "description": (
                            "Datetime in ISO 8601 format "
                            "(e.g., '2025-09-26T12:34:00' or "
                            "'2025-09-26T12:34:00+02:00'). "
                            "If no timezone offset is provided, 'output_tz' will be assumed."
                        ),
                        "format": "date-time",
                    },
                    "output_tz": {
                        "type": "string",
                        "description": (
                            "IANA timezone name for the output "
                            "(e.g., 'Europe/Madrid', 'UTC'). "
                            "Used if 'dt' has no explicit offset."
                        ),
                        "default": "Europe/Madrid",
                    },
                },
                "required": ["dt"],
                "additionalProperties": False,
            },
        },
    }


TOOLS: Final[List[Dict[str, Any]]] = [
    convert_currency_tool_schema(),
    format_datetime_tool_schema(),
]
