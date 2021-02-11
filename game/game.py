"""
Reference: https://www.101computing.net/pong-tutorial-using-pygame-adding-a-scoring-system/
"""
import queue
from typing import List
import pickle
import os
from pathlib import Path

import pygame

from game_objects.paddle import Paddle
from game_objects.ball import Ball

class GameController:

    # TODO: my_paddle: check for key pressing inside pygame event loop.
    # If no pressed, then check the queue --> should be as attribute
    # We should get not only the move, but also the routing_key --> loop over paddled and move the ones, whose was moved
    # --> list of paddles
    # Also I should get coordinates for my_paddle
    def __init__(self):

        pygame.init()

        # Define some colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        # Open a new window
        size = (700, 500)
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption('Pong')

        bg = pygame.image.load(
            os.path.join(Path(__file__).resolve().parent.parent, 'static/background_game_start.gif'))
        self.screen.blit(bg, (0, 0))
        self.screen.blit(pygame.font.SysFont('Helvetica', 36).render(
            'Waiting for another player to join...', 1, self.WHITE), (90, 10))
        pygame.display.update()

    def play(
            self,
            communicator,  # TODO: not the best pattern. Reason: non-ideal design upfront
            my_player,
            other_players: List,
            queue_events: queue.Queue):

        ball = Ball(self.WHITE, 10, 10)
        ball.rect.x = 345
        ball.rect.y = 195

        # This will be a list that will contain all the sprites we intend to use in our game.
        all_sprites_list = pygame.sprite.Group()
        all_sprites_list.add(ball)

        my_paddle = Paddle(self.WHITE, 10, 100)
        my_paddle.rect.x = my_player.coord_x
        my_paddle.rect.y = my_player.coord_y
        all_sprites_list.add(my_paddle)

        other_paddle = Paddle(self.WHITE, 10, 100)
        other_paddle.rect.x = other_players[0].coord_x
        other_paddle.rect.y = other_players[0].coord_y
        all_sprites_list.add(other_paddle)

        # The clock will be used to control how fast the screen updates
        clock = pygame.time.Clock()

        # TODO: bug: it will work only for 2 players now
        # Initialise player scores
        scoreA = 0
        scoreB = 0

        # The loop will carry on until the user exit the game (e.g. clicks the close button).
        carryOn = True

        # -------- Main Program Loop -----------
        while carryOn:
            # --- Main event loop
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    carryOn = False  # Flag that we are done so we exit this loop
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:
                        carryOn = False
                    if event.key == pygame.K_UP:
                        my_paddle.moveUp(5)
                        communicator.publish({'action': "up", 'player_id': str(my_player.uuid)})
                    if event.key == pygame.K_DOWN:
                        my_paddle.moveDown(5)
                        communicator.publish({'action': "down", 'player_id': str(my_player.uuid)})

            try:
                message = queue_events.get_nowait()
                queue_events.task_done()
                if message['action'] == "up":
                    other_paddle.moveUp(5)
                elif message['action'] == "down":
                    other_paddle.moveDown(5)
            except queue.Empty:
                pass
                # print("Was empty")

            # --- Game logic should go here
            all_sprites_list.update()

            # Check if the ball is bouncing against any of the 4 walls:
            if ball.rect.x >= 690:
                scoreA += 1
                ball.velocity[0] = -ball.velocity[0]
            if ball.rect.x <= 0:
                scoreB += 1
                ball.velocity[0] = -ball.velocity[0]
            if ball.rect.y > 490:
                ball.velocity[1] = -ball.velocity[1]
            if ball.rect.y < 0:
                ball.velocity[1] = -ball.velocity[1]

                # Detect collisions between the ball and the paddles
            if pygame.sprite.collide_mask(ball, my_paddle):
                ball.bounce()

            if pygame.sprite.collide_mask(ball, other_paddle):
                ball.bounce()

            # --- Drawing code should go here
            # First, clear the screen to black.
            self.screen.fill(self.BLACK)
            # Draw the net
            pygame.draw.line(self.screen, self.WHITE, [349, 0], [349, 500], 5)

            # Now let's draw all the sprites in one go. (For now we only have 2 sprites!)
            all_sprites_list.draw(self.screen)

            # Display scores:
            font = pygame.font.Font(None, 74)
            text = font.render(str(scoreA), 1, self.WHITE)
            self.screen.blit(text, (250, 10))
            text = font.render(str(scoreB), 1, self.WHITE)
            self.screen.blit(text, (420, 10))

            # --- Go ahead and update the screen with what we've drawn.
            pygame.display.flip()

            # --- Limit to 60 frames per second
            clock.tick(20)

        # Once we have exited the main program loop we can stop the game engine:
        pygame.quit()
