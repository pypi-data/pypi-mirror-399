from typing import Any, Tuple, List, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Model


class BinaryExpression:
    def __init__(self, field: "Field", operator: str, value: Any):
        self.field = field
        self.operator = operator
        self.value = value

    def to_sql(self) -> Tuple[str, List[Any]]:
        sql = f'"{self.field.name}" {self.operator} ?'
        return sql, [self.value]

    def __repr__(self):
        return f"<BinaryExpression: {self.field.name} {self.operator} {self.value}>"


class Field:
    def __init__(
        self, default: Any = None, unique: bool = False, nullable: bool = True
    ):
        if not isinstance(unique, bool):
            raise TypeError("Option 'unique' must be a boolean")
        if not isinstance(nullable, bool):
            raise TypeError("Option 'nullable' must be a boolean")

        self.default = default
        self.unique = unique
        self.nullable = nullable
        self.name = None

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)

    def __set__(self, instance, value):
        if value is None:
            if not self.nullable:
                raise ValueError(f"Field '{self.name}' cannot be None (nullable=False)")
            instance.__dict__[self.name] = None
            return
        self.validate_type(value)
        instance.__dict__[self.name] = value

    def validate_type(self, value):
        raise NotImplementedError

    def get_sql_type(self) -> str:
        return "TEXT"

    def get_column_name(self) -> str:
        """Return the actual column name to use in the database."""
        return self.name

    def to_sql_value(self, instance: Any) -> Any:
        return getattr(instance, self.name)

    def __eq__(self, value: Any) -> BinaryExpression:
        return BinaryExpression(self, "=", value)

    def __ne__(self, value: Any) -> BinaryExpression:
        return BinaryExpression(self, "!=", value)

    def __lt__(self, value: Any) -> BinaryExpression:
        return BinaryExpression(self, "<", value)

    def __le__(self, value: Any) -> BinaryExpression:
        return BinaryExpression(self, "<=", value)

    def __gt__(self, value: Any) -> BinaryExpression:
        return BinaryExpression(self, ">", value)

    def __ge__(self, value: Any) -> BinaryExpression:
        return BinaryExpression(self, ">=", value)


class IntegerField(Field):
    def validate_type(self, value):
        if value is None and self.nullable:
            return
        if not isinstance(value, int):
            raise ValueError(f"Field '{self.name}' expected an int, got {type(value)}.")

    def __set__(self, instance, value):
        self.validate_type(value)
        return super().__set__(instance, value)


class StringField(Field):
    def validate_type(self, value):
        if not isinstance(value, str):
            raise ValueError(f"Field '{self.name}' expected a str, got {type(value)}.")

    def __set__(self, instance, value):
        self.validate_type(value)
        return super().__set__(instance, value)


class DecimalField(Field):
    def validate_type(self, value):
        if not isinstance(value, float):
            raise ValueError(
                f"Field '{self.name}' expected a float, got {type(value)}."
            )

    def __set__(self, instance, value):
        self.validate_type(value)
        return super().__set__(instance, value)


class ReverseRelation:
    def __init__(self, related_model: Type["Model"], field_name: str):
        self.related_model = related_model
        self.field_name = field_name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        fk_field = self.related_model._fields[self.field_name]
        column_name = fk_field.get_column_name()

        return self.related_model.filter(**{column_name: instance.id})


class ForeignKey(Field):
    def __init__(
        self, to: Type["Model"], nullable: bool = False, related_name: str = None
    ):
        super().__init__(nullable=nullable)
        self.to = to
        self.related_name = related_name

    def __set_name__(self, owner, name):
        self.name = name
        if self.related_name:
            back_ref_name = self.related_name
        else:
            back_ref_name = f"{owner._table_name}_set"

        if not hasattr(self.to, back_ref_name):
            setattr(self.to, back_ref_name, ReverseRelation(owner, name))

    def get_sql_type(self) -> str:
        return "INTEGER"

    def get_column_name(self) -> str:
        """ForeignKey columns have _id suffix."""
        return f"{self.name}_id"

    def __set__(self, instance, value):
        if value is None:
            if not self.nullable:
                raise ValueError(f"Field '{self.name}' cannot be None (nullable=False)")
            instance.__dict__[f"{self.name}_id"] = None
            instance.__dict__[f"_{self.name}_cache"] = None
            return
        if isinstance(value, self.to):
            instance.__dict__[f"_{self.name}_cache"] = value
            if hasattr(value, "id"):
                instance.__dict__[f"{self.name}_id"] = getattr(value, "id")
        elif isinstance(value, int):
            instance.__dict__[f"{self.name}_id"] = value
            instance.__dict__[f"_{self.name}_cache"] = None
        else:
            raise ValueError(
                f"Expected {self.to.__name__} instance or int ID, got {type(value)}."
            )

    def __get__(self, instance, owner):
        if instance is None:
            return self
        cached = instance.__dict__.get(f"_{self.name}_cache")
        if cached is not None:
            return cached
        fk_id = instance.__dict__.get(f"{self.name}_id")
        if fk_id is not None:
            related_instance = self.to.get(fk_id)
            instance.__dict__[f"_{self.name}_cache"] = related_instance
            return related_instance
        return None

    def to_sql_value(self, instance: Any) -> Any:
        return instance.__dict__.get(f"{self.name}_id")
