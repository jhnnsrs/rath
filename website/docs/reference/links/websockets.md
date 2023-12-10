---
sidebar_label: websockets
title: links.websockets
---

## WebSocketLink Objects

```python
class WebSocketLink(AsyncTerminatingLink)
```

WebSocketLink is a terminating link that sends operations over websockets using websockets

This is a terminating link, so it should be the last link in the chain.
This is a stateful link, keeing a connection open and sending messages over it.

#### ws\_endpoint\_url

The endpoint url to connect to

#### allow\_reconnect

Should the websocket try to reconnect if it fails

#### time\_between\_retries

The sleep time between retries

#### max\_retries

The maximum amount of retries before giving up

#### ssl\_context

The SSL Context to use for the connection

#### token\_loader

A function that returns the token to use for the connection as a query parameter

