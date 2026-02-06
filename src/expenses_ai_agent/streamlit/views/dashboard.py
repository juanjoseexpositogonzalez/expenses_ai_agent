"""Dashboard page with charts and summary metrics."""

from decimal import Decimal

import pandas as pd
import plotly.express as px
import streamlit as st

from expenses_ai_agent.streamlit.api_client import get_client


def render() -> None:
    """Render the dashboard page."""
    st.title("Dashboard")
    st.caption("Overview of your expense tracking")

    client = get_client()

    try:
        summary = client.get_analytics_summary(months=12)
    except Exception as e:
        st.error(f"Failed to load analytics: {e}")
        return

    # Summary metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        total = Decimal(str(summary["total_expenses"]))
        st.metric("Total Expenses", f"${total:,.2f}")

    with col2:
        st.metric("Expense Count", summary["expense_count"])

    with col3:
        categories_count = len(summary["category_totals"])
        st.metric("Categories", categories_count)

    st.divider()

    # Charts side by side
    chart_col1, chart_col2 = st.columns(2)

    # Category bar chart
    with chart_col1:
        st.subheader("Expenses by Category")

        if summary["category_totals"]:
            category_df = pd.DataFrame(summary["category_totals"])
            category_df["total"] = category_df["total"].apply(
                lambda x: float(Decimal(str(x)))
            )

            fig = px.bar(
                category_df,
                x="category",
                y="total",
                title="",
                labels={"category": "Category", "total": "Amount ($)"},
                color="category",
                color_discrete_sequence=px.colors.qualitative.Set3,
            )
            fig.update_layout(showlegend=False, xaxis_tickangle=-45)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No expenses recorded yet")

    # Monthly line chart
    with chart_col2:
        st.subheader("Monthly Trend")

        if summary["monthly_totals"]:
            monthly_df = pd.DataFrame(summary["monthly_totals"])
            monthly_df["total"] = monthly_df["total"].apply(
                lambda x: float(Decimal(str(x)))
            )

            fig = px.line(
                monthly_df,
                x="month",
                y="total",
                title="",
                labels={"month": "Month", "total": "Amount ($)"},
                markers=True,
            )
            fig.update_traces(line_color="#1f77b4", line_width=2)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No monthly data available")

    # Recent expenses table
    st.divider()
    st.subheader("Recent Expenses")

    try:
        expenses_data = client.list_expenses(page=1, page_size=5)
        items = expenses_data["items"]

        if items:
            df = pd.DataFrame(items)
            df["amount"] = df["amount"].apply(
                lambda x: f"${float(Decimal(str(x))):,.2f}"
            )
            df["date"] = pd.to_datetime(df["date"]).dt.strftime("%Y-%m-%d")

            # Select columns to display
            display_df = df[["date", "description", "category", "amount", "currency"]]
            display_df.columns = ["Date", "Description", "Category", "Amount", "Currency"]

            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.info("No expenses recorded yet. Add your first expense!")

    except Exception as e:
        st.error(f"Failed to load recent expenses: {e}")
