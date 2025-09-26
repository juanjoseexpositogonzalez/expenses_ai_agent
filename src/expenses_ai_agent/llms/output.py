from datetime import datetime, timezone
from decimal import Decimal

from pydantic import BaseModel

from expenses_ai_agent.storage.models import Currency


class ExpenseCategorizationResponse(BaseModel):
    category: str
    total_amount: Decimal
    currency: Currency
    confidence: float
    cost: Decimal
    comments: str | None = None
    timestamp: datetime = datetime.now(timezone.utc)
