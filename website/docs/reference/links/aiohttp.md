---
sidebar_label: aiohttp
title: links.aiohttp
---

## AIOHttpLink Objects

```python
class AIOHttpLink(AsyncTerminatingLink)
```

AIOHttpLink is a terminating link that sends operations over HTTP using aiohttp.

Aiohttp is a Python library for asynchronous HTTP requests. This link uses the
standard aiohttp library to send operations over HTTP, but provides an ssl context
that is configured to use the certifi CA bundle by default. You can override this
behavior by passing your own SSLContext to the constructor.

#### endpoint\_url

endpoint_url is the URL to send operations to.

#### ssl\_context

ssl_context is the SSLContext to use for the aiohttp session. By default, this
is a context that uses the certifi CA bundle.

#### auth\_errors

auth_errors is a list of HTTPStatus codes that indicate that the request was
unauthorized. By default, this is just HTTPStatus.FORBIDDEN, but you can
override this to include other status codes that indicate that the request was
unauthorized.

#### json\_encoder

json_encoder is the JSONEncoder to use when serializing the payload. By default,
this is a DateTimeEncoder that extends the default python json decoder to serializes datetime objects to ISO 8601 strings.

