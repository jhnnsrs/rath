from typing import List

from graphql import OperationType
from pydantic import Field
from turms.plugins.funcs import (
    FunctionDefinition,
    Kwarg,
    FuncsPlugin,
    FuncsPluginConfig,
)


class RathPluginConfig(FuncsPluginConfig):
    """RathPluginConfig is the configuration for the RathFuncsPlugin."""

    definitions: List[FunctionDefinition] = [
        FunctionDefinition(type=OperationType.MUTATION, use="rath.turms.funcs.execute"),
        FunctionDefinition(
            type=OperationType.MUTATION,
            is_async=True,
            use="rath.turms.funcs.aexecute",
        ),
        FunctionDefinition(type=OperationType.QUERY, use="rath.turms.funcs.execute"),
        FunctionDefinition(
            is_async=True,
            type=OperationType.QUERY,
            use="rath.turms.funcs.aexecute",
        ),
        FunctionDefinition(
            type=OperationType.SUBSCRIPTION, use="rath.turms.funcs.subscribe"
        ),
        FunctionDefinition(
            is_async=True,
            type=OperationType.SUBSCRIPTION,
            use="rath.turms.funcs.asubscribe",
        ),
    ]
    extra_kwargs: List[Kwarg] = [
        Kwarg(
            key="rath",
            type="rath.Rath",
            description="The rath client to use",
            default=None,
        ),
    ]


class RathFuncsPlugin(FuncsPlugin):
    """RathFuncsPlugin is a plugin that adds functions to the schema that execute operations using rath."""

    config: RathPluginConfig = Field(default_factory=RathPluginConfig)
