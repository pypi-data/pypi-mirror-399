import sqlite3
from typing import Any, List, Optional
from .base import DatabaseBackend
from atomsql.fields import IntegerField, StringField, ForeignKey, DecimalField


class SQLiteBackend(DatabaseBackend):
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.connection = None
        self.cursor = None

    @property
    def placeholder_char(self) -> str:
        return "?"

    def connect(self, **kwargs: Any) -> None:
        target = self.db_path if self.db_path else ":memory:"
        self.connection = sqlite3.connect(target, **kwargs)
        self.cursor = self.connection.cursor()

    def disconnect(self) -> None:
        self.connection.close()

    def execute(self, query: str, params: Optional[List] = None) -> Any:
        if params is None:
            params = []
        return self.cursor.execute(query, params)

    def commit(self) -> None:
        self.connection.commit()

    def rollback(self) -> None:
        self.connection.rollback()

    def close(self) -> None:
        self.connection.close()

    def get_field_type(self, field) -> str:
        if isinstance(field, IntegerField):
            return "INTEGER"
        elif isinstance(field, StringField):
            return "TEXT"
        elif isinstance(field, ForeignKey):
            return f'INTEGER REFERENCES "{field.to._table_name}"(id)'
        elif isinstance(field, DecimalField):
            return "TEXT"
        return "TEXT"

    def get_primary_key_constraint(self, column_name: str, field_type: str) -> str:
        return f'"{column_name}" {field_type} PRIMARY KEY AUTOINCREMENT'
