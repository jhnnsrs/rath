import json
from datetime import datetime
from json import JSONEncoder
from typing import Any

from pydantic import BaseModel


class PydanticJsonEncoder(JSONEncoder):
    """
    A JSONEncoder that can serialize pydantic models.
    """
    def default(self, o: Any) -> Any:
        if isinstance(o, BaseModel):
            return o.dict(by_alias=True)
        if isinstance(o, datetime):
            return o.isoformat("T")
        return super().default(o)


def dumps(value: Any):
    """
    Serialize an object to a JSON formatted string using PydanticJsonEncoder.
    :param value: The object to serialize.
    :return: The serialized string.
    """
    return json.dumps(value, cls=PydanticJsonEncoder)
