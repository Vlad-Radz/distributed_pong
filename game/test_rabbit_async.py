
import asyncio
from aio_pika import connect_robust
import threading


class Listener:

    async def _listen(self, loop, topics):
        connection = await connect_robust(
            "amqp://guest:guest@192.168.178.43/", loop=loop
        )
        queue_name = ""
        routing_key = "hello"

        # Creating channel
        channel = await connection.channel()
        # Declaring queue
        queue = await channel.declare_queue(queue_name)
        # Declaring exchange
        exchange = await channel.declare_exchange('moves')
        for topic in topics:
            # Binding queue
            await queue.bind(exchange, topic)

        # Receiving message
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(message.body)
                    print(message.routing_key)

    def loop_in_thread(self, loop, topics):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._listen(loop, topics))

    def listen(self, topics):
        loop = asyncio.get_event_loop()
        t = threading.Thread(target=self.loop_in_thread, args=(loop,topics,))
        t.start()
        # loop.run_until_complete(self._listen(loop))
        print("HERE")
        # loop.close()

    """
    incoming_message = await queue.get(timeout=5)
    print(incoming_message)

    # Confirm message
    await incoming_message.ack()

    await queue.unbind(exchange, routing_key)
    await queue.delete()
    await connection.close()
    """

listener = Listener()
listener.listen(topics=["hello", "poka"])
print("HEELLLO")
