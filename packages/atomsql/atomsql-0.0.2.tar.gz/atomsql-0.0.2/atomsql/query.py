from typing import Type, Any, TypeVar, TYPE_CHECKING, Iterable, Optional
import functools

if TYPE_CHECKING:
    from .models import Model
    from .db import Database

T = TypeVar("T", bound="Model")


def aggregate_method(func):
    @functools.wraps(func)
    def wrapper(self: "QuerySet[T]", *args, **kwargs) -> Any:
        agg_expression = func(self, *args, **kwargs)
        sql, params = self._build_sql(select_expression=agg_expression)
        cursor = self.db.backend.execute(sql, params)
        result = cursor.fetchone()
        return result[0] if result else None

    return wrapper


class QuerySet(Iterable[T]):
    def __init__(self, model_cls: Type[T], db: "Database"):
        self.model_cls = model_cls
        self.db = db
        self._filters = {}
        self._order_by: Optional[str] = None
        self._limit: Optional[int] = None
        self._offset: Optional[int] = None
        self.related_fields = []

    def filter(self, **kwargs: Any) -> "QuerySet[T]":
        self._filters.update(kwargs)
        return self

    @property
    def related_field(self):
        return self.related_fields

    @related_field.setter
    def related_field(self, value):
        self.related_fields = value

    def select_related(self, field_name: str) -> "QuerySet[T]":
        if field_name not in self.model_cls._fields:
            raise ValueError(
                f"Field '{field_name}' does not exist on model '{self.model_cls.__name__}'"
            )
        self.related_fields.append(field_name)
        return self

    def order_by(self, field_name: str) -> "QuerySet[T]":
        self._order_by = field_name
        return self

    def limit(self, limit: int) -> "QuerySet[T]":
        self._limit = limit
        return self

    def offset(self, offset: int) -> "QuerySet[T]":
        self._offset = offset
        return self

    @aggregate_method
    def count(self) -> str:
        return "COUNT(*)"

    @aggregate_method
    def sum(self, field_name: str) -> str:
        if field_name not in self.model_cls._fields:
            raise ValueError(
                f"Field '{field_name}' does not exist on model '{self.model_cls.__name__}'"
            )
        return f'SUM("{field_name}")'

    @aggregate_method
    def avg(self, field_name: str) -> str:
        if field_name not in self.model_cls._fields:
            raise ValueError(
                f"Field '{field_name}' does not exist on model '{self.model_cls.__name__}'"
            )
        return f'AVG("{field_name}")'

    def _build_sql(self, select_expression: Optional[str] = None):
        table_name = f'"{self.model_cls._table_name}"'
        columns = [
            f'{table_name}."{field.get_column_name()}"'
            for field in self.model_cls._fields.values()
        ]
        joins = []
        related_columns = {}

        for field_name in self.related_field:
            fk_field = self.model_cls._fields.get(field_name)
            if not fk_field or not hasattr(fk_field, "to"):
                raise ValueError(
                    f"Field '{field_name}' is not a valid ForeignKey field on model '{self.model_cls.__name__}'"
                )
            related_model = fk_field.to
            related_table_name = f'"{related_model._table_name}"'

            related_columns[field_name] = []
            for related_field in related_model._fields.values():
                col_name = related_field.get_column_name()
                alias = f'{related_table_name}."{col_name}"'
                columns.append(alias)
                related_columns[field_name].append(col_name)

            joins.append(
                f'LEFT JOIN {related_table_name} ON {table_name}."{fk_field.get_column_name()}" = {related_table_name}."id"'
            )

        if select_expression is None:
            select_expression = ", ".join(columns)

        sql = f"SELECT {select_expression} FROM {table_name}"

        if joins:
            sql += " " + " ".join(joins)

        params = []

        if self._filters:
            sql += " WHERE "
            conditions = []
            for key, value in self._filters.items():
                conditions.append(f'"{key}" = {self.db.backend.placeholder_char}')
                params.append(value)
            sql += " AND ".join(conditions)

        if self._order_by:
            direction = "DESC" if self._order_by.startswith("-") else "ASC"
            field_name = self._order_by.lstrip("-")
            sql += f' ORDER BY "{field_name}" {direction}'

        if self._limit:
            sql += f" LIMIT {self._limit}"

        if self._offset:
            sql += f" OFFSET {self._offset}"

        return sql, params

    def _hydrate_rows(self, rows: tuple, description: tuple) -> Any:
        idx = 0

        model_data = {}
        for field_name, field in self.model_cls._fields.items():
            model_data[field_name] = rows[idx]
            idx += 1

        instance = self.model_cls(**model_data)

        for related_field in self.related_field:
            fk_field = self.model_cls._fields.get(related_field)
            related_model = fk_field.to

            related_data = {}
            has_data = False
            for rel_field_name, rel_field in related_model._fields.items():
                value = rows[idx]
                related_data[rel_field_name] = value
                if value is not None:
                    has_data = True
                idx += 1

            if has_data:
                related_instance = related_model(**related_data)
                instance.__dict__[f"_{related_field}_cache"] = related_instance
                instance.__dict__[f"{related_field}_id"] = related_instance.id

        return instance

    def __iter__(self):
        sql, params = self._build_sql()
        cursor = self.db.backend.execute(sql, params)
        while True:
            row = cursor.fetchone()
            if not row:
                break
            yield self._hydrate_rows(row, cursor.description)

    def __len__(self):
        """Return the count of results."""
        sql, params = self._build_sql(select_expression="COUNT(*)")
        cursor = self.db.backend.execute(sql, params)
        result = cursor.fetchone()
        return result[0] if result else 0

    def __getitem__(self, index):
        """Support indexing and slicing."""
        if isinstance(index, slice):
            start = index.start or 0
            stop = index.stop
            step = index.step or 1

            if step != 1:
                raise ValueError("QuerySet slicing with step is not supported")

            query = QuerySet(self.model_cls, self.db)
            query._filters = self._filters.copy()
            query._order_by = self._order_by
            query.related_field = self.related_field.copy()
            query._offset = start
            if stop is not None:
                query._limit = stop - start
            return list(query)
        else:
            if index < 0:
                raise IndexError("Negative indexing is not supported")

            query = QuerySet(self.model_cls, self.db)
            query._filters = self._filters.copy()
            query._order_by = self._order_by
            query.related_field = self.related_field.copy()
            query._offset = index
            query._limit = 1
            results = list(query)
            if not results:
                raise IndexError("QuerySet index out of range")
            return results[0]

    def __eq__(self, other):
        """Support equality comparison."""
        if isinstance(other, list):
            return list(self) == other
        return super().__eq__(other)
