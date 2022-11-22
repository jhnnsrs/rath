from typing import Generic, Type, TypeVar

from koil.qt import QtRunner
from qtpy import QtCore
from rath import Rath

T = TypeVar("T")


class QtRathQuery(QtRunner, Generic[T]):
    started: QtCore.Signal = QtCore.Signal()
    errored: QtCore.Signal = QtCore.Signal(Exception)
    cancelled: QtCore.Signal = QtCore.Signal()
    returned: QtCore.Signal = QtCore.Signal(object)

    def __init__(self, operation: Type[T], rath: Rath):
        async def coro(*args, **kwargs):
            assert rath is not None, "No rath found"

            result = await rath.aquery(operation.Meta.document, *args, **kwargs)
            return operation(**result.data)

        super().__init__(coro)
        self.operation = operation

    def run(self, **kwargs):
        arg = self.operation.Arguments(**kwargs).dict()
        return super().run(arg)
