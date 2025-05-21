# CHANGELOG


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
