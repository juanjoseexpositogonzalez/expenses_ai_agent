"""
Week 6 - Definition of Done: Test Coverage Verification

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week6_coverage.py -v
All tests must pass to complete Week 6's coverage milestone.

These tests verify that all major components are importable and testable.
They serve as a checklist for what should be covered by your test suite.
"""

import pytest


class TestImportability:
    """Verify all major components are importable (ensures they exist)."""

    def test_storage_models_importable(self):
        """Storage models should be importable."""
        from expenses_ai_agent.storage.models import (
            Currency,
            Expense,
            ExpenseCategory,
            UserPreference,
        )

        assert Currency is not None
        assert Expense is not None
        assert ExpenseCategory is not None
        assert UserPreference is not None

    def test_storage_repos_importable(self):
        """Storage repositories should be importable."""
        from expenses_ai_agent.storage.repo import (
            CategoryRepository,
            DBCategoryRepo,
            DBExpenseRepo,
            ExpenseRepository,
            InMemoryCategoryRepository,
            InMemoryExpenseRepository,
        )

        assert CategoryRepository is not None
        assert ExpenseRepository is not None
        assert InMemoryCategoryRepository is not None
        assert InMemoryExpenseRepository is not None
        assert DBCategoryRepo is not None
        assert DBExpenseRepo is not None

    def test_llm_components_importable(self):
        """LLM components should be importable."""
        from expenses_ai_agent.llms.base import Assistant, LLMProvider, MESSAGES
        from expenses_ai_agent.llms.openai import OpenAIAssistant
        from expenses_ai_agent.llms.output import ExpenseCategorizationResponse

        assert Assistant is not None
        assert LLMProvider is not None
        assert MESSAGES is not None
        assert OpenAIAssistant is not None
        assert ExpenseCategorizationResponse is not None

    def test_services_importable(self):
        """Services should be importable."""
        from expenses_ai_agent.services.classification import (
            ClassificationResult,
            ClassificationService,
        )
        from expenses_ai_agent.services.preprocessing import (
            InputPreprocessor,
            PreprocessingResult,
        )

        assert ClassificationService is not None
        assert ClassificationResult is not None
        assert InputPreprocessor is not None
        assert PreprocessingResult is not None

    def test_api_components_importable(self):
        """API components should be importable."""
        from expenses_ai_agent.api.main import app
        from expenses_ai_agent.api.deps import get_expense_repo, get_user_id
        from expenses_ai_agent.api.schemas.expense import (
            ExpenseClassifyRequest,
            ExpenseResponse,
        )

        assert app is not None
        assert get_expense_repo is not None
        assert get_user_id is not None
        assert ExpenseClassifyRequest is not None
        assert ExpenseResponse is not None

    def test_telegram_components_importable(self):
        """Telegram components should be importable."""
        from expenses_ai_agent.telegram.bot import ExpenseTelegramBot
        from expenses_ai_agent.telegram.handlers import (
            CurrencyHandler,
            ExpenseConversationHandler,
        )
        from expenses_ai_agent.telegram.keyboards import (
            build_category_confirmation_keyboard,
            build_currency_selection_keyboard,
        )

        assert ExpenseTelegramBot is not None
        assert ExpenseConversationHandler is not None
        assert CurrencyHandler is not None
        assert build_category_confirmation_keyboard is not None
        assert build_currency_selection_keyboard is not None
