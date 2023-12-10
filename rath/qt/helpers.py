from typing import TypeVar

from koil.qt import QtRunner, QtFuture
from qtpy import QtCore
from rath import Rath
from turms.funcs import TurmsOperation
from pydantic import BaseModel

T = TypeVar("T")


class QtRathQuery(QtRunner):
    """QtRathQuery is a QtRunner that runs a query on a Rath instance.
    TODO: This should be more straightforward to use.
    """

    started: QtCore.Signal = QtCore.Signal()
    errored: QtCore.Signal = QtCore.Signal(Exception)
    cancelled: QtCore.Signal = QtCore.Signal()
    returned: QtCore.Signal = QtCore.Signal(object)

    def __init__(self, operation: TurmsOperation, rath: Rath) -> None:
        """Initializes the QtRathQuery

        Parameters
        ----------
        operation : Type[T]
            The operation to run
        rath : Rath
            The rath instance to run the operation on
        """

        async def coro(*args, **kwargs) -> BaseModel:
            """wrapper coroutine to run the operation on the rath instance"""
            assert rath is not None, "No rath found"

            result = await rath.aquery(operation.Meta.document, *args, **kwargs)
            return operation(**result.data)

        super().__init__(coro)
        self.operation = operation

    def run(self, **kwargs) -> QtFuture:
        """Runs the operation on the rath instance

        This is an async method that returns a QtFuture that can be used to cancel the operation.
        The result of the operation is emitted by the returned signal, and the error is emitted by the errored signal.

        Parameters
        ----------
        **kwargs
            The arguments to pass to the operation

        Returns
        -------
        QtFuture:
            The future of the operation, can be used to cancel the operation

        """

        arg = self.operation.Arguments(**kwargs).dict()  # type: ignore
        # TODO: This should be more straightforward to use, and typed
        return super().run(arg)
