---
sidebar_label: rath
title: rath
---

## Rath Objects

```python
class Rath(KoiledModel)
```

A Rath is a client for a GraphQL API.

Links are used to define the transport logic of the Rath. A Rath can be
connected to a GraphQL API using a terminating link. By composing links to
form a chain, you can define the transport logic of the client.

For example, a Rath can be connected to a GraphQL API over HTTP by
composing an HTTP terminating link with a RetryLink. The RetryLink will
retry failed requests, and the HTTP terminating link will send the
requests over HTTP.

**Example**:

  ```python
  from rath import Rath
  from rath.links.retriy import RetryLink
  from rathlinks.aiohttp import  AioHttpLink
  
  retry = RetryLink()
  http = AioHttpLink(&quot;https://graphql-pokemon.now.sh/graphql&quot;)
  
  rath = Rath(link=compose(retry, link))
  async with rath as rath:
  await rath.aquery(...)
  ```

#### link

The terminating link used to send operations to the server. Can be a composed link chain.

#### auto\_connect

If true, the Rath will automatically connect to the server when a query is executed.

#### connect\_on\_enter

If true, the Rath will automatically connect to the server when entering the context manager.

#### aconnect

```python
async def aconnect()
```

Connect to the server.

This method needs to be called within the context of a Rath instance,
to always ensure that the Rath is disconnected when the context is
exited.

This method is called automatically when a query is executed if
`auto_connect` is set to True.

**Raises**:

- `NotEnteredError` - Raises an error if the Rath is not entered.

#### adisconnect

```python
async def adisconnect()
```

Disconnect from the server.

#### aquery

```python
async def aquery(query: Union[str, DocumentNode],
                 variables: Dict[str, Any] = None,
                 headers: Dict[str, Any] = None,
                 operation_name: str = None,
                 **kwargs) -> GraphQLResult
```

Query the GraphQL API.

Takes a querystring, variables, and headers and returns the result.
If provided, the operation_name will be used to identify which operation
to execute.

**Arguments**:

- `query` _str | DocumentNode_ - The query string or the DocumentNode.
- `variables` _Dict[str, Any], optional_ - The variables. Defaults to None.
- `headers` _Dict[str, Any], optional_ - Additional headers. Defaults to None.
- `operation_name` _str, optional_ - The operation_name to executed. Defaults to all.
- `**kwargs` - Additional arguments to pass to the link chain
  

**Raises**:

- `NotConnectedError` - An error when the Rath is not connected and autoload is set to false
  

**Returns**:

- `GraphQLResult` - The result of the query

#### query

```python
def query(query: Union[str, DocumentNode],
          variables: Dict[str, Any] = None,
          headers: Dict[str, Any] = None,
          operation_name: str = None,
          **kwargs) -> GraphQLResult
```

Query the GraphQL API.

Takes a querystring, variables, and headers and returns the result.
If provided, the operation_name will be used to identify which operation
to execute.

**Arguments**:

- `query` _str | DocumentNode_ - The query string or the DocumentNode.
- `variables` _Dict[str, Any], optional_ - The variables. Defaults to None.
- `headers` _Dict[str, Any], optional_ - Additional headers. Defaults to None.
- `operation_name` _str, optional_ - The operation_name to executed. Defaults to all.
- `**kwargs` - Additional arguments to pass to the link chain
  

**Raises**:

- `NotConnectedError` - An error when the Rath is not connected and autoload is set to false
  

**Returns**:

- `GraphQLResult` - The result of the query

#### subscribe

```python
def subscribe(query: str,
              variables: Dict[str, Any] = None,
              headers: Dict[str, Any] = None,
              operation_name: str = None,
              **kwargs) -> Iterator[GraphQLResult]
```

Subscripe to a GraphQL API.

Takes a querystring, variables, and headers and returns an async iterator
that yields the results.

**Arguments**:

- `query` _str | DocumentNode_ - The query string or the DocumentNode.
- `variables` _Dict[str, Any], optional_ - The variables. Defaults to None.
- `headers` _Dict[str, Any], optional_ - Additional headers. Defaults to None.
- `operation_name` _str, optional_ - The operation_name to executed. Defaults to all.
- `**kwargs` - Additional arguments to pass to the link chain
  

**Raises**:

- `NotConnectedError` - An error when the Rath is not connected and autoload is set to false
  

**Yields**:

- `Iterator[GraphQLResult]` - The result of the query as an async iterator

