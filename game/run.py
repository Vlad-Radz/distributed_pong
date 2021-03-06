import asyncio
import pickle
import socket
from typing import List, Tuple, Type
import threading
import queue
import subprocess

from aio_pika import connect_robust
import pika

from game.player_config import PlayerConfig
from game.game import GameController


class Initiator:
    '''
    This class is responsible for communication with server:
        1. It gets DTO for own player; id of own player is needed for creation of topic in msg broker
        2. Afterwards it listens for socket and gets list of DTOs for all players; it should know ids of other players
        to know to what topics in message brokers to listen to.
    '''

    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.addr = (self.host, self.port)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def get_configs(self) -> Tuple[PlayerConfig, List[PlayerConfig]]:
        my_player = self._connect()
        print(f"My player is: {my_player}")
        while True:
            data = self.client.recv(2048)
            if data:
                other_players: List[PlayerConfig] = pickle.loads(data)
                other_players.remove(my_player)
                break
        return my_player, other_players

    def _connect(self):
        self.client.connect(self.addr)
        return pickle.loads(self.client.recv(2048))

    def send(self, data):
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(2048).decode()
            return reply
        except socket.error as e:
            return str(e)


class Communicator:
    '''
    This class is responsible for communication with other players via a message broker.
    '''

    def __init__(
            self,
            msg_broker_host: str,
            my_routing_key: str,
            topics: List[str],
            queue_events: asyncio.Queue):
        self.msg_broker_host = msg_broker_host
        self.my_routing_key = my_routing_key
        self.mq_channel = self._set_up_msg_broker_connection()
        self.topics = topics
        self.exchange = 'moves'  # TODO: is not good that it knows the name of exchange - should get it from orchestrator
        self.queue_events = queue_events
        # TODO: I need to close connection somewhere: `connection.close()`

    def _set_up_msg_broker_connection(self):
        mq_connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=self.msg_broker_host))
        channel = mq_connection.channel()
        return channel

    async def _listen(self, loop):
        # TODO: user and pwd should be submitted (pwd manager? parameter store?), not hardcored
        connection = await connect_robust(
            f"amqp://guest:guest@{self.msg_broker_host}/", loop=loop
        )
        queue_name = ""

        # Creating channel
        channel = await connection.channel()
        # Declaring queue
        queue = await channel.declare_queue(queue_name)
        # Declaring exchange
        exchange = await channel.declare_exchange(self.exchange)
        for topic in self.topics:
            # Binding queue
            await queue.bind(exchange, topic)

        # Receiving message
        async with queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    print(pickle.loads(message.body))
                    print(message.routing_key)
                    message_to_put = pickle.loads(message.body)  # TODO: actually no need to pickle here
                    self.queue_events.put_nowait(message_to_put)

    def _loop_in_thread(self, method, loop):
        asyncio.set_event_loop(loop)
        loop.run_until_complete(method(loop))

    def listen(self):
        '''
        This method will be run in background, listening to new events
        '''
        # TODO: I know that it's a bad practice to run async code in a thread for this use case - code should be rewritten as coroutines.
        loop = asyncio.get_event_loop()
        t = threading.Thread(target=self._loop_in_thread, args=(self._listen,loop,))
        t.start()

    def publish(self, message: dict):
        '''
        Facade method for the publish method of RabbitMQ
        '''
        self.mq_channel.exchange_declare(exchange=self.exchange)
        self.mq_channel.basic_publish(
            exchange=self.exchange,
            routing_key=self.my_routing_key,
            body=pickle.dumps(message))


class Player:
    '''
    This is the service class interacting with other object via dependency injection.
    '''

    def __init__(
            self,
            mq_host: str,
            initiator: Initiator,
            communicator: Type[Communicator],
            game_controller: Type[GameController]):
        self.initiator = initiator

        self.game_controller = game_controller()

        my_player, other_players = initiator.get_configs()
        print(my_player, other_players)
        my_id = str(my_player.uuid)
        other_players_ids = [str(player.uuid) for player in other_players]

        queue_events = queue.Queue()

        # TODO: here is a potential bug: I don't check, if everybody subscribed to all the required topics -> missed moves
        self.communicator = communicator(
            msg_broker_host=mq_host,
            my_routing_key=my_id,
            topics=other_players_ids,
            queue_events=queue_events)
        self.communicator.listen()  # This will open a thread with daemon listening for messages from message broker
        self.game_controller.play(
            communicator=self.communicator,
            my_player=my_player,
            other_players=other_players,
            queue_events=queue_events)


if __name__ == "__main__":
    # I use same host for communication over sockets and message broker
    # TODO: to env vars
    host = subprocess.check_output("hostname -I", shell=True).decode("utf-8").split(" ")[0]
    port = 5555

    initiator = Initiator(host=host, port=port)
    player = Player(
        mq_host=host,
        initiator=initiator,
        communicator=Communicator,
        game_controller=GameController)
