import pytest
from atomsql import Database, Model, IntegerField, StringField


# --- Models ---
class Account(Model):
    name = StringField()
    balance = IntegerField()


# --- Fixtures ---
@pytest.fixture
def db():
    """Returns a fresh in-memory database with tables registered."""
    database = Database("sqlite:///:memory:")
    database.register(Account)
    return database


# --- Tests ---
def test_atomic_transaction_rollback(db):
    """
    Test that a transaction rolls back ALL changes if an exception occurs
    within the transaction block.
    """
    # 1. Setup Initial State
    acc = Account(name="Cash", balance=100)
    acc.save(db)
    db.commit()

    # Verify initial state
    db.execute("SELECT balance FROM account WHERE name='Cash'")
    assert db.backend.cursor.fetchone()[0] == 100

    # 2. Execute Transaction that Fails
    # We expect a ValueError to bubble up, but the data must be rolled back.
    with pytest.raises(ValueError, match="Something went wrong"):
        with db.transaction():
            # a. Perform a valid update (this should be rolled back)
            acc.balance = 200
            acc.save(db)

            # b. Raise an exception (Simulate crash)
            raise ValueError("Something went wrong calculating taxes!")

    # 3. Verify Rollback
    # Fetch the data again. It should be 100 (initial), NOT 200 (dirty state).
    db.execute("SELECT balance FROM account WHERE name='Cash'")
    final_balance = db.backend.cursor.fetchone()[0]

    assert final_balance == 100, f"Rollback failed! Expected 100, got {final_balance}"


def test_atomic_transaction_commit(db):
    """Test that a successful transaction commits changes."""
    acc = Account(name="Savings", balance=500)
    acc.save(db)
    db.commit()

    with db.transaction():
        acc.balance = 600
        acc.save(db)

    # Should persist without explicit db.commit() because transaction() handles it
    db.execute("SELECT balance FROM account WHERE name='Savings'")
    assert db.backend.cursor.fetchone()[0] == 600
