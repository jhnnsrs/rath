from pydantic.main import BaseModel, ModelMetaclass
from turms.types.operation import OperationMeta
from rath.rath import Rath, get_current_rath


class GraphQLOperation(BaseModel, metaclass=OperationMeta):
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
