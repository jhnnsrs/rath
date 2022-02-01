from turms.types.object import GraphQLObject
from turms.types.object import GraphQLObject
from pydantic.fields import Field
from typing import Optional, List, Dict, Union, Literal
from enum import Enum
from turms.types.object import GraphQLObject
from rath.turms.operation import GraphQLQuery
from rath.turms.operation import GraphQLMutation
from rath.turms.operation import GraphQLSubscription


class users_select_column(str, Enum):
    '''select columns of table "users"'''

    id = "id"
    "column name"
    name = "name"
    "column name"
    rocket = "rocket"
    "column name"
    timestamp = "timestamp"
    "column name"
    twitter = "twitter"
    "column name"


class order_by(str, Enum):
    """column ordering options"""

    asc = "asc"
    "in the ascending order, nulls last"
    asc_nulls_first = "asc_nulls_first"
    "in the ascending order, nulls first"
    asc_nulls_last = "asc_nulls_last"
    "in the ascending order, nulls last"
    desc = "desc"
    "in the descending order, nulls first"
    desc_nulls_first = "desc_nulls_first"
    "in the descending order, nulls first"
    desc_nulls_last = "desc_nulls_last"
    "in the descending order, nulls last"


class users_constraint(str, Enum):
    '''unique or primary key constraints on table "users"'''

    users_pkey = "users_pkey"
    "unique or primary key constraint"


class users_update_column(str, Enum):
    '''update columns of table "users"'''

    id = "id"
    "column name"
    name = "name"
    "column name"
    rocket = "rocket"
    "column name"
    timestamp = "timestamp"
    "column name"
    twitter = "twitter"
    "column name"


class conflict_action(str, Enum):
    """conflict action"""

    ignore = "ignore"
    "ignore the insert on this row"
    update = "update"
    "update the row with the given values"


class UserFragment(GraphQLObject):
    typename: Optional[Literal["users"]] = Field(alias="__typename")
    id: str


class UserQuery(GraphQLQuery):
    users: List[UserFragment]

    class Meta:
        domain = "default"
        document = "fragment User on users {\n  id\n}\n\nquery User {\n  users {\n    ...User\n  }\n}"


class Get_capsulesQueryCapsulesMissions(GraphQLObject):
    typename: Optional[Literal["CapsuleMission"]] = Field(alias="__typename")
    flight: Optional[int]
    name: Optional[str]


class Get_capsulesQueryCapsules(GraphQLObject):
    typename: Optional[Literal["Capsule"]] = Field(alias="__typename")
    id: Optional[str]
    missions: Optional[List[Optional[Get_capsulesQueryCapsulesMissions]]]


class Get_capsulesQuery(GraphQLQuery):
    capsules: Optional[List[Optional[Get_capsulesQueryCapsules]]]

    class Meta:
        domain = "default"
        document = "query get_capsules {\n  capsules {\n    id\n    missions {\n      flight\n      name\n    }\n  }\n}"


class Inset_userMutationInsert_usersReturning(GraphQLObject):
    '''columns and relationships of "users"'''

    typename: Optional[Literal["users"]] = Field(alias="__typename")
    id: str


class Inset_userMutationInsert_users(GraphQLObject):
    '''response of any mutation on the table "users"'''

    typename: Optional[Literal["users_mutation_response"]] = Field(alias="__typename")
    returning: List[Inset_userMutationInsert_usersReturning]
    "data of the affected rows by the mutation"


class Inset_userMutation(GraphQLMutation):
    insert_users: Optional[Inset_userMutationInsert_users]

    class Meta:
        domain = "default"
        document = "mutation inset_user($id: uuid) {\n  insert_users(objects: {id: $id}) {\n    returning {\n      id\n    }\n  }\n}"


async def aUser() -> UserFragment:
    """User

    fetch data from the table: "users"

    Arguments:

    Returns:
        UserFragment: The returned Mutation"""
    return (await UserQuery.aexecute({})).users


def User() -> UserFragment:
    """User

    fetch data from the table: "users"

    Arguments:

    Returns:
        UserFragment: The returned Mutation"""
    return UserQuery.execute({}).users


async def aget_capsules() -> List[Get_capsulesQueryCapsules]:
    """get_capsules



    Arguments:

    Returns:
        Get_capsulesQueryCapsules: The returned Mutation"""
    return (await Get_capsulesQuery.aexecute({})).capsules


def get_capsules() -> List[Get_capsulesQueryCapsules]:
    """get_capsules



    Arguments:

    Returns:
        Get_capsulesQueryCapsules: The returned Mutation"""
    return Get_capsulesQuery.execute({}).capsules


async def ainset_user(id: str = None) -> Inset_userMutationInsert_users:
    """inset_user

    insert data into the table: "users"

    Arguments:
        id (uuid, Optional): uuid

    Returns:
        Inset_userMutationInsert_users: The returned Mutation"""
    return (await Inset_userMutation.aexecute({"id": id})).insert_users


def inset_user(id: str = None) -> Inset_userMutationInsert_users:
    """inset_user

    insert data into the table: "users"

    Arguments:
        id (uuid, Optional): uuid

    Returns:
        Inset_userMutationInsert_users: The returned Mutation"""
    return Inset_userMutation.execute({"id": id}).insert_users
