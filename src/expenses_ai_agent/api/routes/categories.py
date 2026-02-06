"""Category endpoints."""

from fastapi import APIRouter

from expenses_ai_agent.api.deps import CategoryRepoDep

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/")
def list_categories(category_repo: CategoryRepoDep) -> list[dict[str, str | int]]:
    """List all expense categories."""
    categories = category_repo.list()
    return [{"id": c.id, "name": c.name} for c in categories]
