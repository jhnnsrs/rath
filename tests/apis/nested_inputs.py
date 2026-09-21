from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field

from rath.rath import Rath
from rath.turms.funcs import aexecute, execute


class UnsetType:
    """Sentinel for arguments the caller did not provide. Such fields are omitted on serialization so the GraphQL server applies its own default."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self):
        return "UNSET"

    def __bool__(self):
        return False


UNSET = UnsetType()


class BeastVector(BaseModel):
    """No documentation"""

    x: int | None = None
    y: int | None = None
    z: int | None = None


class CreateBeastCreateBeast(BaseModel):
    """No documentation"""

    typename: Literal["Beast"] = Field(alias="__typename", default="Beast")
    binomial: str | None = Field(default=None)
    "a beast's name in Latin"


class CreateBeast(BaseModel):
    """No documentation found for this operation."""

    create_beast: CreateBeastCreateBeast | None = Field(
        default=None, alias="createBeast"
    )
    "Genrates a best which is nice"

    class Arguments(BaseModel):
        """Arguments for createBeast"""

        nested: list[list[str]] | None = Field(default=None)
        non_optional_parameter: str = Field(alias="nonOptionalParameter")

    class Meta:
        """Meta class for createBeast"""

        document = "mutation createBeast($nested: [[String!]!], $nonOptionalParameter: String!) {\n  createBeast(nested: $nested, nonOptionalParameter: $nonOptionalParameter) {\n    binomial\n    __typename\n  }\n}"


class CreateTranspiledBeastCreateTranspiledBeast(BaseModel):
    """No documentation"""

    typename: Literal["Beast"] = Field(alias="__typename", default="Beast")
    binomial: str | None = Field(default=None)
    "a beast's name in Latin"


class CreateTranspiledBeast(BaseModel):
    """No documentation found for this operation."""

    create_transpiled_beast: CreateTranspiledBeastCreateTranspiledBeast | None = Field(
        default=None, alias="createTranspiledBeast"
    )

    class Arguments(BaseModel):
        """Arguments for createTranspiledBeast"""

        vectors: list[BeastVector | None] | None = Field(default=None)
        non_optional_parameter: int = Field(alias="nonOptionalParameter")

    class Meta:
        """Meta class for createTranspiledBeast"""

        document = "mutation createTranspiledBeast($vectors: [BeastVector], $nonOptionalParameter: Int!) {\n  createTranspiledBeast(\n    vectors: $vectors\n    nonOptionalParameter: $nonOptionalParameter\n  ) {\n    binomial\n    __typename\n  }\n}"


def create_beast(
    non_optional_parameter: str,
    nested: list[list[str]] | None | UnsetType = UNSET,
    rath: Rath | None = None,
) -> CreateBeastCreateBeast | None:
    """createBeast

    Genrates a best which is nice

    Args:
        non_optional_parameter (str): No description
        nested (list[list[str]] | None, optional): No description.
        rath (rath.rath.Rath, optional): The rath client to execute the operation on

    Returns:
        CreateBeastCreateBeast | None
    """
    variables: dict[str, Any] = {}
    if nested is not UNSET:
        variables["nested"] = nested
    variables["nonOptionalParameter"] = non_optional_parameter
    return execute(CreateBeast, variables, rath=rath).create_beast


async def acreate_beast(
    non_optional_parameter: str,
    nested: list[list[str]] | None | UnsetType = UNSET,
    rath: Rath | None = None,
) -> CreateBeastCreateBeast | None:
    """createBeast

    Genrates a best which is nice

    Args:
        non_optional_parameter (str): No description
        nested (list[list[str]] | None, optional): No description.
        rath (rath.rath.Rath, optional): The rath client to execute the operation on

    Returns:
        CreateBeastCreateBeast | None
    """
    variables: dict[str, Any] = {}
    if nested is not UNSET:
        variables["nested"] = nested
    variables["nonOptionalParameter"] = non_optional_parameter
    return (await aexecute(CreateBeast, variables, rath=rath)).create_beast


def create_transpiled_beast(
    non_optional_parameter: int,
    vectors: list[BeastVector | None] | None | UnsetType = UNSET,
    rath: Rath | None = None,
) -> CreateTranspiledBeastCreateTranspiledBeast | None:
    """createTranspiledBeast


    Args:
        non_optional_parameter (int): No description
        vectors (list[BeastVector | None] | None, optional): No description.
        rath (rath.rath.Rath, optional): The rath client to execute the operation on

    Returns:
        CreateTranspiledBeastCreateTranspiledBeast | None
    """
    variables: dict[str, Any] = {}
    if vectors is not UNSET:
        variables["vectors"] = vectors
    variables["nonOptionalParameter"] = non_optional_parameter
    return execute(CreateTranspiledBeast, variables, rath=rath).create_transpiled_beast


async def acreate_transpiled_beast(
    non_optional_parameter: int,
    vectors: list[BeastVector | None] | None | UnsetType = UNSET,
    rath: Rath | None = None,
) -> CreateTranspiledBeastCreateTranspiledBeast | None:
    """createTranspiledBeast


    Args:
        non_optional_parameter (int): No description
        vectors (list[BeastVector | None] | None, optional): No description.
        rath (rath.rath.Rath, optional): The rath client to execute the operation on

    Returns:
        CreateTranspiledBeastCreateTranspiledBeast | None
    """
    variables: dict[str, Any] = {}
    if vectors is not UNSET:
        variables["vectors"] = vectors
    variables["nonOptionalParameter"] = non_optional_parameter
    return (
        await aexecute(CreateTranspiledBeast, variables, rath=rath)
    ).create_transpiled_beast
