# Connecting Streamlit to FastAPI

The Streamlit dashboard needs to communicate with the FastAPI backend. This lesson covers building an API client and handling the request/response cycle.


## Why a Dedicated API Client?

You could make HTTP calls directly in your Streamlit views:

```python
import httpx

def render_dashboard():
    response = httpx.get(
        "http://localhost:8000/api/v1/analytics/summary",
        headers={"X-User-ID": "12345"},
    )
    if response.status_code == 200:
        data = response.json()
        # Display...
```

But this scatters HTTP logic throughout your views. A dedicated client provides:

1. **Single source of configuration** - Base URL, headers in one place
2. **Consistent error handling** - Same pattern for all API calls
3. **Type hints** - Method signatures document the API
4. **Testability** - Mock the client, not individual requests


## ExpenseAPIClient Design

```python
import httpx
from decouple import config

class ExpenseAPIClient:
    """HTTP client for the FastAPI expense API."""

    def __init__(
        self,
        base_url: str = None,
        user_id: int = None,
    ):
        self.base_url = base_url or config("API_BASE_URL", default="http://localhost:8000/api/v1")
        self.user_id = user_id or config("DEFAULT_USER_ID", cast=int, default=12345)

    def _headers(self) -> dict:
        """Build request headers."""
        return {"X-User-ID": str(self.user_id)}

    def get_expenses(self, page: int = 1, page_size: int = 20) -> dict:
        """Get paginated list of expenses."""
        response = httpx.get(
            f"{self.base_url}/expenses/",
            headers=self._headers(),
            params={"page": page, "page_size": page_size},
        )
        response.raise_for_status()
        return response.json()

    def classify_expense(self, description: str) -> dict:
        """Classify an expense using AI."""
        response = httpx.post(
            f"{self.base_url}/expenses/classify",
            headers=self._headers(),
            json={"description": description},
        )
        response.raise_for_status()
        return response.json()

    def get_summary(self) -> dict:
        """Get analytics summary."""
        response = httpx.get(
            f"{self.base_url}/analytics/summary",
            headers=self._headers(),
        )
        response.raise_for_status()
        return response.json()

    def delete_expense(self, expense_id: int) -> None:
        """Delete an expense."""
        response = httpx.delete(
            f"{self.base_url}/expenses/{expense_id}",
            headers=self._headers(),
        )
        response.raise_for_status()

    def health_check(self) -> bool:
        """Check if API is available."""
        try:
            response = httpx.get(f"{self.base_url}/health", timeout=5.0)
            return response.status_code == 200
        except httpx.RequestError:
            return False
```


## Error Handling in Streamlit

Handle API errors gracefully in your views:

```python
import streamlit as st
from httpx import HTTPStatusError, RequestError

def render_dashboard():
    st.header("Dashboard")

    try:
        summary = api_client.get_summary()
        display_charts(summary)
    except HTTPStatusError as e:
        if e.response.status_code == 404:
            st.warning("No expenses found. Add some expenses first!")
        else:
            st.error(f"API error: {e.response.status_code}")
    except RequestError:
        st.error("Cannot connect to API. Is the backend running?")
```

**Best practices:**
- Catch specific exceptions
- Provide actionable error messages
- Don't expose internal details to users


## Health Check on Startup

Check API availability when the app loads:

```python
import streamlit as st

def main():
    st.set_page_config(page_title="Expense Tracker", layout="wide")

    api_client = ExpenseAPIClient()

    # Check API health
    if not api_client.health_check():
        st.error(
            "Cannot connect to the API. "
            "Please ensure the FastAPI server is running on port 8000."
        )
        st.stop()

    # Continue with app...
```

`st.stop()` halts script execution, preventing further errors.


## Using the Client in Views

Pass the client to view functions:

```python
# app.py
def main():
    api_client = ExpenseAPIClient()

    # Navigation
    page = st.sidebar.radio("Navigate", ["Dashboard", "Expenses", "Add Expense"])

    if page == "Dashboard":
        render_dashboard(api_client)
    elif page == "Expenses":
        render_expenses(api_client)
    elif page == "Add Expense":
        render_add_expense(api_client)
```

```python
# views/dashboard.py
def render_dashboard(api_client: ExpenseAPIClient):
    st.header("Dashboard")
    summary = api_client.get_summary()
    # Display charts...
```


## Handling User ID

The API identifies users by the `X-User-ID` header. In Streamlit, you can:

**Option 1: Use a default ID (simplest)**
```python
api_client = ExpenseAPIClient()  # Uses DEFAULT_USER_ID from .env
```

**Option 2: Let users enter their ID**
```python
user_id = st.sidebar.number_input("User ID", value=12345, min_value=1)
api_client = ExpenseAPIClient(user_id=user_id)
```

**Option 3: Session-based (more sophisticated)**
```python
if "user_id" not in st.session_state:
    st.session_state["user_id"] = 12345

api_client = ExpenseAPIClient(user_id=st.session_state["user_id"])
```


## httpx vs requests

| Feature | httpx | requests |
|---------|-------|----------|
| Async support | Yes | No |
| HTTP/2 | Yes | No |
| Timeout handling | Explicit | Defaults to None (infinite) |
| API similarity | Very similar | Standard |

For Streamlit (synchronous), both work. We use httpx because:
- Consistent with async FastAPI patterns
- Better timeout defaults
- Modern Python typing


## API Integration in Our Project

| Component | Purpose |
|-----------|---------|
| `ExpenseAPIClient` | HTTP client with all API methods |
| `api_client.get_expenses()` | Fetch expense list |
| `api_client.classify_expense()` | Classify new expense |
| `api_client.get_summary()` | Fetch analytics data |
| `api_client.delete_expense()` | Remove expense |
| `api_client.health_check()` | Verify API availability |


## Further Reading

- [httpx Documentation](https://www.python-httpx.org/)
- [Streamlit + External APIs](https://docs.streamlit.io/knowledge-base/tutorials/databases)
- [HTTP Status Codes](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status)
