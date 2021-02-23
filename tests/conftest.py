import subprocess
import json
import queue

import pytest

from game.game import GameController
from game.run import Communicator
from game.player_config import PlayerConfig


@pytest.fixture(scope="session")
def container_rabbitmq_name():
    return 'my-rabbit-192jc8D4la3mJS'


@pytest.fixture(scope="session")
def container_rabbitmq(container_rabbitmq_name):

    # Run docker container if not already running
    container_id = subprocess.check_output(
        f'docker ps -q -f name={container_rabbitmq_name}', shell=True)
    if not container_id:
        container_id = subprocess.check_output(
            f"docker run --rm -it -d --hostname {container_rabbitmq_name} \
                --name {container_rabbitmq_name} -p 15672:15672 -p 5672:5672 \
                rabbitmq:3-management",
            shell=True).decode("utf-8").split(" ")[0]
    
    print(f"container ID: {container_id}")

    yield

    # Teardown code
    subprocess.run(
        [
            'docker',
            'stop',
            f'{container_rabbitmq_name}'])


@pytest.fixture(scope="session")
def id_player_self():
    return "uid48382078"


@pytest.fixture(scope="session")
def id_player_other():
    return ["uid2871710801"]


@pytest.fixture(scope="session")
def player_self(id_player_self):
    return PlayerConfig(
        uuid=id_player_self,
        side='right',
        coord_x=670,
        coord_y=200,
        eligible_to_start=False)


@pytest.fixture(scope="session")
def player_other(id_player_other):
    return PlayerConfig(
        uuid=id_player_other,
        side='left',
        coord_x=20,
        coord_y=200,
        eligible_to_start=True)


@pytest.fixture(scope="session")
def game_controller():
    return GameController()


@pytest.fixture(scope="session")
def game_events_queue():
    return queue.Queue()


@pytest.fixture(scope="session")
def server_host():
    return subprocess.check_output("hostname -I", shell=True).decode("utf-8").split(" ")[0]


@pytest.fixture(scope="session")
def communicator(
        id_player_self,
        id_player_other,
        server_host):
    import time
    # time.sleep(60)  # We need this because RabbitMQ is up only after some time --> replace via diff. mechanism
    return Communicator(
        msg_broker_host=server_host,
        my_routing_key=id_player_self,
        topics=id_player_other,
        queue_events=game_events_queue)
