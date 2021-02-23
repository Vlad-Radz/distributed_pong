import pytest

import pygame

from game.game import GameController


@pytest.mark.xfail(reason="Conection to RabbitMQ not implemented (check #TODO below)")
@pytest.mark.usefixtures("container_rabbitmq")
def test_events_pygame(
        game_controller,
        communicator,
        player_self,
        player_other,
        game_events_queue):
    """
    Problems of this test:
    - too slow --> we should not wait 60 seconds (in the fixture), but somehow get signal, that RabbitMQ is up
    - reveals problems with code structure in the `game` module
    """
    from threading import Thread
    import time
    import pika

    connection = pika.BlockingConnection()
    channel = connection.channel()
    channel.exchange_declare(exchange='moves')  

    thread = Thread(
        target = game_controller.play,
        args = (communicator, player_self, [player_other], game_events_queue))
    thread.start()

    TESTEVENT = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN)
    pygame.event.post(TESTEVENT)
    pygame.event.post(TESTEVENT)
    pygame.event.post(TESTEVENT)

    QUIT_EVENT = pygame.event.Event(pygame.QUIT)
    pygame.event.post(QUIT_EVENT)
    thread.join()

    # TODO: connect to RabbitMQ, and check whether 3 messages in the channel
