import json
from datetime import datetime
from json import JSONEncoder
from typing import Any

from pydantic import BaseModel


class PydanticJsonEncoder(JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, BaseModel):
            return o.dict(by_alias=True)
        if isinstance(o, datetime):
            return o.isoformat("T")


def dumps(value: Any):
    return json.dumps(value, cls=PydanticJsonEncoder)
