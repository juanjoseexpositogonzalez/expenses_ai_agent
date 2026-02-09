"""
Week 2 - Definition of Done: LLM Layer

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week2_llm.py -v
All tests must pass to complete Week 2's LLM milestone.

These tests verify your implementation of:
- ExpenseCategorizationResponse Pydantic model
- Assistant Protocol definition
- LLMProvider enum
- Type aliases (MESSAGES, COST)
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Protocol, Sequence

import pytest


class TestExpenseCategorizationResponse:
    """Tests for the structured output model."""

    def test_response_has_required_fields(self):
        """Response model must have all required fields."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("42.50"),
            currency=Currency.EUR,
            confidence=0.95,
            cost=Decimal("0.001"),
        )

        assert response.category == "Food"
        assert response.total_amount == Decimal("42.50")
        assert response.currency == Currency.EUR
        assert response.confidence == 0.95
        assert response.cost == Decimal("0.001")

    def test_response_optional_fields(self):
        """Response should support optional comments."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Transport",
            total_amount=Decimal("15.00"),
            currency=Currency.USD,
            confidence=0.8,
            cost=Decimal("0.002"),
            comments="Taxi ride to airport",
        )

        assert response.comments == "Taxi ride to airport"

    def test_response_has_timestamp(self):
        """Response should include a timestamp."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Entertainment",
            total_amount=Decimal("10.00"),
            currency=Currency.EUR,
            confidence=0.9,
            cost=Decimal("0.001"),
        )

        assert hasattr(response, "timestamp")
        assert isinstance(response.timestamp, datetime)

    def test_response_is_pydantic_model(self):
        """Response should be a Pydantic BaseModel for validation."""
        from pydantic import BaseModel

        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse

        assert issubclass(ExpenseCategorizationResponse, BaseModel)

    def test_response_json_serialization(self):
        """Response should serialize to JSON."""
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse
        from expenses_ai_agent.storage.models import Currency

        response = ExpenseCategorizationResponse(
            category="Food",
            total_amount=Decimal("25.00"),
            currency=Currency.GBP,
            confidence=0.85,
            cost=Decimal("0.001"),
        )

        json_str = response.model_dump_json()
        assert "Food" in json_str
        assert "25" in json_str


class TestAssistantProtocol:
    """Tests for the Assistant Protocol definition."""

    def test_assistant_protocol_exists(self):
        """Assistant should be defined as a Protocol."""
        from expenses_ai_agent.llms.base import Assistant

        # Protocol is a special class for structural typing
        assert hasattr(Assistant, "__protocol_attrs__") or issubclass(Assistant, Protocol)

    def test_assistant_has_completion_method(self):
        """Assistant Protocol must define completion method."""
        from expenses_ai_agent.llms.base import Assistant

        # Check that completion is defined in the protocol
        assert hasattr(Assistant, "completion")

    def test_assistant_has_calculate_cost_method(self):
        """Assistant Protocol must define calculate_cost method."""
        from expenses_ai_agent.llms.base import Assistant

        assert hasattr(Assistant, "calculate_cost")

    def test_assistant_has_get_available_models_method(self):
        """Assistant Protocol must define get_available_models method."""
        from expenses_ai_agent.llms.base import Assistant

        assert hasattr(Assistant, "get_available_models")


class TestLLMProvider:
    """Tests for the LLMProvider enumeration."""

    def test_llm_provider_has_openai(self):
        """LLMProvider should include OPENAI."""
        from expenses_ai_agent.llms.base import LLMProvider

        assert hasattr(LLMProvider, "OPENAI")

    def test_llm_provider_has_groq(self):
        """LLMProvider should include GROQ."""
        from expenses_ai_agent.llms.base import LLMProvider

        assert hasattr(LLMProvider, "GROQ")

    def test_llm_provider_is_str_enum(self):
        """LLMProvider should be a StrEnum for string compatibility."""
        from enum import StrEnum

        from expenses_ai_agent.llms.base import LLMProvider

        assert issubclass(LLMProvider, StrEnum)


class TestTypeAliases:
    """Tests for type alias definitions."""

    def test_messages_type_alias_exists(self):
        """MESSAGES type alias should be defined."""
        from expenses_ai_agent.llms.base import MESSAGES

        # MESSAGES should be a type alias for List[Dict[str, str]]
        # We can verify it accepts the expected structure
        sample_messages: MESSAGES = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"},
        ]
        assert len(sample_messages) == 2

    def test_cost_type_alias_exists(self):
        """COST type alias should be defined."""
        from expenses_ai_agent.llms.base import COST

        # COST should be a type alias for Dict[str, List[Decimal]]
        sample_cost: COST = {
            "prompt": [Decimal("0.001"), Decimal("0.002")],
            "completion": [Decimal("0.003")],
        }
        assert "prompt" in sample_cost
