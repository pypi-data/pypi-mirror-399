import pytest
from atomsql.backends.sqlite import SQLiteBackend
from atomsql.backends.postgres import PostgresBackend
from atomsql.fields import IntegerField, StringField, DecimalField, ForeignKey
from atomsql.models import Model


# Mock a target model for ForeignKey testing
class User(Model):
    name = StringField()


# --- Fixtures ---
@pytest.fixture
def sqlite_backend():
    return SQLiteBackend("sqlite:///:memory:")


@pytest.fixture
def pg_backend():
    # We don't need real credentials just to test type mapping logic
    # Pass a mock connection string
    return PostgresBackend("postgresql://admin@localhost/test_db")


# --- Tests ---


def test_sqlite_type_mapping(sqlite_backend):
    """Verify SQLite uses TEXT for Decimals and INTEGER for PKs."""

    # 1. Decimal -> TEXT
    assert sqlite_backend.get_field_type(DecimalField()) == "TEXT"

    # 2. Integer -> INTEGER
    assert sqlite_backend.get_field_type(IntegerField()) == "INTEGER"

    # 3. String -> TEXT
    assert sqlite_backend.get_field_type(StringField()) == "TEXT"

    # 4. Primary Key Constraint
    # In SQLite, it MUST be 'INTEGER PRIMARY KEY AUTOINCREMENT'
    pk_constraint = sqlite_backend.get_primary_key_constraint("id", "INTEGER")
    assert pk_constraint == '"id" INTEGER PRIMARY KEY AUTOINCREMENT'


def test_postgres_type_mapping(pg_backend):
    """Verify Postgres uses NUMERIC for Decimals and SERIAL for PKs."""

    # 1. Decimal -> NUMERIC (High precision native support)
    assert pg_backend.get_field_type(DecimalField()) == "NUMERIC"

    # 2. Integer -> INTEGER
    assert pg_backend.get_field_type(IntegerField()) == "INTEGER"

    # 3. Primary Key -> SERIAL
    # The field type itself might be INTEGER, but the constraint generator handles SERIAL
    pk_constraint = pg_backend.get_primary_key_constraint("id", "INTEGER")
    assert pk_constraint == '"id" SERIAL PRIMARY KEY'


def test_foreign_key_mapping(sqlite_backend, pg_backend):
    """Verify FKs resolve to the correct table reference syntax."""
    fk = ForeignKey(User)

    # Both backends usually share similar syntax for FKs,
    # but let's ensure they are generating valid SQL.

    sqlite_sql = sqlite_backend.get_field_type(fk)
    assert 'REFERENCES "user"(id)' in sqlite_sql
    assert sqlite_sql.startswith("INTEGER")

    pg_sql = pg_backend.get_field_type(fk)
    assert 'REFERENCES "user"(id)' in pg_sql
