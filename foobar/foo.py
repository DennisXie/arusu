import anyio
import anyio.abc
import time
import threading


def sync_timer():
    for i in range(10):
        time.sleep(1)
        print(f"run {i}")
    print("run finished")


async def async_timer():
    import asyncio
    for i in range(10):
        await asyncio.sleep(1)
        print(f"async run {i}")
    print("async run finished")


async def another_async_timer():
    import asyncio
    for i in range(20):
        await asyncio.sleep(0.5)
        print(f"another async run {i}")
    print("another async run finished")


async def start_async_timer_asyncio():
    import asyncio
    asyncio.create_task(async_timer())
    asyncio.create_task(another_async_timer())


async def start_async_timer_anyio():
    async with anyio.create_task_group() as tg:
        tg.start_soon(async_timer)
        tg.start_soon(another_async_timer)
    print("start_async_timer_anyio return")


async def anyio_async_timer():
    for i in range(10):
        await anyio.sleep(1)
        print(f"async run {i}")
    print("async run finished")


async def another_anyio_async_timer():
    for i in range(10):
        await anyio.sleep(0.5)
        print(f"another async run {i}")
    print("another async run finished")


async def main():
    # await start_async_timer_anyio()
    await start_async_timer_asyncio()
    print("main start finished")
    await anyio.sleep(15)
    print("sleep finished")

if __name__ == "__main__":
    anyio.run(main)
