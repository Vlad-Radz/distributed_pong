import socket
import uuid
from _thread import start_new_thread  # low-level primitives for working with multiple threads
import queue
import pickle
# TODO: needs to be run through isort for the right import sorting
# TODO: use structlog for better logging

import pika

from player_config import PlayerConfig


class Orchestrator:

    def __init__(self, host: str, port: int, my_queue: queue.Queue):
        self.host = host
        self.port = port
        self.config_players_queue = my_queue
        self.connected_players_queue = queue.Queue()

        # socket: A socket is one endpoint of a two-way communication link between two programs running on the network.
        # socket: is bound to a port number so that the TCP layer can identify the app that data is destined to be sent to.
        # socket: software structure
        # ####
        # AF_INET & AF_INET6: address (and protocol) families
        # SOCK_STREAM means that it is a TCP socket.
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))  # Bind the socket to address
        # Enable a server to accept connections
        # number of unaccepted connections that the system will allow before refusing new connections
        self.socket.listen(expected_players)
        print("Waiting for a connection")

    def orchestrate(self):
        while True:
            # Set up a queue in message broker for future communication between players
            # TODO: abstraction from message broker needed; probably using abstract base classes and / or facade pattern
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=self.host))
            channel = connection.channel()
            channel.exchange_declare(exchange='moves', exchange_type='direct')

            # `conn` is a new socket object usable to send and receive data on the connection
            # `address` is the address bound to the socket on the other end of the connection.
            conn, addr = self.socket.accept()
            print(conn, type(conn))
            print("Connected to: ", addr)

            # Start a new thread and return its identifier.
            # The thread executes the function function with the argument list args (which must be a tuple).
            # TODO: asyncio implmenetation might be better
            start_new_thread(self.handle_connection, (conn,))

    def handle_connection(self, conn: socket.socket):
        config_player = self.config_players_queue.get()
        # TODO: pickle is not the best tool, since can be used only for Python and has security issues.
        conn.send(pickle.dumps(config_player))
        self.config_players_queue.task_done()

        self.connected_players_queue.put(config_player)
        # TODO: refactor methods, better division of responsibilities
        # TODO: idea with second queue is not perfect - any other structure with shared data? look into asyncio
        # TODO: implement max possible number of players
        if self.connected_players_queue.qsize() == expected_players:
            print("HELLO")
            conn.sendall(pickle.dumps((list(self.connected_players_queue.queue))))

        print("Connection Closed")
        conn.close()


host = '192.168.178.43'
port = 5555
expected_players = 2

player_left = PlayerConfig(
    uuid=uuid.uuid4(),
    side='left',
    coord_x=20,
    coord_y=200)

player_right = PlayerConfig(
    uuid=uuid.uuid4(),
    side='right',
    coord_x=670,
    coord_y=200)

# Not needed now, because not implemented yet
player_up = ...
player_down = ...

# I use FIFO queue since order is important for this game (from my perspective)
players_queue = queue.Queue(maxsize=expected_players)
players_queue.put(player_left)
players_queue.put(player_right)

server = Orchestrator(host=host, port=port, my_queue=players_queue)
server.orchestrate()
