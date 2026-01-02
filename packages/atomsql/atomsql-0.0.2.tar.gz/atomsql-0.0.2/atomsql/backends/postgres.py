from typing import Any, List, Optional, TYPE_CHECKING
from .base import DatabaseBackend
from atomsql.fields import IntegerField, StringField, ForeignKey, DecimalField

if TYPE_CHECKING:
    import psycopg


class PostgresBackend(DatabaseBackend):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.connection: Optional["psycopg.Connection"] = None
        self.cursor: Optional["psycopg.Cursor"] = None

    def connect(self, **kwargs: Any) -> None:
        import psycopg

        self.connection = psycopg.connect(self.db_path, **kwargs)
        self.cursor = self.connection.cursor()

    def disconnect(self) -> None:
        if self.connection:
            self.connection.close()

    def execute(self, query: str, params: Optional[List] = None) -> Any:
        if params is None:
            params = []
        return self.cursor.execute(query, params)

    def commit(self) -> None:
        if self.connection:
            self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def close(self) -> None:
        self.disconnect()

    def get_field_type(self, field) -> str:
        if isinstance(field, IntegerField):
            return "INTEGER"
        elif isinstance(field, StringField):
            return "TEXT"
        elif isinstance(field, ForeignKey):
            return f'INTEGER REFERENCES "{field.to._table_name}"(id)'
        elif isinstance(field, DecimalField):
            return "NUMERIC"
        return "TEXT"

    def get_primary_key_constraint(self, column_name, field_type):
        return f'"{column_name}" SERIAL PRIMARY KEY'

    @property
    def placeholder_char(self) -> str:
        return "%s"
