class CategoryNotFoundError(Exception):
    """Raised when a category is not found in the database."""

    def __init__(self, message: str = "Category not found"):
        self.message = message


class ExpenseCreationError(Exception):
    """Raised when there is an error creating an expense."""

    def __init__(self, message: str = "Error creating expense"):
        self.message = message


class ExpenseNotFoundError(Exception):
    """Raised when an expense is not found in the database."""

    def __init__(self, message: str = "Expense not found"):
        self.message = message
