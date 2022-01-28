from rath.operation import Operation


class Parser:
    pass

    def __call__(self, rath):
        self.rath = rath
        return self

    async def aparse(self, operation: Operation) -> Operation:
        return self.parse(operation)

    def parse(self, operation: Operation) -> Operation:
        raise NotImplementedError("Please overwrite this method")

    async def aconnect(self):
        pass
