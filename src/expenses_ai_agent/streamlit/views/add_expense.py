"""Add expense page with classification form."""

from decimal import Decimal

import streamlit as st

from expenses_ai_agent.streamlit.api_client import get_client


def render() -> None:
    """Render the add expense page."""
    st.title("Add Expense")
    st.caption("Classify and record a new expense using AI")

    client = get_client()

    # Input form
    with st.form("expense_form"):
        description = st.text_area(
            "Expense Description",
            placeholder="Enter your expense description...\n\nExamples:\n- Coffee at Starbucks $5.50\n- Uber ride to airport 25 EUR\n- Monthly Netflix subscription 15.99",
            height=120,
        )

        submitted = st.form_submit_button("Classify & Save", type="primary")

    if submitted:
        if not description or len(description.strip()) < 3:
            st.error("Please enter a valid expense description (at least 3 characters)")
            return

        with st.spinner("Classifying expense..."):
            try:
                result = client.classify_expense(description.strip())

                st.success("Expense classified and saved!")

                # Display result
                st.divider()
                st.subheader("Classification Result")

                col1, col2 = st.columns(2)

                with col1:
                    amount = Decimal(str(result["amount"]))
                    st.metric("Amount", f"${amount:,.2f} {result['currency']}")
                    st.metric("Category", result["category"])

                with col2:
                    confidence = result["confidence"]
                    confidence_color = (
                        "green"
                        if confidence > 0.8
                        else "orange"
                        if confidence > 0.5
                        else "red"
                    )
                    st.metric("Confidence", f"{confidence:.0%}")
                    st.metric("Expense ID", result["id"])

                if result.get("comments"):
                    st.info(f"Comments: {result['comments']}")

            except Exception as e:
                error_msg = str(e)
                if "400" in error_msg:
                    st.error("Invalid input. Please check your expense description.")
                elif "500" in error_msg:
                    st.error("Classification failed. Please try again.")
                else:
                    st.error(f"Error: {e}")

    # Tips section
    st.divider()
    with st.expander("Tips for better classification"):
        st.markdown("""
        For best results, include:
        - **Amount** with currency symbol ($5.50, 25 EUR, £15)
        - **Description** of what you purchased
        - **Location or vendor** name if applicable

        **Examples:**
        - "Coffee and croissant at Starbucks $8.50"
        - "Uber from home to JFK airport 45 USD"
        - "Monthly Spotify subscription 9.99 EUR"
        - "Groceries at Whole Foods $127.34"
        - "Electric bill for January 89.50"
        """)
