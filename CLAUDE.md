# Rath – Claude Code Guide

## Project overview

Rath is an async, transport-agnostic GraphQL client for Python built on [Pydantic v2](https://docs.pydantic.dev/) and [Koil](https://github.com/jhnnsrs/koil).  
The core abstraction is a **link chain**: composable middleware objects that transform or forward `Operation` objects until a terminating link dispatches them over the network.

## Layout

```
rath/                  # library source
  rath.py              # Rath client (entry point)
  operation.py         # Operation, Context, Extensions, GraphQLResult, opify()
  errors.py            # Top-level exceptions (RathException, …)
  links/
    base.py            # Link, TerminatingLink, ContinuationLink
    compose.py         # compose(), ComposedLink, TypedComposedLink
    auth.py            # AuthTokenLink, ComposedAuthLink
    apq.py             # ApqLink (Automatic Persisted Queries)
    httpx.py           # HttpxLink (HTTP transport)
    aiohttp.py         # AIOHttpLink (HTTP transport)
    graphql_ws.py      # GraphQLWSLink (WebSocket, graphql-ws protocol)
    subscription_transport_ws.py  # legacy subscriptions-transport-ws
    split.py           # SplitLink (route by operation type)
    validate.py        # ValidatingLink (schema validation)
    timeout.py         # TimeoutLink
    testing/           # AsyncMockLink, AsyncStatefulMockLink, AssertLink, utils
    …
  turms/               # Integration helpers for turms-generated code
tests/                 # pytest suite (mirrors rath/ structure)
```

## Code style

- **Python ≥ 3.11**; type hints on all public APIs.
- **Pydantic v2** models throughout — prefer `Field(default_factory=…)` for mutable defaults.
- Links inherit from `Link`, `ContinuationLink`, or `AsyncTerminatingLink`; implement `aexecute(self, operation) -> AsyncIterator[GraphQLResult]`.
- Keep methods short. No inline comments unless the _why_ is non-obvious.
- Formatting: [Ruff](https://docs.astral.sh/ruff/) (`ruff check .`), line length 300.

## Tests

- Framework: **pytest** with `asyncio_mode = "auto"` — async test functions work without extra decorators.
- Run offline tests: `uv run pytest -k "not integration and not public and not qt"`
- Run all tests: `uv run pytest`
- Coverage: `uv run pytest --cov --cov-branch --cov-report=xml`
- Tests that need a live server are marked `@pytest.mark.integration`.
- Tests that hit public APIs are marked `@pytest.mark.public`.
- Use `AsyncMockLink` / `AsyncStatefulMockLink` from `rath.links.testing` to mock the terminating link in unit tests.
- Use `AssertLink` + `compose()` to verify that upstream links transform operations correctly.
- CI runs the full test matrix (Python 3.11 + 3.12, Ubuntu + Windows) on every PR to `main`.

## Commit conventions

This repo uses **[Conventional Commits](https://www.conventionalcommits.org/)**.  
Every commit message must start with a type prefix:

| Prefix | When to use |
|--------|-------------|
| `feat:` | New feature or capability |
| `fix:` | Bug fix |
| `chore:` | Maintenance, dependency bumps, config |
| `refactor:` | Code change with no behaviour change |
| `test:` | Adding or updating tests only |
| `docs:` | Documentation only |
| `ci:` | CI / workflow changes |

Examples:
```
feat: add RetryLink with configurable back-off
fix: restore omit_document flag after APQ fallback
chore: bump koil to >=3
test: add unit tests for AuthTokenLink refresh logic
```

Semantic Release reads these prefixes to determine the next version number and generate `CHANGELOG.md` — **do not skip the prefix**.

## Dependency management

Dependencies are managed with **[uv](https://docs.astral.sh/uv/)**.  
- Add a runtime dep: `uv add <package>`  
- Add a dev dep: `uv add --dev <package>`  
- Sync: `uv sync --all-extras --dev`

The `koil` requirement is `>=3`; do not downgrade it.
