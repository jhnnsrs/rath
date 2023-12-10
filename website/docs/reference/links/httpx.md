---
sidebar_label: httpx
title: links.httpx
---

## HttpxLink Objects

```python
class HttpxLink(AsyncTerminatingLink)
```

HttpxLink is a terminating link that sends operations over HTTP using httpx

#### endpoint\_url

endpoint_url is the URL to send operations to.

#### auth\_errors

auth_errors is a list of HTTPStatus codes that indicate an authentication error.

