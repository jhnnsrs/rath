# rath

[![codecov](https://codecov.io/gh/jhnnsrs/rath/branch/master/graph/badge.svg?token=UGXEA2THBV)](https://codecov.io/gh/jhnnsrs/rath)
[![PyPI version](https://badge.fury.io/py/rath.svg)](https://pypi.org/project/rath/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://pypi.org/project/rath/)
![Maintainer](https://img.shields.io/badge/maintainer-jhnnsrs-blue)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/rath.svg)](https://pypi.python.org/pypi/rath/)
[![PyPI status](https://img.shields.io/pypi/status/rath.svg)](https://pypi.python.org/pypi/rath/)
[![PyPI download month](https://img.shields.io/pypi/dm/rath.svg)](https://pypi.python.org/pypi/rath/)

### DEVELOPMENT

## Inspiration

Rath is an Apollo (that typescript thing) like library for python, it supports a link like structure
to facilitate and multiple links

## Features

- includes modular links to support specificatiosn for

  - Subscriptions (via websockets)
  - File Uploads (multipart specifications)

- Works well with turms created queries

## Installation

```bash
pip install rath
```

## Usage Query

```python
from rath.links.auth import AuthTokenLink
from rath.links.aiohttp import AioHttpLink
from rath.gql import gql

auth = AuthTokenLink(token_loader=aload_token)
link = AioHttpLink(url="http://localhost:3000/graphql")


rath = Rath(links=[auth,link])

rath.connect()

query = qgl("query space ex")

result = rath.execute(query)
```

Generate beautifully typed Operations, Enums,...

### Why Rath

Well "apollo" is already taken as a name, and rath (according to wikipedia) is an etruscan deity identified with Apollo.

## Examples

This github repository also contains an example client with a turms generated query with the public SpaceX api, as well as a sample of the generated api.

## CLI

```bash
rath run
```
