from pydantic import BaseModel
from typing import Any, Callable, Generator, Type


class ID(str):
    """A custom scalar for IDs. If passed a pydantic model it an id property
    it will automatically validate to that models id"""

    def __init__(self, value: str) -> None:
        """Initialize the ID"""
        self.value = value

    @classmethod
    def __get_validators__(cls: Type["ID"]) -> Generator[Callable[..., Any], Any, Any]:
        """Get validators"""
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls: Type["ID"], v: Any, *info) -> "ID":
        """Validate the ID"""
        if isinstance(v, BaseModel):
            if hasattr(v, "id"):
                return cls(v.id)  # type: ignore
            else:
                raise TypeError("This needs to be a instance of BaseModel with an id")

        if isinstance(v, str):
            return cls(v)

        if isinstance(v, int):
            return cls(str(v))

        raise TypeError(
            "Needs to be either a instance of BaseModel (with an id) or a string"
        )
