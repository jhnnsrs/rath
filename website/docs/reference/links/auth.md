---
sidebar_label: auth
title: links.auth
---

## AuthTokenLink Objects

```python
class AuthTokenLink(ContinuationLink)
```

AuthTokenLink is a link that adds an authentication token to the context.
The authentication token is retrieved by calling the token_loader function.
If the wrapped link raises an AuthenticationError, the token_refresher function
is called again to refresh the token.

This link is statelss, and does not store the token. It is up to the user to
store the token and pass it to the token_loader function.

#### token\_loader

The function used to load the authentication token. This function should
return a string containing the authentication token.

#### token\_refresher

The function used to refresh the authentication token. This function should
return a string containing the authentication token.

#### maximum\_refresh\_attempts

The maximum number of times the token_refresher function will be called, before the operation fails.

#### load\_token\_on\_connect

If True, the token_loader function will be called when the link is connected.

#### load\_token\_on\_enter

If True, the token_loader function will be called when the link is entered.

