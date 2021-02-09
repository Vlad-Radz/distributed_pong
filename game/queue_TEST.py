import asyncio
import random


class Test:

    def __init__(self):
        # Create a queue that we will use to store our "workload".
        self.queue = asyncio.Queue()

    async def worker(self, queue):
        while True:
            # Get a "work item" out of the queue.
            sleep_for = await queue.get()

            # Sleep for the "sleep_for" seconds.
            await asyncio.sleep(sleep_for)

            # Notify the queue that the "work item" has been processed.
            queue.task_done()

    async def main(self):
        # Generate random timings and put them into the queue.
        for _ in range(10):
            sleep_for = random.uniform(0.05, 1.0)
            print(f"sleep_for: {sleep_for}")
            self.queue.put_nowait(sleep_for)

        # Create three worker tasks to process the queue concurrently.
        tasks = []
        for i in range(3):
            task = asyncio.create_task(self.worker(self.queue))
            tasks.append(task)

        # Wait until the queue is fully processed.
        await self.queue.join()
        # Cancel our worker tasks.
        for task in tasks:
            task.cancel()
        # Wait until all worker tasks are cancelled.
        await asyncio.gather(*tasks, return_exceptions=True)

    def listen_queue(self):
        asyncio.run(self.main())

test = Test()
test.listen_queue()
