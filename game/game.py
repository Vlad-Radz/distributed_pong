"""
Reference: https://www.101computing.net/pong-tutorial-using-pygame-adding-a-scoring-system/
"""
from typing import List

import pygame

from game_objects.paddle import Paddle
from game_objects.ball import Ball


class GameController:

    # TODO: my_paddle: check for key pressing inside pygame event loop.
    # If no pressed, then check the queue --> should be as attribute
    # We should get not only the move, but also the routing_key --> loop over paddled and move the ones, whose was moved
    # --> list of paddles
    # Also I should get coordinates for my_paddle
    def __init__(self, my_player, other_players: List):
        pygame.init()

        # Define some colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)

        # Open a new window
        size = (700, 500)
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Pong")

        self.ball = Ball(self.WHITE, 10, 10)
        self.ball.rect.x = 345
        self.ball.rect.y = 195

        # This will be a list that will contain all the sprites we intend to use in our game.
        all_sprites_list = pygame.sprite.Group()
        all_sprites_list.add(self.ball)

        self.my_paddle = Paddle(self.WHITE, 10, 100)
        self.my_paddle.rect.x = my_player.coord_x
        self.my_paddle.rect.y = my_player.coord_y
        all_sprites_list.add(self.my_paddle)

        for player in other_players:
            paddle = Paddle(self.WHITE, 10, 100)
            paddle.rect.x = player.coord_x
            paddle.rect.y = player.coord_y
            all_sprites_list.add(paddle)

        # The clock will be used to control how fast the screen updates
        clock = pygame.time.Clock()

        # TODO: bug: it will work only for 2 players now
        # Initialise player scores
        scoreA = 0
        scoreB = 0

        # The loop will carry on until the user exit the game (e.g. clicks the close button).
        carryOn = True

        # TODO: I STOPPED HERE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        # -------- Main Program Loop -----------
        while carryOn:
            # --- Main event loop
            for event in pygame.event.get():  # User did something
                if event.type == pygame.QUIT:  # If user clicked close
                    carryOn = False  # Flag that we are done so we exit this loop
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_x:  # Pressing the x Key will quit the game
                        carryOn = False
                    if event.key == pygame.K_UP:
                        self.my_paddle.moveUp(5)
                    if event.key == pygame.K_DOWN:  # Pressing the x Key will quit the game
                        self.my_paddle.moveDown(5)

            # Moving the paddles when the use uses the arrow keys (player A) or "W/S" keys (player B)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:
                self.my_paddle.moveUp(5)
            if keys[pygame.K_s]:
                self.my_paddle.moveDown(5)
            if keys[pygame.K_UP]:
                paddle.moveUp(5)
            if keys[pygame.K_DOWN]:
                paddle.moveDown(5)

                # --- Game logic should go here
            all_sprites_list.update()

            # Check if the ball is bouncing against any of the 4 walls:
            if self.ball.rect.x >= 690:
                scoreA += 1
                self.ball.velocity[0] = -self.ball.velocity[0]
            if self.ball.rect.x <= 0:
                scoreB += 1
                self.ball.velocity[0] = -self.ball.velocity[0]
            if self.ball.rect.y > 490:
                self.ball.velocity[1] = -self.ball.velocity[1]
            if self.ball.rect.y < 0:
                self.ball.velocity[1] = -self.ball.velocity[1]

                # Detect collisions between the ball and the paddles
            if pygame.sprite.collide_mask(self.ball, self.my_paddle) or pygame.sprite.collide_mask(self.ball, paddle):
                self.ball.bounce()

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
            clock.tick(60)

        # Once we have exited the main program loop we can stop the game engine:
        pygame.quit()