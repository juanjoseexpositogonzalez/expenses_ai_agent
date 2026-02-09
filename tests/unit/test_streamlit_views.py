"""Tests for Streamlit views."""

from decimal import Decimal
from unittest.mock import MagicMock, patch, PropertyMock

import httpx
import pytest


def create_columns_mock(count_to_cols: dict[int, list]) -> MagicMock:
    """Create a columns mock that returns appropriate number of mock columns."""

    def columns_side_effect(n):
        # Handle both int and list args (st.columns(3) vs st.columns([3, 2, 2, 1]))
        if isinstance(n, list):
            count = len(n)
        else:
            count = n

        if count in count_to_cols:
            return count_to_cols[count]
        return [MagicMock() for _ in range(count)]

    mock = MagicMock(side_effect=columns_side_effect)
    return mock


class TestDashboardView:
    """Tests for dashboard view."""

    @patch("expenses_ai_agent.streamlit.views.dashboard.get_client")
    @patch("expenses_ai_agent.streamlit.views.dashboard.st")
    def test_render_dashboard_success(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test dashboard renders successfully with data."""
        from expenses_ai_agent.streamlit.views.dashboard import render

        # Setup mock client
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_analytics_summary.return_value = {
            "total_expenses": "1000.00",
            "expense_count": 10,
            "category_totals": [
                {"category": "Food", "total": "500.00"},
                {"category": "Transport", "total": "500.00"},
            ],
            "monthly_totals": [
                {"month": "2024-01", "total": "300.00"},
                {"month": "2024-02", "total": "700.00"},
            ],
        }
        mock_client.list_expenses.return_value = {
            "items": [
                {
                    "id": 1,
                    "description": "Coffee",
                    "category": "Food",
                    "amount": "5.50",
                    "currency": "USD",
                    "date": "2024-01-15T10:00:00Z",
                }
            ],
            "total": 1,
            "page": 1,
            "pages": 1,
        }

        # Mock columns to return correct number of columns
        mock_st.columns = create_columns_mock({
            3: [MagicMock(), MagicMock(), MagicMock()],
            2: [MagicMock(), MagicMock()],
        })

        render()

        mock_st.title.assert_called_once_with("Dashboard")
        mock_st.caption.assert_called_once_with("Overview of your expense tracking")
        mock_client.get_analytics_summary.assert_called_once_with(months=12)

    @patch("expenses_ai_agent.streamlit.views.dashboard.get_client")
    @patch("expenses_ai_agent.streamlit.views.dashboard.st")
    def test_render_dashboard_api_error(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test dashboard handles API error gracefully."""
        from expenses_ai_agent.streamlit.views.dashboard import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_analytics_summary.side_effect = Exception("API Error")

        render()

        mock_st.error.assert_called_once()
        assert "Failed to load analytics" in str(mock_st.error.call_args)

    @patch("expenses_ai_agent.streamlit.views.dashboard.get_client")
    @patch("expenses_ai_agent.streamlit.views.dashboard.st")
    def test_render_dashboard_empty_data(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test dashboard renders with empty data."""
        from expenses_ai_agent.streamlit.views.dashboard import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_analytics_summary.return_value = {
            "total_expenses": "0.00",
            "expense_count": 0,
            "category_totals": [],
            "monthly_totals": [],
        }
        mock_client.list_expenses.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "pages": 0,
        }

        mock_st.columns = create_columns_mock({
            3: [MagicMock(), MagicMock(), MagicMock()],
            2: [MagicMock(), MagicMock()],
        })

        render()

        # Should show info message for empty category data
        assert mock_st.info.call_count >= 1

    @patch("expenses_ai_agent.streamlit.views.dashboard.get_client")
    @patch("expenses_ai_agent.streamlit.views.dashboard.st")
    def test_render_dashboard_recent_expenses_error(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test dashboard handles recent expenses load error."""
        from expenses_ai_agent.streamlit.views.dashboard import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.get_analytics_summary.return_value = {
            "total_expenses": "100.00",
            "expense_count": 1,
            "category_totals": [],
            "monthly_totals": [],
        }
        mock_client.list_expenses.side_effect = Exception("Load error")

        mock_st.columns = create_columns_mock({
            3: [MagicMock(), MagicMock(), MagicMock()],
            2: [MagicMock(), MagicMock()],
        })

        render()

        # Should show error for recent expenses
        error_calls = [str(call) for call in mock_st.error.call_args_list]
        assert any("recent expenses" in str(call).lower() for call in error_calls)


class MockSessionState(dict):
    """Mock session state that supports both dict and attribute access."""

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)

    def __setattr__(self, key, value):
        self[key] = value

    def __contains__(self, key):
        return dict.__contains__(self, key)


class TestExpensesView:
    """Tests for expenses list view."""

    @patch("expenses_ai_agent.streamlit.views.expenses.get_client")
    @patch("expenses_ai_agent.streamlit.views.expenses.st")
    def test_render_expenses_success(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test expenses list renders successfully."""
        from expenses_ai_agent.streamlit.views.expenses import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.list_expenses.return_value = {
            "items": [
                {
                    "id": 1,
                    "description": "Coffee",
                    "category": "Food",
                    "amount": "5.50",
                    "currency": "USD",
                    "date": "2024-01-15T10:00:00Z",
                }
            ],
            "total": 1,
            "page": 1,
            "pages": 1,
        }

        # Mock session state with proper class
        mock_st.session_state = MockSessionState(expense_page=1)
        mock_st.columns = create_columns_mock({
            4: [MagicMock(), MagicMock(), MagicMock(), MagicMock()],
            3: [MagicMock(), MagicMock(), MagicMock()],
        })
        mock_st.container.return_value.__enter__ = MagicMock(return_value=None)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=None)
        mock_st.button.return_value = False

        render()

        mock_st.title.assert_called_once_with("Expenses")
        mock_client.list_expenses.assert_called_once()

    @patch("expenses_ai_agent.streamlit.views.expenses.get_client")
    @patch("expenses_ai_agent.streamlit.views.expenses.st")
    def test_render_expenses_empty_list(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test expenses list with no expenses."""
        from expenses_ai_agent.streamlit.views.expenses import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.list_expenses.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "pages": 0,
        }

        mock_st.session_state = MockSessionState(expense_page=1)

        render()

        mock_st.warning.assert_called_once()
        assert "No expenses found" in str(mock_st.warning.call_args)

    @patch("expenses_ai_agent.streamlit.views.expenses.get_client")
    @patch("expenses_ai_agent.streamlit.views.expenses.st")
    def test_render_expenses_api_error(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test expenses list handles API error."""
        from expenses_ai_agent.streamlit.views.expenses import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.list_expenses.side_effect = Exception("API Error")

        mock_st.session_state = MockSessionState(expense_page=1)

        render()

        mock_st.error.assert_called_once()
        assert "Failed to load expenses" in str(mock_st.error.call_args)

    @patch("expenses_ai_agent.streamlit.views.expenses.get_client")
    @patch("expenses_ai_agent.streamlit.views.expenses.st")
    def test_render_expenses_initializes_page_state(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test expenses list initializes pagination state."""
        from expenses_ai_agent.streamlit.views.expenses import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.list_expenses.return_value = {
            "items": [],
            "total": 0,
            "page": 1,
            "pages": 0,
        }

        # Empty session state - should initialize expense_page
        mock_st.session_state = MockSessionState()

        render()

        # Should have set expense_page to 1
        assert mock_st.session_state.get("expense_page") == 1

    @patch("expenses_ai_agent.streamlit.views.expenses.get_client")
    @patch("expenses_ai_agent.streamlit.views.expenses.st")
    def test_render_expenses_delete_success(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test expense delete flow."""
        from expenses_ai_agent.streamlit.views.expenses import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.list_expenses.return_value = {
            "items": [
                {
                    "id": 1,
                    "description": "Coffee",
                    "category": "Food",
                    "amount": "5.50",
                    "currency": "USD",
                    "date": "2024-01-15T10:00:00Z",
                }
            ],
            "total": 1,
            "page": 1,
            "pages": 1,
        }

        mock_st.session_state = MockSessionState(expense_page=1)
        mock_st.columns = create_columns_mock({
            4: [MagicMock(), MagicMock(), MagicMock(), MagicMock()],
            3: [MagicMock(), MagicMock(), MagicMock()],
        })
        mock_st.container.return_value.__enter__ = MagicMock(return_value=None)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=None)

        # Simulate delete button click
        mock_st.button.return_value = True

        render()

        mock_client.delete_expense.assert_called_once_with(1)
        mock_st.success.assert_called()

    @patch("expenses_ai_agent.streamlit.views.expenses.get_client")
    @patch("expenses_ai_agent.streamlit.views.expenses.st")
    def test_render_expenses_delete_error(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test expense delete error handling."""
        from expenses_ai_agent.streamlit.views.expenses import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.list_expenses.return_value = {
            "items": [
                {
                    "id": 1,
                    "description": "Coffee",
                    "category": "Food",
                    "amount": "5.50",
                    "currency": "USD",
                    "date": "2024-01-15T10:00:00Z",
                }
            ],
            "total": 1,
            "page": 1,
            "pages": 1,
        }
        mock_client.delete_expense.side_effect = Exception("Delete failed")

        mock_st.session_state = MockSessionState(expense_page=1)
        mock_st.columns = create_columns_mock({
            4: [MagicMock(), MagicMock(), MagicMock(), MagicMock()],
            3: [MagicMock(), MagicMock(), MagicMock()],
        })
        mock_st.container.return_value.__enter__ = MagicMock(return_value=None)
        mock_st.container.return_value.__exit__ = MagicMock(return_value=None)
        mock_st.button.return_value = True

        render()

        error_calls = [str(call) for call in mock_st.error.call_args_list]
        assert any("delete" in str(call).lower() for call in error_calls)


class TestAddExpenseView:
    """Tests for add expense view."""

    @patch("expenses_ai_agent.streamlit.views.add_expense.get_client")
    @patch("expenses_ai_agent.streamlit.views.add_expense.st")
    def test_render_add_expense_form(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test add expense form renders."""
        from expenses_ai_agent.streamlit.views.add_expense import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock form context
        mock_form = MagicMock()
        mock_st.form.return_value.__enter__ = MagicMock(return_value=mock_form)
        mock_st.form.return_value.__exit__ = MagicMock(return_value=None)
        mock_st.form_submit_button.return_value = False

        # Mock expander
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)

        render()

        mock_st.title.assert_called_once_with("Add Expense")
        mock_st.form.assert_called_once_with("expense_form")

    @patch("expenses_ai_agent.streamlit.views.add_expense.get_client")
    @patch("expenses_ai_agent.streamlit.views.add_expense.st")
    def test_render_add_expense_submit_success(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test successful expense submission."""
        from expenses_ai_agent.streamlit.views.add_expense import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.classify_expense.return_value = {
            "id": 1,
            "amount": "5.50",
            "currency": "USD",
            "category": "Food & Dining",
            "confidence": 0.95,
            "comments": "Test comment",
        }

        # Mock form
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock(return_value=None)
        mock_st.text_area.return_value = "Coffee at Starbucks $5.50"
        mock_st.form_submit_button.return_value = True

        # Mock spinner
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=None)

        # Mock columns
        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col]

        # Mock expander
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)

        render()

        mock_client.classify_expense.assert_called_once_with("Coffee at Starbucks $5.50")
        mock_st.success.assert_called()

    @patch("expenses_ai_agent.streamlit.views.add_expense.get_client")
    @patch("expenses_ai_agent.streamlit.views.add_expense.st")
    def test_render_add_expense_validation_error(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test validation error for short description."""
        from expenses_ai_agent.streamlit.views.add_expense import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock form
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock(return_value=None)
        mock_st.text_area.return_value = "ab"  # Too short
        mock_st.form_submit_button.return_value = True

        # Mock expander
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)

        render()

        mock_st.error.assert_called()
        assert "at least 3 characters" in str(mock_st.error.call_args)

    @patch("expenses_ai_agent.streamlit.views.add_expense.get_client")
    @patch("expenses_ai_agent.streamlit.views.add_expense.st")
    def test_render_add_expense_empty_description(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test validation error for empty description."""
        from expenses_ai_agent.streamlit.views.add_expense import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Mock form
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock(return_value=None)
        mock_st.text_area.return_value = ""
        mock_st.form_submit_button.return_value = True

        # Mock expander
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)

        render()

        mock_st.error.assert_called()

    @patch("expenses_ai_agent.streamlit.views.add_expense.get_client")
    @patch("expenses_ai_agent.streamlit.views.add_expense.st")
    def test_render_add_expense_api_error_400(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test 400 error handling."""
        from expenses_ai_agent.streamlit.views.add_expense import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.classify_expense.side_effect = Exception("400 Bad Request")

        # Mock form
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock(return_value=None)
        mock_st.text_area.return_value = "Invalid expense"
        mock_st.form_submit_button.return_value = True

        # Mock spinner
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=None)

        # Mock expander
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)

        render()

        mock_st.error.assert_called()
        error_calls = [str(call) for call in mock_st.error.call_args_list]
        assert any("invalid input" in str(call).lower() for call in error_calls)

    @patch("expenses_ai_agent.streamlit.views.add_expense.get_client")
    @patch("expenses_ai_agent.streamlit.views.add_expense.st")
    def test_render_add_expense_api_error_500(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test 500 error handling."""
        from expenses_ai_agent.streamlit.views.add_expense import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.classify_expense.side_effect = Exception("500 Server Error")

        # Mock form
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock(return_value=None)
        mock_st.text_area.return_value = "Coffee $5"
        mock_st.form_submit_button.return_value = True

        # Mock spinner
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=None)

        # Mock expander
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)

        render()

        mock_st.error.assert_called()
        error_calls = [str(call) for call in mock_st.error.call_args_list]
        assert any("classification failed" in str(call).lower() for call in error_calls)

    @patch("expenses_ai_agent.streamlit.views.add_expense.get_client")
    @patch("expenses_ai_agent.streamlit.views.add_expense.st")
    def test_render_add_expense_api_error_with_response_detail(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test API error with response detail parsing."""
        from expenses_ai_agent.streamlit.views.add_expense import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Create mock exception with response
        mock_response = MagicMock()
        mock_response.json.return_value = {"detail": "total_amount is required"}
        mock_error = Exception("API Error")
        mock_error.response = mock_response
        mock_client.classify_expense.side_effect = mock_error

        # Mock form
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock(return_value=None)
        mock_st.text_area.return_value = "Coffee no amount"
        mock_st.form_submit_button.return_value = True

        # Mock spinner
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=None)

        # Mock expander
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)

        render()

        mock_st.error.assert_called()
        error_calls = [str(call) for call in mock_st.error.call_args_list]
        assert any("amount" in str(call).lower() for call in error_calls)

    @patch("expenses_ai_agent.streamlit.views.add_expense.get_client")
    @patch("expenses_ai_agent.streamlit.views.add_expense.st")
    def test_render_add_expense_no_comments(
        self, mock_st: MagicMock, mock_get_client: MagicMock
    ) -> None:
        """Test successful submission without comments."""
        from expenses_ai_agent.streamlit.views.add_expense import render

        mock_client = MagicMock()
        mock_get_client.return_value = mock_client
        mock_client.classify_expense.return_value = {
            "id": 1,
            "amount": "5.50",
            "currency": "USD",
            "category": "Food & Dining",
            "confidence": 0.95,
            # No comments field
        }

        # Mock form
        mock_st.form.return_value.__enter__ = MagicMock()
        mock_st.form.return_value.__exit__ = MagicMock(return_value=None)
        mock_st.text_area.return_value = "Coffee $5.50"
        mock_st.form_submit_button.return_value = True

        # Mock spinner
        mock_st.spinner.return_value.__enter__ = MagicMock()
        mock_st.spinner.return_value.__exit__ = MagicMock(return_value=None)

        # Mock columns
        mock_col = MagicMock()
        mock_st.columns.return_value = [mock_col, mock_col]

        # Mock expander
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)

        render()

        mock_st.success.assert_called()
        # st.info should not be called for comments when there are none
        info_calls = mock_st.info.call_args_list
        comments_calls = [c for c in info_calls if "comments" in str(c).lower()]
        assert len(comments_calls) == 0
