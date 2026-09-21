# CHANGELOG


## v4.0.1 (2026-09-21)

### Bug Fixes

- **ci**: Publish only when semantic-release actually cut a release
  ([`1177d9b`](https://github.com/jhnnsrs/rath/commit/1177d9bdc6c9a17990768b92cb36078ffc1e7b70))

`uv publish` ran unconditionally. `semantic-release version` builds only when it cuts a release, so
  any push carrying nothing releasable -- a `build:`, `chore:` or `docs:` change -- left `dist/`
  empty and failed the job on the publish step. Both publish steps are now guarded on
  `hashFiles('dist/**')`, which is the same shape as the guard the tag-only repos get from the
  semantic-release action's `released` output.

Also moves the dokker floor to 2.8 with the rest of the wave.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

Claude-Session: https://claude.ai/code/session_01QEr4a9XNWRms96tmxUPXmz


## v4.0.0 (2026-09-21)

### Build System

- **deps**: Ask for qtpy directly instead of inheriting it
  ([`5aaefdc`](https://github.com/jhnnsrs/rath/commit/5aaefdc768299b414168da4cf07ecc7d7f23008b))

`tests/test_qt.py` imports `koil.qt`, which imports `qtpy` at module scope. rath never declared it
  -- it arrived transitively through a `fakts==1.0.0` dev-pin that nothing imported, and removing
  that dead pin in the sweep took qtpy with it, so collection failed in CI with
  `ModuleNotFoundError: No module named 'qtpy'`.

It did not fail locally, because the local venv still had qtpy installed from before the pin was
  removed. Re-syncing from the lockfile reproduces CI exactly and is what verified this.

`koil[qtpy]>=3.3.3` says what the tests actually need. The turms dev-pin also moves to 2.1.0, which
  is now released.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

### Chores

- **codegen**: Point graphql.config.yaml at a plugin that exists
  ([`a250bec`](https://github.com/jhnnsrs/rath/commit/a250bec112e76c75915e2648d7e5f6ff2eef1e40))

`graphql.config.yaml` named `rath.turms.plugins.funcs.RathFuncsPlugin` in all three projects. That
  plugin was deleted in 87eae6e ("Remove Transpile link and add typing") and the `plugins/` package
  under `rath/turms/` went with it -- so the config has been unloadable ever since, which is why
  nobody noticed it also still declared `turms.parsers.polyfill.PolyfillParser`, removed in turms
  2.0.

It is turms' own `FuncsPlugin` now, with `definitions` pointing at `rath.turms.funcs` (which is very
  much alive -- it is what the generated functions call). `global_kwargs` rather than `global_args`:
  turms puts args first, and `execute` takes its rath last, so args would have passed the client as
  the operation.

`tests/apis/tests.py` and `nested_inputs.py` are regenerated from it. The `countries` project is
  left as generated -- its schema is a third-party endpoint, so regenerating it needs the network.

`website/docs/turms.md` documented the dead plugin as live, and showed `get_beasts()` reaching for
  an implicit "currently active client" that no longer exists. Rewritten against what the config
  actually produces.

Dev-deps: `fakts==1.0.0` and `herre==1.0.0`, which nothing imports (the `herre` in
  `tests/integration/mini.yaml` is a compose service name), replaced by `turms`, so the config can
  be run from rath's own venv.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

### Features

- Origin carries the client, not a context variable
  ([`0224bfa`](https://github.com/jhnnsrs/rath/commit/0224bfa703f2482928246993e0c8bd070bbe0912))

Baseline commit of the in-flight `app-context` work.

`Origin.client` replaces the ambient `current_rath` contextvar, which is deleted along with
  `rath/resolve.py`. `FederationFetchable.expand(id, client)` and `federated(fragment, origin=)`
  hand expanders their client explicitly, and `rath.turms.funcs` now requires one.

Tests: 162 pass (QT_QPA_PLATFORM=offscreen).

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

- **task**: The task a request is attributed to, ambient or explicit
  ([`5725492`](https://github.com/jhnnsrs/rath/commit/57254924f91d41cf4673414f47f54bdcae019b22))

`rath.task` holds `current_task`, a `task_scope()` that sets and unwinds it, a one-member `TaskLike`
  protocol, `token_of()` and the `Rekuest-Task` header name. Additive: nothing reads it yet.

It lives in rath rather than in the package that defines the concrete task because every client
  depends on rath, while alpaka and fluss deliberately do not depend on that package and still stamp
  the header. It is the request-side sibling of `rath.origin`, which answers which client an object
  came *from*.

`token_of` tests `task is None` rather than truthiness, so a task cannot lose to its own `__bool__`
  -- pinned by a deliberately falsy fake. `TaskLike` is not `runtime_checkable`: `isinstance`
  against a one-property Protocol only checks that the attribute exists, which is a weaker claim
  than it looks.

The limits are pinned as tests rather than left to be discovered: a raw `threading.Thread` and a
  `ThreadPoolExecutor` inherit nothing, while `copy_context().run(...)` does, and the module
  docstring says so.

rath: 173 pass.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>


## v3.13.0 (2026-09-01)

### Features

- Better auth errors
  ([`d034203`](https://github.com/jhnnsrs/rath/commit/d0342030902266c0070fd1269934456e60e0696d))


## v3.12.0 (2026-06-21)

### Features

- Update to koil 3.3 that fixes major task leakage and better error reporting
  ([`3cbcbb1`](https://github.com/jhnnsrs/rath/commit/3cbcbb1bd6071085862355ff767c864c28dadcfd))


## v3.11.1 (2026-06-09)


## v3.11.0 (2026-06-09)

### Bug Fixes

- Update koil
  ([`0b89c72`](https://github.com/jhnnsrs/rath/commit/0b89c724f82af1057f7e48888296aef325e76981))

### Features

- Update readme
  ([`83424e4`](https://github.com/jhnnsrs/rath/commit/83424e4c30b1a6558cd7f0868df322e9a7a0e9c9))


## v3.10.0 (2026-06-08)

### Features

- Add CLAUDE.md with project guide and commit conventions
  ([`d09babd`](https://github.com/jhnnsrs/rath/commit/d09babd0f994014d29ba4b97ffa63da51b867a1e))

Documents repo layout, code style, test patterns, and enforces Conventional Commits so Semantic
  Release can version correctly.

https://claude.ai/code/session_014EK7JtPbiN9hUt2LvrZQUX


## v3.9.1 (2026-04-14)

### Bug Fixes

- 3.11 compatibility without type ar
  ([`21e6ce3`](https://github.com/jhnnsrs/rath/commit/21e6ce358a3c6b842eda1a93577ae34c38080584))


## v3.9.0 (2026-04-09)

### Features

- Better exception description
  ([`f8d1e82`](https://github.com/jhnnsrs/rath/commit/f8d1e8271ba61f593555f8e4de98606e5ffb394f))


## v3.8.0 (2025-11-29)

### Chores

- Preliminary apq query
  ([`458db29`](https://github.com/jhnnsrs/rath/commit/458db298124c882f99dee45bd3b4719447841cd9))

### Features

- Add typemap apply recursive helpers
  ([`9d164bd`](https://github.com/jhnnsrs/rath/commit/9d164bd94bc8aa7a1893a901ca388f8a47c1a437))


## v3.7.0 (2025-08-22)

### Features

- Add fragment options
  ([`cbdc576`](https://github.com/jhnnsrs/rath/commit/cbdc5769414c9e6a12a5174dff757b73030ba0dd))


## v3.6.0 (2025-07-11)

### Features

- Made exception have operation inside
  ([`4458041`](https://github.com/jhnnsrs/rath/commit/4458041d64cf7574cacd71967cab21564c1d84cb))


## v3.5.1 (2025-07-08)

### Bug Fixes

- Update idcoerciable to accept int
  ([`3915e4e`](https://github.com/jhnnsrs/rath/commit/3915e4ed404ef6d61e27d04be11564721d56c91d))


## v3.5.0 (2025-05-21)

### Features

- Adding in the IDCoercible type for turms generated functions
  ([`cd1622c`](https://github.com/jhnnsrs/rath/commit/cd1622c5c2d5c297bf1de41f3ef8cd847cec7bb2))


## v3.4.0 (2025-05-13)


## v3.3.0 (2025-05-12)

### Features

- Upgrade to koil > 2, for typed support
  ([`6098587`](https://github.com/jhnnsrs/rath/commit/6098587a37e12fc351ce028de52624d92aa32771))


## v3.2.0 (2025-05-11)


## v3.1.0 (2025-05-11)


## v3.0.0 (2025-05-10)

### Bug Fixes

- Add DirectSucceedingLink for enhanced testing capabilities
  ([`b8b83d9`](https://github.com/jhnnsrs/rath/commit/b8b83d9f7e389ff08c7195291527b902f09db287))

### Features

- Add NeverSucceedingLink and TimeoutLink for enhanced testing capabilities
  ([`e683ad7`](https://github.com/jhnnsrs/rath/commit/e683ad72dbf625db06c5a7b11b8d66e0578aa650))

- Add py.typed file and update pyproject.toml for type hinting support
  ([`260da3c`](https://github.com/jhnnsrs/rath/commit/260da3ca293814a013e410799168b290f7541717))

- Refactor and enhance type hints across multiple modules
  ([`a75ddcc`](https://github.com/jhnnsrs/rath/commit/a75ddccf847b6458c59bfa79fe2a1699e175e2e4))

- Improved type hints in `graphql_ws.py`, `httpx.py`, `sign_local_link.py`, `split.py`,
  `subscription_transport_ws.py`, `mock.py`, `never_succeeding_link.py`, `statefulmock.py`,
  `utils.py`, `validate.py`, `helpers.py`, and `rath.py` for better clarity and type safety. -
  Updated async context manager methods to return `Self` for improved type inference. - Enhanced
  error handling and logging messages for better debugging. - Cleaned up code formatting for
  consistency and readability.

- Refactor Turms operation protocols and update beast models for clarity
  ([`68b794b`](https://github.com/jhnnsrs/rath/commit/68b794ba65ba036dae25457c8333f16fe9fbd4a4))

- Remove Transpile link and add typing
  ([`87eae6e`](https://github.com/jhnnsrs/rath/commit/87eae6e0e296d216d78f63dc012c40c74b440e95))

- Yield result in TimeoutLink's aexecute method for proper async handling
  ([`2282d8e`](https://github.com/jhnnsrs/rath/commit/2282d8eba705f79c3886502222c83ddf4d9d5b6d))


## v2.0.0 (2025-05-09)

### Features

- Remove outdated authentication example from README
  ([`06ca84b`](https://github.com/jhnnsrs/rath/commit/06ca84b608dd5575a4f5c8aa812a00f738c3be74))


## v1.0.0 (2025-05-09)

### Features

- Update CI workflow to remove macOS and bump version to 0.5.1
  ([`ff91de2`](https://github.com/jhnnsrs/rath/commit/ff91de2b94d10a7b45dc6baa25141b0515324aa6))


## v0.5.1 (2025-05-09)


## v0.5.0 (2025-05-09)

### Bug Fixes

- Add qt action
  ([`7a4a7b5`](https://github.com/jhnnsrs/rath/commit/7a4a7b5a66eae9b205b1ab6b09122ae58193d2a8))

- Adjust formatting in coverage.yaml and ensure qt setup step is included
  ([`a68f10b`](https://github.com/jhnnsrs/rath/commit/a68f10bbedd072b795e6f51a9b7540c723c932b1))

- Correct typo in IDModel docstring
  ([`292d01a`](https://github.com/jhnnsrs/rath/commit/292d01a66f59fc2498ae4f2c6baf822fb772bf8a))

- Remove pyqt5-qt5 from dev dependencies in pyproject.toml and uv.lock
  ([`6314343`](https://github.com/jhnnsrs/rath/commit/6314343ffe717e5ea1e4d107eceeb7db81c2a90b))

- Remove unnecessary whitespace in AuthTokenLink class
  ([`fd8f6f3`](https://github.com/jhnnsrs/rath/commit/fd8f6f3cb3c5c209cffd875abe6c203ed09cb2ce))

- Specify exact versions for pyqt5 and pyqt5-qt5 in dependencies
  ([`d7da6e2`](https://github.com/jhnnsrs/rath/commit/d7da6e2fc2e905074978bfa6b31897fc6ef54b7f))

### Features

- Add example script for querying countries using Rath
  ([`64fd24d`](https://github.com/jhnnsrs/rath/commit/64fd24ddff3c570d843a1260e7db328b7d2a6bda))

- Refactor code structure for improved readability and maintainability
  ([`35c842b`](https://github.com/jhnnsrs/rath/commit/35c842bfa4533d5da82b6fb7fe6fb3521c5e56c3))

- Swapping to semantic release
  ([`6cabcd2`](https://github.com/jhnnsrs/rath/commit/6cabcd2b57201230a5e12a790b91593993a968ef))


## v0.4.0 (2022-11-22)
