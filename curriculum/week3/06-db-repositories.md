# Database Repositories with SQLModel

Database-backed repositories persist data to SQLite using SQLModel. This lesson covers session management and the difference between owned and injected sessions.


## Why Database Repositories?

In-memory repositories are great for testing, but production needs persistence:

```python
# In-memory - data lost on restart
repo = InMemoryExpenseRepository()
repo.add(expense)
# Restart program... data is gone

# Database - data persists
repo = DBExpenseRepository(db_url="sqlite:///expenses.db")
repo.add(expense)
# Restart program... data is still there
```


## Session Management Patterns

SQLModel uses sessions for database operations. There are two patterns:

### Owned Session (Repository creates it)

```python
class DBExpenseRepo(ExpenseRepository):
    def __init__(self, db_url: str):
        engine = create_engine(db_url)
        self._session = Session(engine)
        self._owns_session = True  # We created it, we manage it
```

### Injected Session (Caller provides it)

```python
class DBExpenseRepo(ExpenseRepository):
    def __init__(self, db_url: str, session: Session | None = None):
        self._db_url = db_url
        if session:
            self._session = session
            self._owns_session = False  # External session, don't close it
        else:
            engine = create_engine(db_url)
            self._session = Session(engine)
            self._owns_session = True
```


## When to Use Each Pattern

| Pattern | Use Case |
|---------|----------|
| Owned session | Standalone repo, simple CRUD |
| Injected session | Transactions across multiple repos |
| Injected session | Testing with in-memory database |


## DBExpenseRepo Implementation

```python
from sqlmodel import Session, create_engine, select

class DBExpenseRepo(ExpenseRepository):
    def __init__(self, db_url: str, session: Session | None = None):
        self._db_url = db_url
        if session:
            self._session = session
            self._owns_session = False
        else:
            engine = create_engine(db_url)
            SQLModel.metadata.create_all(engine)
            self._session = Session(engine)
            self._owns_session = True

    def add(self, expense: Expense) -> None:
        self._session.add(expense)
        self._session.commit()
        self._session.refresh(expense)

    def get(self, expense_id: int) -> Expense | None:
        return self._session.get(Expense, expense_id)

    def list(self) -> list[Expense]:
        statement = select(Expense)
        return list(self._session.exec(statement))

    def delete(self, expense_id: int) -> None:
        expense = self.get(expense_id)
        if not expense:
            raise ExpenseNotFoundError(expense_id)
        self._session.delete(expense)
        self._session.commit()

    def search_by_category(self, category: ExpenseCategory) -> list[Expense]:
        statement = select(Expense).where(Expense.category_id == category.id)
        return list(self._session.exec(statement))
```


## Testing with Injected Sessions

```python
@pytest.fixture
def db_session():
    """Create an in-memory test session."""
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


def test_expense_repo(db_session):
    # Inject the test session
    repo = DBExpenseRepo(db_url="sqlite:///:memory:", session=db_session)

    expense = Expense(amount=Decimal("10"), currency=Currency.EUR)
    repo.add(expense)

    assert repo.get(expense.id) is not None
```


## Python Comparison

| Pattern | Direct SQL | SQLModel Repository |
|---------|-----------|---------------------|
| Connection | `conn = sqlite3.connect(...)` | `engine = create_engine(...)` |
| Query | `cursor.execute("SELECT...")` | `session.exec(select(...))` |
| Insert | `cursor.execute("INSERT...")` | `session.add(expense)` |
| Commit | `conn.commit()` | `session.commit()` |


## Database Repositories in Our Project

| Repository | Methods | Purpose |
|------------|---------|---------|
| `DBCategoryRepo` | add, get, list, update, delete | Manage categories |
| `DBExpenseRepo` | add, get, list, delete, search_by_category, search_by_dates, list_by_user | Manage expenses |


## Further Reading

- [SQLModel Documentation](https://sqlmodel.tiangolo.com/)
- [SQLAlchemy Session](https://docs.sqlalchemy.org/en/20/orm/session.html)
- [SQLModel Relationships](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/)
