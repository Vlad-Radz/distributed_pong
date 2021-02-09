import asyncio
import random
import time
import threading

"""
class Test:

    def __init__(self):
        # Create a queue that we will use to store our "workload".
        self.queue = asyncio.Queue()

    async def worker(self, queue):
        #while True:
        # Get a "work item" out of the queue.
        sleep_for = await queue.get()

        # Sleep for the "sleep_for" seconds.
        await asyncio.sleep(sleep_for)

        # Notify the queue that the "work item" has been processed.
        queue.task_done()

    async def main(self):
        # Generate random timings and put them into the queue.
        # for _ in range(3):
        sleep_for = random.uniform(0.05, 1.0)
        print(f"sleep_for: {sleep_for}")
        self.queue.put_nowait(sleep_for)

        # await self.worker(self.queue)

    def listen_queue(self):
        asyncio.run(self.main())
        asyncio.run(self.worker(self.queue))


test = Test()
test.listen_queue()
"""


class Communicator:
    '''
    This class is responsible for communication with other players via a message broker.
    '''

    def __init__(self):
        self.queue_events = asyncio.Queue()

    async def _listen(self, loop):
        for _ in range(2):
            self.queue_events.put_nowait("hello")
            # await asyncio.sleep(5)
            time.sleep(5)

    def _loop_in_thread(self, method, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(method(loop))

    def listen(self):
        '''
        This method will be run in background, listening to new events
        '''
        loop = asyncio.get_event_loop()
        t = threading.Thread(target=self._loop_in_thread, args=(self._listen, loop,))
        t.start()

    async def _receive(self, loop):
        while True:
            sleep_for = await self.queue_events.get()
            print(f"GOT IT: {sleep_for}")
            self.queue_events.task_done()

    def receive(self):
        loop = asyncio.new_event_loop()
        t = threading.Thread(target=self._loop_in_thread, args=(self._receive, loop,))
        t.start()


test = Communicator()
test.listen()
test.receive()
