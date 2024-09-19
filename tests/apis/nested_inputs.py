from typing import List, Optional

from pydantic import BaseModel, Field
from typing_extensions import Literal

from rath.turms.funcs import aexecute, execute


class BeastVector(BaseModel):
    x: Optional[int] = None
    y: Optional[int] = None
    z: Optional[int] = None


class CreateBeastCreatebeast(BaseModel):
    typename: Optional[Literal["Beast"]] = Field("Beast", alias="__typename")
    binomial: Optional[str] = None
    "a beast's name in Latin"


class CreateBeast(BaseModel):
    create_beast: Optional[CreateBeastCreatebeast] = Field(alias="createBeast")
    "Genrates a best which is nice"

    class Meta:
        domain = "nested_inputs"
        document = "mutation createBeast($nested: [[String!]!], $nonOptionalParameter: String!) {\n  createBeast(nested: $nested, nonOptionalParameter: $nonOptionalParameter) {\n    binomial\n  }\n}"


class CreateTranspiledBeastCreatetranspiledbeast(BaseModel):
    typename: Optional[Literal["Beast"]] = Field("Beast", alias="__typename")
    binomial: Optional[str] = None
    "a beast's name in Latin"


class CreateTranspiledBeast(BaseModel):
    create_transpiled_beast: Optional[
        CreateTranspiledBeastCreatetranspiledbeast
    ] = Field(alias="createTranspiledBeast")

    class Meta:
        domain = "nested_inputs"
        document = "mutation createTranspiledBeast($vectors: [BeastVector], $nonOptionalParameter: Int!) {\n  createTranspiledBeast(\n    vectors: $vectors\n    nonOptionalParameter: $nonOptionalParameter\n  ) {\n    binomial\n  }\n}"


def create_beast(
    non_optional_parameter: Optional[str], nested: Optional[List[List[str]]] = None
) -> Optional[CreateBeastCreatebeast]:
    """createBeast

    Genrates a best which is nice

    Arguments:
        non_optional_parameter (str): nonOptionalParameter
        nested (Optional[List[List[str]]], optional): nested.

    Returns:
        CreateBeastCreatebeast"""
    return execute(
        CreateBeast, {"nested": nested, "nonOptionalParameter": non_optional_parameter}
    ).create_beast


async def acreate_beast(
    non_optional_parameter: Optional[str], nested: Optional[List[List[str]]] = None
) -> Optional[CreateBeastCreatebeast]:
    """createBeast

    Genrates a best which is nice

    Arguments:
        non_optional_parameter (str): nonOptionalParameter
        nested (Optional[List[List[str]]], optional): nested.

    Returns:
        CreateBeastCreatebeast"""
    return (
        await aexecute(
            CreateBeast,
            {"nested": nested, "nonOptionalParameter": non_optional_parameter},
        )
    ).create_beast


def create_transpiled_beast(
    non_optional_parameter: Optional[int],
    vectors: Optional[List[Optional[BeastVector]]] = None,
) -> Optional[CreateTranspiledBeastCreatetranspiledbeast]:
    """createTranspiledBeast



    Arguments:
        non_optional_parameter (int): nonOptionalParameter
        vectors (Optional[List[Optional[BeastVector]]], optional): vectors.

    Returns:
        CreateTranspiledBeastCreatetranspiledbeast"""
    return execute(
        CreateTranspiledBeast,
        {"vectors": vectors, "nonOptionalParameter": non_optional_parameter},
    ).create_transpiled_beast


async def acreate_transpiled_beast(
    non_optional_parameter: Optional[int],
    vectors: Optional[List[Optional[BeastVector]]] = None,
) -> Optional[CreateTranspiledBeastCreatetranspiledbeast]:
    """createTranspiledBeast



    Arguments:
        non_optional_parameter (int): nonOptionalParameter
        vectors (Optional[List[Optional[BeastVector]]], optional): vectors.

    Returns:
        CreateTranspiledBeastCreatetranspiledbeast"""
    return (
        await aexecute(
            CreateTranspiledBeast,
            {"vectors": vectors, "nonOptionalParameter": non_optional_parameter},
        )
    ).create_transpiled_beast
