from typing import List

from graphql import OperationType
from turms.plugins.funcs import (
    FunctionDefinition,
    Kwarg,
    OperationsFuncPluginConfig,
    OperationsFuncPlugin,
)


class RathPluginConfig(OperationsFuncPluginConfig):
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


class RathFuncsPlugin(OperationsFuncPlugin):
    def __init__(self, config=None, **data):
        self.plugin_config = config or RathPluginConfig(**data)
