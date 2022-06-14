from pydantic import BaseModel


class ID(str):
    """A custom scalar for IDs. If passed a pydantic model it an id property
    it will automatically validate to that models id"""

    def __init__(self, value) -> None:
        self.value = value

    @classmethod
    def __get_validators__(cls):
        # one or more validators may be yielded which will be called in the
        # order to validate the input, each validator will receive as an input
        # the value returned from the previous validator
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, BaseModel):
            if hasattr(v, "id"):
                return cls(v.id)
            else:
                raise TypeError("This needs to be a instance of BaseModel with an id")

        if isinstance(v, str):
            return cls(v)

        if isinstance(v, int):
            return cls(str(v))

        raise TypeError(
            "Needs to be either a instance of BaseModel (with an id) or a string"
        )
