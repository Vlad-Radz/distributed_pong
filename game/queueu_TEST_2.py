import asyncio

queue = asyncio.Queue()


async def worker(queue):
    while True:
        # Get a "work item" out of the queue.
        sleep_for = await queue.get()
        print(sleep_for)
        print("HELLO")

async def big_function():
    while True:
        await worker(queue=queue)

asyncio.run(big_function())