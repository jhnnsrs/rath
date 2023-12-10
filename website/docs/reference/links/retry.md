---
sidebar_label: retry
title: links.retry
---

## RetryLink Objects

```python
class RetryLink(ContinuationLink)
```

RetriyLink is a link that retries a operation  fails.
This link is stateful, and will keep track of the number of times the
subscription has been retried.

#### maximum\_retry\_attempts

The maximum number of times the operation function will be called, before the operation fails.

#### sleep\_interval

The number of seconds to wait before retrying the operation.

