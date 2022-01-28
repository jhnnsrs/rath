import asyncio


# This is an example of an generator actor
async def gen(provision: int):

    while True:
        await asyncio.sleep(0.1)
        assignation = yield
        print("Hallo")
        assignation = yield 15
        print("New Assignation:", assignation)
        raise Exception("Error")


async def generate_message():
    x = 0
    while True:
        await asyncio.sleep(0.4)
        x += 1
        if x == 2:
            yield "stop"
        else:
            yield "yield"


async def main():

    x = gen(2)
    t = generate_message()

    await x.asend(None)

    async for i in t:
        try:
            print(await x.asend(i))
        except StopAsyncIteration:
            break


asyncio.run(main())
