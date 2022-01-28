from rath.operation import GraphQLResult, Operation


class Transport:
    def __call__(self, rath):
        self.rath = rath
        return self

    async def aconnect(self) -> None:
        pass

    async def aquery(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError("Please overwrite this method")

    async def asubscribe(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError("Please overwrite this method")
