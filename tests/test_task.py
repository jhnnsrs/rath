"""The current task: ambient by default, explicit when handed one."""

import asyncio
import contextvars
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from rath.task import TASK_HEADER, current_task, task_scope, token_of


class FakeTask:
    """As much of a task as a client reads."""

    def __init__(self, token: str | None) -> None:
        self.token = token

    def __bool__(self) -> bool:
        # A task that is falsy: `task or current_task.get()` would drop it.
        return False


def test_nothing_is_current_by_default() -> None:
    assert current_task.get() is None
    assert token_of(None) is None


def test_the_header_name_is_the_one_the_server_reads() -> None:
    assert TASK_HEADER == "Rekuest-Task"


def test_a_scope_sets_and_restores() -> None:
    task = FakeTask("t1")
    with task_scope(task):
        assert current_task.get() is task
        assert token_of(None) == "t1"
    assert current_task.get() is None


def test_a_scope_restores_even_when_the_body_raises() -> None:
    with pytest.raises(ValueError):
        with task_scope(FakeTask("t1")):
            raise ValueError("boom")
    assert current_task.get() is None


def test_scopes_nest() -> None:
    outer, inner = FakeTask("outer"), FakeTask("inner")
    with task_scope(outer):
        with task_scope(inner):
            assert token_of(None) == "inner"
        assert token_of(None) == "outer"
    assert current_task.get() is None


def test_a_scope_of_none_is_explicitly_unattributed() -> None:
    with task_scope(FakeTask("t1")):
        with task_scope(None):
            assert token_of(None) is None
        assert token_of(None) == "t1"


def test_an_explicit_task_beats_the_ambient_one() -> None:
    with task_scope(FakeTask("ambient")):
        assert token_of(FakeTask("explicit")) == "explicit"


def test_a_falsy_task_still_counts() -> None:
    """`if task is None`, not `task or ...`: a task must not lose to __bool__."""
    assert token_of(FakeTask("t1")) == "t1"


def test_a_task_without_a_token_attributes_nothing() -> None:
    with task_scope(FakeTask(None)):
        assert token_of(None) is None


@pytest.mark.asyncio
async def test_concurrent_asyncio_tasks_do_not_see_each_other() -> None:
    """Each asyncio Task runs in its own context copy."""

    async def run(name: str) -> str | None:
        with task_scope(FakeTask(name)):
            await asyncio.sleep(0)
            return token_of(None)

    assert await asyncio.gather(run("a"), run("b")) == ["a", "b"]
    assert current_task.get() is None


def test_a_plain_thread_inherits_nothing_unless_you_carry_the_context() -> None:
    """The documented limitation, pinned so it is a decision and not a surprise."""
    seen: dict[str, str | None] = {}

    with task_scope(FakeTask("t1")):
        bare = threading.Thread(target=lambda: seen.__setitem__("bare", token_of(None)))
        bare.start()
        bare.join()

        ctx = contextvars.copy_context()
        carried = threading.Thread(
            target=lambda: ctx.run(lambda: seen.__setitem__("carried", token_of(None)))
        )
        carried.start()
        carried.join()

        with ThreadPoolExecutor(1) as pool:
            seen["pool"] = pool.submit(token_of, None).result()

    assert seen["bare"] is None, "a raw thread start does not carry contextvars"
    assert seen["pool"] is None, "nor does an executor"
    assert seen["carried"] == "t1", "copy_context().run does"
