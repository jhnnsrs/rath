from pydantic import BaseModel
from typing import Any, Type, Protocol
from pydantic import GetCoreSchemaHandler
from pydantic_core import CoreSchema, core_schema


class ID(str):
    """A custom scalar for IDs. If passed a pydantic model it an id property
    it will automatically validate to that models id"""

    def __get__(self, instance, owner) -> "ID": ...

    def __set__(self, instance, value: "IDCoercible") -> None: ...

    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        source_type: Any,  # noqa: ANN401
        handler: GetCoreSchemaHandler,  # noqa: ANN401
    ) -> CoreSchema:
        """Get the pydantic core schema for the interface"""
        return core_schema.no_info_before_validator_function(cls.validate, handler(str))

    @classmethod
    def validate(cls: Type["ID"], v: "IDCoercible") -> "ID":
        """Validate the ID"""
        if isinstance(v, BaseModel):
            if hasattr(v, "id"):
                return cls(v.id)  # type: ignore
            else:
                raise ValueError("It appears to be a pydantic model but has no id")

        if isinstance(v, str):
            return cls(v)

        if isinstance(v, int):
            return cls(str(v))

        raise TypeError(
            f"Needs to be either a instance of BaseModel (with an id) or a string got {type(v)}"
        )


class WithId(Protocol):
    "A protocol for objects that have an id attribute."

    id: "IDCoercible"


IDCoercible = str | ID | WithId | int
""" A type that can be coerced into an ID."""
