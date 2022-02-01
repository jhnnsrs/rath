from pydantic.main import BaseModel, ModelMetaclass
from turms.types.operation import OperationMeta
from rath.rath import Rath, get_current_rath


class GraphQLOperation(BaseModel, metaclass=OperationMeta):
    @classmethod
    def execute(cls, variables, rath: Rath = None):
        rath = rath or get_current_rath()
        return cls(**rath.execute(cls.get_meta().document, variables).data)

    @classmethod
    async def aexecute(cls, variables, rath: Rath = None):
        rath = rath or get_current_rath()
        return cls(**(await rath.aexecute(cls.get_meta().document, variables)).data)

    class Meta:
        abstract = True


class GraphQLQuery(GraphQLOperation):
    class Meta:
        abstract = True


class GraphQLMutation(GraphQLOperation):
    class Meta:
        abstract = True


class GraphQLSubscription(GraphQLOperation):
    class Meta:
        abstract = True
