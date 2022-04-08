from rath.rath import Rath, current_rath


def execute(operation, variables, rath: Rath = None):
    rath = rath or current_rath.get()
    return operation(**rath.query(operation.Meta.document, variables).data)


async def aexecute(operation, variables, rath: Rath = None):
    rath = rath or current_rath.get()
    x = await rath.aquery(operation.Meta.document, variables)
    return operation(**x.data)


def subscribe(operation, variables, rath: Rath = None):
    rath = rath or current_rath.get()

    for event in rath.subscribe(operation.Meta.document, variables):
        yield operation(**event.data)


async def asubscribe(operation, variables, rath: Rath = None):
    rath = rath or current_rath.get()
    async for event in rath.asubscribe(operation.Meta.document, variables):
        yield operation(**event.data)
