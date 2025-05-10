from typing_extensions import Literal
from typing import List, Optional
from rath.turms.funcs import execute, aexecute
from pydantic import Field, BaseModel


class CountriesCountries(BaseModel):
    typename: Optional[Literal["Country"]] = Field("Country", alias="__typename")
    phone: str
    capital: Optional[str] = None
    code: str


class Countries(BaseModel):
    countries: List[CountriesCountries]
    
    
    class Arguments(BaseModel):
        pass

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
