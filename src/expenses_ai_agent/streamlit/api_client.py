"""HTTP client for FastAPI backend."""

from decimal import Decimal
from typing import Any

import httpx
from decouple import config


class APIClient:
    """Client for interacting with the Expenses API."""

    def __init__(
        self,
        base_url: str | None = None,
        user_id: int | None = None,
    ) -> None:
        """Initialize API client.

        Args:
            base_url: API base URL. Defaults to API_BASE_URL env var.
            user_id: User ID for requests. Defaults to DEFAULT_USER_ID env var.
        """
        self.base_url = base_url or config(
            "API_BASE_URL", default="http://localhost:8000/api/v1", cast=str
        )
        self.user_id = user_id or config("DEFAULT_USER_ID", default=12345, cast=int)
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"X-User-ID": str(self.user_id)},
            timeout=30.0,
        )

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self) -> "APIClient":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    # ------------------------------------------------------------------
    # Expenses
    # ------------------------------------------------------------------

    def list_expenses(
        self, page: int = 1, page_size: int = 20
    ) -> dict[str, Any]:
        """List expenses with pagination.

        Args:
            page: Page number (1-indexed).
            page_size: Items per page.

        Returns:
            Paginated expense list response.
        """
        response = self._client.get(
            "/expenses/",
            params={"page": page, "page_size": page_size},
        )
        response.raise_for_status()
        return response.json()

    def classify_expense(self, description: str) -> dict[str, Any]:
        """Classify and persist a new expense.

        Args:
            description: Natural language expense description.

        Returns:
            Classified expense response.
        """
        response = self._client.post(
            "/expenses/classify",
            json={"description": description},
        )
        response.raise_for_status()
        return response.json()

    def delete_expense(self, expense_id: int) -> None:
        """Delete an expense.

        Args:
            expense_id: The expense ID to delete.
        """
        response = self._client.delete(f"/expenses/{expense_id}")
        response.raise_for_status()

    def get_users(self) -> list[int]:
        """Get list of unique user IDs that have expenses.

        Returns:
            List of user IDs.
        """
        response = self._client.get("/expenses/users/")
        response.raise_for_status()
        return response.json()

    def set_user_id(self, user_id: int) -> None:
        """Update the user ID for all future requests.

        Args:
            user_id: The new user ID to use.
        """
        self.user_id = user_id
        self._client.headers["X-User-ID"] = str(user_id)

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_analytics_summary(self, months: int = 12) -> dict[str, Any]:
        """Get analytics summary for dashboard.

        Args:
            months: Number of months of data.

        Returns:
            Analytics summary with category and monthly totals.
        """
        response = self._client.get(
            "/analytics/summary",
            params={"months": months},
        )
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Categories
    # ------------------------------------------------------------------

    def list_categories(self) -> list[dict[str, Any]]:
        """List all expense categories.

        Returns:
            List of categories.
        """
        response = self._client.get("/categories/")
        response.raise_for_status()
        return response.json()

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------

    def health_check(self) -> bool:
        """Check API health.

        Returns:
            True if API is healthy, False otherwise.
        """
        try:
            # Health endpoint is at root, not under /api/v1
            base = self.base_url.replace("/api/v1", "")
            response = httpx.get(f"{base}/health", timeout=5.0)
            return response.status_code == 200
        except httpx.HTTPError:
            return False


# Singleton for Streamlit caching
_client: APIClient | None = None


def get_client() -> APIClient:
    """Get or create API client singleton.

    Uses DEFAULT_USER_ID from .env for all requests.

    Returns:
        The API client instance.
    """
    global _client
    if _client is None:
        _client = APIClient()
    return _client
