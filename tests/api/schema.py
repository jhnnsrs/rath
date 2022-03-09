from typing import Literal, Optional, List
from enum import Enum
from rath.turms.funcs import aexecute, execute
from pydantic import Field, BaseModel


class Beast(BaseModel):
    typename: Optional[Literal["Beast"]] = Field(alias="__typename")
    commonName: Optional[str]
    "a beast's name to you and I"
    taxClass: Optional[str]
    "taxonomy grouping"


class Get_beasts(BaseModel):
    beasts: Optional[List[Optional[Beast]]]

    class Meta:
        domain = "default"
        document = "fragment Beast on Beast {\n  commonName\n  taxClass\n}\n\nquery get_beasts {\n  beasts {\n    ...Beast\n  }\n}"


def get_beasts() -> List[Beast]:
    """get_beasts



    Arguments:

    Returns:
        Beast: The returned Mutation"""
    return execute(Get_beasts, {}).beasts


async def aget_beasts() -> List[Beast]:
    """get_beasts



    Arguments:

    Returns:
        Beast: The returned Mutation"""
    return (await aexecute(Get_beasts, {})).beasts
