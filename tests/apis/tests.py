from enum import Enum
from pydantic import BaseModel, Field
from rath.rath import Rath
from rath.turms.funcs import aexecute, execute
from typing import Any, Literal


class Beast(BaseModel):
    """No documentation"""

    typename: Literal["Beast"] = Field(alias="__typename", default="Beast")
    common_name: str | None = Field(default=None, alias="commonName")
    "a beast's name to you and I"
    tax_class: str | None = Field(default=None, alias="taxClass")
    "taxonomy grouping"

    class Meta:
        """Meta class for Beast"""

        document = (
            "fragment Beast on Beast {\n  commonName\n  taxClass\n  __typename\n}"
        )
        name = "Beast"
        type = "Beast"


class Get_beasts(BaseModel):
    """No documentation found for this operation."""

    beasts: list[Beast | None] | None = Field(default=None)

    class Arguments(BaseModel):
        """Arguments for get_beasts"""

        pass

    class Meta:
        """Meta class for get_beasts"""

        document = "fragment Beast on Beast {\n  commonName\n  taxClass\n  __typename\n}\n\nquery get_beasts {\n  beasts {\n    ...Beast\n    __typename\n  }\n}"


def get_beasts(rath: Rath | None = None) -> list[Beast | None] | None:
    """get_beasts


    Args:
        rath (rath.rath.Rath, optional): The rath client to execute the operation on

    Returns:
        list[Beast | None] | None
    """
    variables: dict[str, Any] = {}
    return execute(Get_beasts, variables, rath=rath).beasts


async def aget_beasts(rath: Rath | None = None) -> list[Beast | None] | None:
    """get_beasts


    Args:
        rath (rath.rath.Rath, optional): The rath client to execute the operation on

    Returns:
        list[Beast | None] | None
    """
    variables: dict[str, Any] = {}
    return (await aexecute(Get_beasts, variables, rath=rath)).beasts
