---
sidebar_position: 1
sidebar_label: "Sync vs Async"
---

# Sync vs Async

Rath tries to faciliate the usage of async and sync consumers alike and hide implementation details under a coverning api that
should feel natural for both type of scenarios. No matter which Terminating Link **async** or **sync** you are choosing. The Api i
always the following depending on the context:

```python title="async.api"

async with Rath(...) as rath:

    result = await rath.aexecute(...)

    async for reslt in rath.asubscribe(...):
        print(result)


```

```python title="async.api"

with Rath(...) as rath:

    result = rath.execute(...)

    for result in rath.subscribe(...):
        print(result)


```

If your terminating link does not involve any connection logic that needs to facilitate subscriptions, you can generally omit the
context manager eg:

```python title="sync.api"
rath = Rath(...)

result = rath.execute("query")
```

```python title="sync.api"
rath = Rath(...)

result = await rath.aexecute("query")
```

:::tip
You can call the execute api also from an asynchronous context and await the result in async world "execute" and "aexecute" are both
coroutines (execute just checks additionally if we are in the loop)
:::

If you really don't want to use context managers and handle the connection logic and killing of threads or tasks yourself you
can always just call "connect" and "disconnect"

```python
rath = Rath(...)
rath.connect()

for e in rath.subscribe(...)
    print(e)

#rath disconnect
rath.disconnect()
```

:::warning
If you choose this approach and forget to disconnect, you will have a deamon thread running in the background that is still being
connected. Choose this wisely!
::::

### How this is done...

Rath uses the koil library to facilitate this "context switch". In short when using koil _and_ running under a sync context, rath
will either spin up a new event loop in another thread on connect (or entering the context manager). No you are allow you to interact with
that event loop through a synchronous api. This means you can even create asyncio.like Tasks synchronously in the other event loop (using as_task),
or iterate over results in the other loop. On closing the context manager or disconnect, that event loop gets closed and all tasks cancelled.

Koil can be also run globally (for example in a pyqt app) and will return, task classes with signals that you can connect to. E.g.

```python
class QWidget(qtpy.QtWidget):

    def __init__(*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.koil = QtKoil(auto_create=True) # WIll automaticalll create a threaded eventloop
        self.rath = Rath(...)
        self.text = QLineEdit()
        self.rath.connect() # disconnecting will automatically happen on application close
        self.subscribe_to_events()

    def subscribe_to_events(self):

        self.beastSubscription = self.rath.subscribe("""subscribtion {
            watchBeasts {
                name
                legs
            }
        }""", as_task=True)

        self.beastSubscription.yielded.connect(self.new_beast) #pyqt signal for yield on task


    def new_beast(res: GraphQLResult):
        self.text.setText(res.data["watchBeasts"]["name"])


    def close():
        self.beastSubscription.cancel()

```

#### However

Using async libraries in a sync environment is not an easy undertaking and comes with a lot of pitfalls, and performance penalties.
So when you start out your project make sure you understand what you are dealing with.
