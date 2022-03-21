from typing_extensions import Literal
from typing import List, Optional
from rath.turms.funcs import execute, aexecute
from pydantic import BaseModel, Field


class Beast(BaseModel):
    typename: Optional[Literal["Beast"]] = Field(alias="__typename")
    common_name: Optional[str] = Field(alias="commonName")
    "a beast's name to you and I"
    tax_class: Optional[str] = Field(alias="taxClass")
    "taxonomy grouping"


class Get_beasts(BaseModel):
    beasts: Optional[List[Optional[Beast]]]

    class Meta:
        domain = "default"
        document = "fragment Beast on Beast {\n  commonName\n  taxClass\n}\n\nquery get_beasts {\n  beasts {\n    ...Beast\n  }\n}"


def get_beasts() -> Optional[List[Beast]]:
    """get_beasts



    Arguments:

    Returns:
        Beast"""
    return execute(Get_beasts, {}).beasts


async def aget_beasts() -> Optional[List[Beast]]:
    """get_beasts



    Arguments:

    Returns:
        Beast"""
    return (await aexecute(Get_beasts, {})).beasts
