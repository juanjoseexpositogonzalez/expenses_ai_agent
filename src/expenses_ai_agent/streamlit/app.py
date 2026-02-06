"""Main Streamlit application for expense tracking dashboard."""

import streamlit as st

from expenses_ai_agent.streamlit.api_client import get_client

# Page configuration
st.set_page_config(
    page_title="Expenses AI Agent",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Check API health
client = get_client()
api_healthy = client.health_check()

# Sidebar navigation
st.sidebar.title("💰 Expenses AI Agent")

if not api_healthy:
    st.sidebar.error("API is not available")
    st.error(
        "Cannot connect to the API. Please ensure the FastAPI server is running:\n\n"
        "```bash\nuvicorn expenses_ai_agent.api.main:app --reload\n```"
    )
    st.stop()

st.sidebar.success("API Connected")

# Navigation
page = st.sidebar.radio(
    "Navigation",
    ["Dashboard", "Expenses", "Add Expense"],
    label_visibility="collapsed",
)

st.sidebar.divider()
st.sidebar.caption("Powered by AI classification")

# Route to pages
if page == "Dashboard":
    from expenses_ai_agent.streamlit.pages.dashboard import render

    render()
elif page == "Expenses":
    from expenses_ai_agent.streamlit.pages.expenses import render

    render()
elif page == "Add Expense":
    from expenses_ai_agent.streamlit.pages.add_expense import render

    render()
