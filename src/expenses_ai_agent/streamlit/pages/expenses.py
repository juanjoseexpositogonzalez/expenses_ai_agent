"""Expenses list page with pagination and delete."""

from decimal import Decimal

import pandas as pd
import streamlit as st

from expenses_ai_agent.streamlit.api_client import get_client


def render() -> None:
    """Render the expenses list page."""
    st.title("Expenses")
    st.caption("View and manage your expenses")

    client = get_client()

    # Pagination state
    if "expense_page" not in st.session_state:
        st.session_state.expense_page = 1

    page_size = 10

    # Load expenses
    try:
        data = client.list_expenses(
            page=st.session_state.expense_page,
            page_size=page_size,
        )
    except Exception as e:
        st.error(f"Failed to load expenses: {e}")
        return

    items = data["items"]
    total = data["total"]
    pages = data["pages"]

    # Summary
    st.info(f"Showing {len(items)} of {total} expenses (Page {st.session_state.expense_page}/{pages})")

    if not items:
        st.warning("No expenses found. Add your first expense!")
        return

    # Display expenses
    for item in items:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            with col1:
                st.markdown(f"**{item['description'] or 'No description'}**")
                st.caption(f"Category: {item['category'] or 'Uncategorized'}")

            with col2:
                amount = Decimal(str(item["amount"]))
                st.markdown(f"**${amount:,.2f}** {item['currency']}")

            with col3:
                date = pd.to_datetime(item["date"]).strftime("%Y-%m-%d %H:%M")
                st.caption(date)

            with col4:
                if st.button("Delete", key=f"delete_{item['id']}", type="secondary"):
                    try:
                        client.delete_expense(item["id"])
                        st.success("Expense deleted!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete: {e}")

            st.divider()

    # Pagination controls
    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        if st.session_state.expense_page > 1:
            if st.button("← Previous"):
                st.session_state.expense_page -= 1
                st.rerun()

    with col2:
        st.markdown(
            f"<p style='text-align: center'>Page {st.session_state.expense_page} of {pages}</p>",
            unsafe_allow_html=True,
        )

    with col3:
        if st.session_state.expense_page < pages:
            if st.button("Next →"):
                st.session_state.expense_page += 1
                st.rerun()
