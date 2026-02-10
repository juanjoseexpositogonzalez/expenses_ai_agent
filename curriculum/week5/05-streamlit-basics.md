# Streamlit Dashboard Patterns

Streamlit turns Python scripts into interactive web applications. This lesson covers the patterns you'll use to build the expense dashboard.


## Why Streamlit Exists

Building a traditional web frontend requires:

- HTML templates
- CSS styling
- JavaScript for interactivity
- Build tools (webpack, vite)
- Framework knowledge (React, Vue, Angular)

Streamlit eliminates this complexity:

```python
import streamlit as st

st.title("Expense Dashboard")
description = st.text_input("Expense description")
if st.button("Classify"):
    result = api_client.classify(description)
    st.success(f"Classified as {result['category']}")
```

This is the entire application - no HTML, no CSS, no JavaScript. Streamlit handles rendering, state management, and reactivity.


## How Streamlit Works

Streamlit scripts run top-to-bottom on every interaction:

```python
import streamlit as st

st.write("This runs every time")

counter = st.session_state.get("counter", 0)

if st.button("Increment"):
    counter += 1
    st.session_state["counter"] = counter

st.write(f"Count: {counter}")
```

When the user clicks "Increment":
1. The script reruns from the top
2. `counter` loads from session_state
3. The button condition is True (it was clicked)
4. Counter increments and saves to session_state
5. UI updates with new value

**Key insight:** Streamlit is a stateless script that appears stateful because of session_state.


## Sidebar Navigation

Create a multi-page app with sidebar navigation:

```python
import streamlit as st

st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Select page",
    ["Dashboard", "Expenses", "Add Expense"]
)

if page == "Dashboard":
    render_dashboard()
elif page == "Expenses":
    render_expenses()
elif page == "Add Expense":
    render_add_expense()
```

Each page is a function that renders its content:

```python
def render_dashboard():
    st.header("Dashboard")
    summary = api_client.get_summary()
    # Display charts...

def render_expenses():
    st.header("Expenses")
    expenses = api_client.get_expenses()
    # Display table...

def render_add_expense():
    st.header("Add Expense")
    description = st.text_input("Description")
    # Handle form...
```


## Session State

Persist data across reruns with `st.session_state`:

```python
# Initialize state
if "user_id" not in st.session_state:
    st.session_state["user_id"] = 12345

# Use state
user_id = st.session_state["user_id"]

# Update state
if st.button("Change User"):
    st.session_state["user_id"] = new_user_id
```

**When to use session_state:**
- User settings (current page, filters)
- Form data that needs to persist
- Cached API responses
- Any data that shouldn't reset on rerun


## Display Elements

Streamlit provides many display components:

```python
# Text
st.title("Main Title")
st.header("Section Header")
st.subheader("Subsection")
st.write("Regular text or any Python object")
st.markdown("**Bold** and *italic*")

# Data
st.dataframe(df)  # Interactive table
st.table(df)      # Static table
st.json(data)     # JSON viewer
st.metric("Total", "$1,234", delta="+$50")

# Status
st.success("Operation completed!")
st.error("Something went wrong")
st.warning("Be careful")
st.info("Just so you know")

# Media
st.image("path/to/image.png")
st.plotly_chart(fig)
```


## Input Widgets

Capture user input with widgets:

```python
# Text
text = st.text_input("Enter text")
area = st.text_area("Longer text")

# Numbers
number = st.number_input("Amount", min_value=0.0)
slider = st.slider("Range", 0, 100, 50)

# Selection
choice = st.selectbox("Pick one", ["A", "B", "C"])
multi = st.multiselect("Pick many", ["A", "B", "C"])
radio = st.radio("Choose", ["Option 1", "Option 2"])

# Actions
if st.button("Submit"):
    # Handle button click
    pass
```


## Plotly Integration

Create interactive charts with Plotly:

```python
import plotly.express as px
import streamlit as st

# Bar chart for category totals
fig = px.bar(
    category_data,
    x="category",
    y="total",
    title="Spending by Category",
    color="category",
)
st.plotly_chart(fig, use_container_width=True)

# Line chart for monthly trends
fig = px.line(
    monthly_data,
    x="month",
    y="total",
    title="Monthly Spending",
    markers=True,
)
st.plotly_chart(fig, use_container_width=True)
```

`use_container_width=True` makes charts responsive to the page width.


## Caching API Calls

Avoid redundant API calls with `st.cache_data`:

```python
@st.cache_data(ttl=60)  # Cache for 60 seconds
def fetch_summary(user_id: int):
    """Fetch analytics summary from API."""
    return api_client.get_summary(user_id)

# Cached call - only hits API if cache expired
summary = fetch_summary(user_id)
```

**When to cache:**
- Read-only data that doesn't change frequently
- Expensive API calls
- Data shared across reruns


## Python Comparison

| Traditional web | Streamlit |
|-----------------|-----------|
| HTML/CSS/JS | Python only |
| Build step | Run directly |
| State management libraries | st.session_state |
| Routing configuration | Sidebar navigation |
| Chart libraries + integration | st.plotly_chart() |


## Streamlit in Our Project

| File | Purpose |
|------|---------|
| `streamlit/app.py` | Main app with navigation |
| `streamlit/api_client.py` | HTTP client for FastAPI |
| `streamlit/views/dashboard.py` | Analytics charts |
| `streamlit/views/expenses.py` | Expense list |
| `streamlit/views/add_expense.py` | Classification form |


## Further Reading

- [Streamlit Documentation](https://docs.streamlit.io/)
- [Streamlit Session State](https://docs.streamlit.io/library/api-reference/session-state)
- [Plotly Express](https://plotly.com/python/plotly-express/)
