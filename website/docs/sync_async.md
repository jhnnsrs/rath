---
sidebar_position: 3
sidebar_label: "Sync, Async and Qt"
---

# Sync and Async Api

Rath tries to faciliate the usage of async and sync consumers alike and hide implementation details under a coverning api that
should feel natural for both type of scenarios. No matter which Terminating Link **async** or **sync** you are choosing. The Api i
always the following depending on the context:

```python title="async.api"

async with Rath(...) as rath:

    result = await rath.aexecute(...)

    async for reslt in rath.asubscribe(...):
        print(result)


```

```python title="sync.api"

with Rath(...) as rath:

    result = rath.execute(...)

    for result in rath.subscribe(...):
        print(result)


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

Rath uses the **koil library** to facilitate this "context switch". In short when using koil **and** running under a sync context, rath
will either spin up a new event loop in another thread on connect (or entering the context manager). You now interact threadsafe with
that event loop through a synchronous api. This means you can even create asyncio.like Tasks in the other event loop (using as_task),
or iterate over results in the other loop. On closing the context manager or disconnect, that event loop gets closed and all tasks cancelled.

# QT

Koil can be also run globally (for example in a pyqt app) and can overwrite the task classes that are being returned, so that you can easily integrate
rath in a qt app and use signals.

```python
from koil.qt import QtKoil


class QWidget(qtpy.QtWidget):

    def __init__(*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.koil = QtKoil(auto_connect=True) # WIll automaticalll create a threaded eventloop and destroy it on application close
        self.rath = Rath(...)
        self.text = QLineEdit()

        self.rath.connect() # disconnecting will automatically happen on application close or on call to disconnect
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

### However

Using async libraries in a sync environment is not an easy undertaking and comes with a lot of pitfalls, and performance penalties.
So when you start out your project make sure you understand what you are dealing with.
