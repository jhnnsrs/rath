"""The task a request is made for: who to attribute it to.

A client that serves an agent makes its requests on behalf of whatever task is
running, and the server wants that written on the request. The task is not an
argument of the query, so it travels beside it: ambient in a contextvar by
default, explicit as a ``task=`` keyword when the caller has one in hand.

This is the request-side sibling of :mod:`rath.origin`, which answers "which
client did this object come *from*". It lives here rather than in the package
that defines the concrete task because every client depends on rath, while some
of them deliberately do not depend on that package.

.. warning::
   A contextvar does not cross every boundary. It is copied into a thread by
   :func:`koil.bridge.run_threaded` and into an asyncio Task at creation, but a
   **plain** ``threading.Thread`` or ``ThreadPoolExecutor.submit`` that your code
   starts itself inherits nothing, and a task you spawn with
   ``asyncio.create_task`` keeps the value it was created with even after the
   work it belongs to has finished. In both cases pass ``task=`` explicitly, or
   carry the context yourself::

       ctx = contextvars.copy_context()
       threading.Thread(target=lambda: ctx.run(work)).start()
"""

import contextvars
from contextlib import contextmanager
from typing import Iterator, Optional, Protocol

TASK_HEADER = "Rekuest-Task"
"""The header a request carries its task's provenance token in."""


class TaskLike(Protocol):
    """What a client needs of a task: the token its requests are attributed with.

    Deliberately one member. A concrete task carries far more -- who is running
    it, what it is a child of -- but a client reads none of that, and a wider
    protocol would tempt one to. Not ``runtime_checkable``: an ``isinstance``
    against a one-property Protocol only checks that the attribute exists, which
    is a weaker claim than it looks.
    """

    @property
    def token(self) -> Optional[str]:
        """The provenance token, or ``None`` when the task opted out of one."""
        ...


current_task: contextvars.ContextVar[Optional[TaskLike]] = contextvars.ContextVar(
    "rath_current_task", default=None
)
"""The task requests made right now belong to, if any."""


@contextmanager
def task_scope(task: Optional[TaskLike]) -> Iterator[Optional[TaskLike]]:
    """Attribute everything done inside the block to ``task``.

    Restores the previous value on the way out, including when the body raises,
    so a task never outlives the work it belongs to. Nests: an inner scope shadows
    an outer one and the outer one is intact afterwards.

    Pass ``None`` to make a block explicitly unattributed.
    """
    token = current_task.set(task)
    try:
        yield task
    finally:
        current_task.reset(token)


def token_of(task: Optional[TaskLike]) -> Optional[str]:
    """The token to attribute a request to: ``task``'s, else the ambient one's.

    ``task is None`` rather than a truth test on purpose -- a task object must not
    be able to lose to its own ``__bool__``.
    """
    if task is None:
        task = current_task.get()
    return getattr(task, "token", None)


__all__ = ["TASK_HEADER", "TaskLike", "current_task", "task_scope", "token_of"]
