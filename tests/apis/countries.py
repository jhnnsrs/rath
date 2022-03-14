from enum import Enum
from typing import Literal, Optional, List
from rath.turms.funcs import aexecute, execute
from pydantic import Field, BaseModel


class CountriesCountries(BaseModel):
    typename: Optional[Literal["Country"]] = Field(alias="__typename")
    phone: str
    capital: Optional[str]


class Countries(BaseModel):
    countries: List[CountriesCountries]

    class Meta:
        domain = "countries"
        document = "query Countries {\n  countries {\n    phone\n    capital\n  }\n}"


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
