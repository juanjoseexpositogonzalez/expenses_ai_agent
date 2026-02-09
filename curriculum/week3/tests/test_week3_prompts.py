"""
Week 3 - Definition of Done: Prompts

Copy this file to your project's tests/unit/ directory.
Run: pytest tests/unit/test_week3_prompts.py -v
All tests must pass to complete Week 3's prompts milestone.

These tests verify your implementation of:
- CLASSIFICATION_PROMPT system prompt
- USER_PROMPT template
"""

import pytest


class TestClassificationPrompt:
    """Tests for the system prompt used in expense classification."""

    def test_classification_prompt_exists(self):
        """CLASSIFICATION_PROMPT should be defined as a string constant."""
        from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT

        assert isinstance(CLASSIFICATION_PROMPT, str)
        assert len(CLASSIFICATION_PROMPT) > 100  # Non-trivial prompt

    def test_classification_prompt_contains_categories(self):
        """System prompt should mention all 12 expense categories."""
        from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT

        required_categories = [
            "Food",
            "Transport",
            "Entertainment",
            "Shopping",
            "Health",
            "Bills",
            "Education",
            "Travel",
            "Services",
            "Gifts",
            "Investments",
            "Other",
        ]

        prompt_lower = CLASSIFICATION_PROMPT.lower()
        for category in required_categories:
            assert category.lower() in prompt_lower, f"Category '{category}' not found in prompt"

    def test_classification_prompt_mentions_json_output(self):
        """System prompt should mention JSON output format."""
        from expenses_ai_agent.prompts.system import CLASSIFICATION_PROMPT

        prompt_lower = CLASSIFICATION_PROMPT.lower()
        assert "json" in prompt_lower, "Prompt should mention JSON output"


class TestUserPrompt:
    """Tests for the user prompt template."""

    def test_user_prompt_exists(self):
        """USER_PROMPT should be defined as a string constant."""
        from expenses_ai_agent.prompts.user import USER_PROMPT

        assert isinstance(USER_PROMPT, str)

    def test_user_prompt_has_placeholder(self):
        """USER_PROMPT should have a placeholder for expense description."""
        from expenses_ai_agent.prompts.user import USER_PROMPT

        # Should contain a placeholder (could be {expense_description} or similar)
        assert "{" in USER_PROMPT and "}" in USER_PROMPT, "Prompt should have a placeholder"

    def test_user_prompt_can_be_formatted(self):
        """USER_PROMPT should be formattable with expense description."""
        from expenses_ai_agent.prompts.user import USER_PROMPT

        # Try to format the prompt
        try:
            formatted = USER_PROMPT.format(expense_description="Coffee at Starbucks $5.50")
            assert "Coffee" in formatted or "Starbucks" in formatted or "5.50" in formatted
        except KeyError as e:
            # If different placeholder name, that's OK as long as it's formattable
            assert "expense" in str(e).lower(), f"Unexpected placeholder: {e}"
