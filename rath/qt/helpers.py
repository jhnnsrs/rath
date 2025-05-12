from typing import Any, Generic, TypeVar

from koil.qt import QtRunner
from qtpy import QtCore
from koil.task import KoilFuture
from rath import Rath
from turms.funcs import TurmsOperation
from pydantic import BaseModel

T = TypeVar("T", bound=TurmsOperation[Any, Any])


class QtRathQuery(QtRunner, Generic[T]):
    """QtRathQuery is a QtRunner that runs a query on a Rath instance.
    TODO: This should be more straightforward to use.
    """

    started: QtCore.Signal = QtCore.Signal()  # type: ignore
    errored: QtCore.Signal = QtCore.Signal(Exception)  # type: ignore
    cancelled: QtCore.Signal = QtCore.Signal()  # type: ignore
    returned: QtCore.Signal = QtCore.Signal(object)  # type: ignore

    def __init__(self, operation: T, rath: Rath) -> None:
        """Initializes the QtRathQuery

        Parameters
        ----------
        operation : Type[T]
            The operation to run
        rath : Rath
            The rath instance to run the operation on
        """

        async def coro(*args, **kwargs) -> BaseModel:  # type: ignore
            """wrapper coroutine to run the operation on the rath instance"""
            assert rath is not None, "No rath found"

            result = await rath.aquery(operation.Meta.document, *args, **kwargs)  # type: ignore
            return operation(**result.data)  # type: ignore

        super().__init__(coro)  # type: ignore
        self.operation = operation

    def run(self, **kwargs) -> KoilFuture[T]:
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
