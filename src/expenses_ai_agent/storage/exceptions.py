class CategoryNotFoundError(Exception):
    """Raised when a category is not found in the database."""

    def __init__(self, message: str = "Category not found"):
        self.message = message


class ExpenseNotFoundError(Exception):
    """Raised when an expense is not found in the database."""

    def __init__(self, message: str = "Expense not found"):
        self.message = message
