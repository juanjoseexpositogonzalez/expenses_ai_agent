"""Tests for tool schemas."""

from expenses_ai_agent.storage.models import Currency
from expenses_ai_agent.tools.tools import (
    TOOLS,
    convert_currency_tool_schema,
    format_datetime_tool_schema,
)


class TestConvertCurrencyToolSchema:
    """Tests for convert_currency tool schema."""

    def test_returns_function_type(self) -> None:
        """Test schema has correct type."""
        schema = convert_currency_tool_schema()
        assert schema["type"] == "function"

    def test_function_name(self) -> None:
        """Test function name is correct."""
        schema = convert_currency_tool_schema()
        assert schema["function"]["name"] == "convert_currency"

    def test_has_required_parameters(self) -> None:
        """Test schema has required parameters."""
        schema = convert_currency_tool_schema()
        params = schema["function"]["parameters"]
        assert "amount" in params["properties"]
        assert "from_currency" in params["properties"]
        assert "to_currency" in params["properties"]
        assert params["required"] == ["amount", "from_currency"]

    def test_currency_enum_values(self) -> None:
        """Test currency enum contains all Currency values."""
        schema = convert_currency_tool_schema()
        from_currency_enum = schema["function"]["parameters"]["properties"]["from_currency"]["enum"]

        for currency in Currency:
            assert currency.value in from_currency_enum


class TestFormatDatetimeToolSchema:
    """Tests for format_datetime tool schema."""

    def test_returns_function_type(self) -> None:
        """Test schema has correct type."""
        schema = format_datetime_tool_schema()
        assert schema["type"] == "function"

    def test_function_name(self) -> None:
        """Test function name is correct."""
        schema = format_datetime_tool_schema()
        assert schema["function"]["name"] == "format_datetime"

    def test_has_required_parameters(self) -> None:
        """Test schema has required parameters."""
        schema = format_datetime_tool_schema()
        params = schema["function"]["parameters"]
        assert "dt" in params["properties"]
        assert "output_tz" in params["properties"]
        assert params["required"] == ["dt"]

    def test_output_tz_default(self) -> None:
        """Test output_tz has default value."""
        schema = format_datetime_tool_schema()
        output_tz = schema["function"]["parameters"]["properties"]["output_tz"]
        assert output_tz["default"] == "Europe/Madrid"


class TestToolsList:
    """Tests for TOOLS constant."""

    def test_tools_contains_both_schemas(self) -> None:
        """Test TOOLS list contains both tool schemas."""
        assert len(TOOLS) == 2

    def test_tools_has_convert_currency(self) -> None:
        """Test TOOLS contains convert_currency."""
        function_names = [tool["function"]["name"] for tool in TOOLS]
        assert "convert_currency" in function_names

    def test_tools_has_format_datetime(self) -> None:
        """Test TOOLS contains format_datetime."""
        function_names = [tool["function"]["name"] for tool in TOOLS]
        assert "format_datetime" in function_names
