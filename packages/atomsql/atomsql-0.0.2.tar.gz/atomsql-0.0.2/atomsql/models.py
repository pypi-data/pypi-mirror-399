from .fields import Field, IntegerField
from .query import QuerySet
import logging

logger = logging.getLogger(__name__)


class ModelMeta(type):
    models = []

    def __new__(cls, name, bases, attrs):
        if "id" not in attrs:
            attrs["id"] = IntegerField(nullable=True)
        fields = {}
        for key, value in list(attrs.items()):
            if isinstance(value, Field):
                fields[key] = value
        attrs["_fields"] = fields
        attrs["_table_name"] = name.lower()
        new_class = super().__new__(cls, name, bases, attrs)
        new_class._db = None

        if bases:
            cls.models.append(new_class)

        return new_class


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs):
        for name, field in self._fields.items():
            if name in kwargs:
                value = kwargs[name]
            else:
                value = field.default
                if callable(value):
                    value = value()
            setattr(self, name, value)

    def save(self, db_interface=None):
        db_interface = db_interface or self._db
        if db_interface is None:
            raise RuntimeError(
                f"Model {self.__class__.__name__} is not registered to any database."
            )
        table_name = f'"{self._table_name}"'

        if self.id is not None:
            raw_columns = [
                self._fields[col].get_column_name()
                for col in self._fields.keys()
                if col != "id"
            ]
            values = [
                self._fields[col].to_sql_value(self)
                for col in self._fields.keys()
                if col != "id"
            ]
            set_clause = ", ".join(
                [
                    f'"{col}" = {db_interface.backend.placeholder_char}'
                    for col in raw_columns
                ]
            )
            values.append(self.id)

            sql = f"UPDATE {table_name} SET {set_clause} WHERE id = {db_interface.backend.placeholder_char}"
            db_interface.execute(sql, values)
            logger.info(
                f"Updated {self._table_name} with id={self.id}, values: {values[:-1]}"
            )
        else:
            raw_columns = [
                self._fields[col].get_column_name()
                for col in self._fields.keys()
                if col != "id"
            ]
            values = [
                self._fields[col].to_sql_value(self)
                for col in self._fields.keys()
                if col != "id"
            ]
            placeholders = [db_interface.backend.placeholder_char for _ in values]

            sql = f"INSERT INTO {table_name} ({', '.join(raw_columns)}) VALUES ({', '.join(placeholders)})"

            cursor = db_interface.execute(sql, values)
            if hasattr(cursor, "lastrowid") and cursor.lastrowid:
                self.id = cursor.lastrowid

            logger.info(f"Inserted {self._table_name} with values: {values}")

    @classmethod
    def get(cls, pk: int) -> "Model":
        if cls._db is None:
            raise RuntimeError(
                f"Model {cls.__name__} is not registered to any database."
            )
        table_name = f'"{cls._table_name}"'
        columns = ", ".join(
            [f'"{field.get_column_name()}"' for field in cls._fields.values()]
        )

        sql = f"SELECT {columns} FROM {table_name} WHERE id = {cls._db.backend.placeholder_char}"
        cursor = cls._db.backend.execute(sql, [pk])
        row = cursor.fetchone()

        if row:
            data = {}
            for idx, (field_name, field) in enumerate(cls._fields.items()):
                data[field_name] = row[idx]
            return cls(**data)
        return None

    @classmethod
    def objects(cls) -> QuerySet:
        if cls._db is None:
            raise RuntimeError(
                f"Model {cls.__name__} is not registered to any database."
            )
        return QuerySet(cls, cls._db)

    @classmethod
    def all(cls) -> QuerySet:
        return cls.objects()

    @classmethod
    def filter(cls, **kwargs) -> QuerySet:
        return cls.all().filter(**kwargs)
