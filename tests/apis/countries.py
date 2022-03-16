from typing_extensions import Literal
from typing import List, Optional
from rath.turms.funcs import execute, aexecute
from enum import Enum
from pydantic import BaseModel, Field


class CountriesCountries(BaseModel):
    typename: Optional[Literal["Country"]] = Field(alias="__typename")
    phone: str
    capital: Optional[str]
    code: str


class Countries(BaseModel):
    countries: List[CountriesCountries]

    class Meta:
        domain = "countries"
        document = (
            "query Countries {\n  countries {\n    phone\n    capital\n    code\n  }\n}"
        )


def countries() -> List[CountriesCountries]:
    """Countries



    Arguments:

    Returns:
        CountriesCountries"""
    return execute(Countries, {}).countries


async def acountries() -> List[CountriesCountries]:
    """Countries



    Arguments:

    Returns:
        CountriesCountries"""
    return (await aexecute(Countries, {})).countries
