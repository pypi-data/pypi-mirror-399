from typing import Literal, cast

from pydantic.fields import FieldInfo


def get_dspy_field_type(field: FieldInfo) -> Literal["input", "output"]:
    extra = field.json_schema_extra if field.json_schema_extra and not callable(field.json_schema_extra) else {}
    field_type = extra.get("__dspy_field_type")
    if field_type is None:
        raise ValueError(f"Field {field} does not have a __dspy_field_type")
    assert field_type in ("input", "output")
    return cast(Literal["input", "output"], field_type)
