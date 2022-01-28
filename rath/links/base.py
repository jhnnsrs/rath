from rath.operation import GraphQLResult, Operation


class Link:
    async def aconnect(self) -> None:
        pass

    async def aquery(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError("Please overwrite this method")

    async def asubscribe(self, operation: Operation) -> GraphQLResult:
        raise NotImplementedError("Please overwrite this method")


class TerminatingLink:
    def __call__(self, rath):
        self.rath = rath
        return self


class ContinuationLink:
    def __call__(self, rath, next: Link):
        self.rath = rath
        self.next = next
        return self
