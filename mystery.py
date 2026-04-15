import random
import time
from const import *
from ball import Ball
from airplane import PlayerAirplane
from sound_manager import * 

class MysteryBall(Ball):
    """
    A MysteryBall is a special type of Ball that grants temporary abilities to the player's airplane.

    MysteryBalls come in several types (MYSTERY_BALL1, MYSTERY_BALL2, MYSTERY_BALL3), each
    providing a different power-up. When the player collects a MysteryBall, a corresponding ability
    is activated for a limited duration.
    """

    def __init__(self, size, x, y, vx, vy, color, ball_type):
        """
        Initialize a MysteryBall with the given parameters.

        Args:
            size (int): The radius or size of the ball.
            x (float): The initial x-position of the ball.
            y (float): The initial y-position of the ball.
            vx (float): The horizontal velocity of the ball.
            vy (float): The vertical velocity of the ball.
            color (str): The color of the ball (unused if using images).
            ball_type (int): The type of the mystery ball, determining the ability it grants.
        """
        super().__init__(size, x, y, vx, vy, color)
        self.type = ball_type
        self.time_collected = None

        # Set the MysteryBall image based on its type
        self._shape = f"picture/MYSTERY_BALL{self.type}.gif"
        self.turtle.screen.register_shape(self._shape)
        self.turtle.shape(self._shape)
        self.turtle.goto(self.x, self.y)

    def move(self):
        """
        Move the MysteryBall according to its vertical velocity.
        
        This updates the y-position of the MysteryBall, causing it to fall down the screen.
        """
        self.y += self.vy
        self.turtle.clear()
        self.turtle.penup()
        self.turtle.goto(self.x, self.y)

    def is_off_screen(self):
        """
        Check if the MysteryBall has moved off the screen.

        Returns:
            bool: True if the MysteryBall is below the bottom of the screen, False otherwise.
        """
        return self.y < -SCREEN_HEIGHT / 2

    def activate_ability(self, player: PlayerAirplane):
        """
        Activate the MysteryBall's ability on the player's airplane.

        Args:
            player (PlayerAirplane): The player's airplane object.
        """
        SoundManager.play_powerup_sound()  # Play power-up sound
        if self.type == MYSTERY_BALL1:
            player.activate_tridirectional_shooting()
        elif self.type == MYSTERY_BALL2:
            player.increase_health()
        elif self.type == MYSTERY_BALL3:
            player.double_speed()
        self.time_collected = time.time()
        self._hide_ball()

    def is_ability_active(self, player: PlayerAirplane):
        """
        Check if the MysteryBall's ability should still be active.

        If the duration of the ability exceeds MYSTERY_BALL_LIFETIME, it will deactivate the ability.

        Args:
            player (PlayerAirplane): The player's airplane object.

        Returns:
            bool: True if the ability is still active, False otherwise.
        """
        if self.time_collected and (time.time() - self.time_collected) > MYSTERY_BALL_LIFETIME:
            player.deactivate_ability()
            return False
        return True

    def _hide_ball(self):
        """
        Hide the MysteryBall's turtle representation.

        This method is called after the ball has been collected by the player.
        """
        self.turtle.hideturtle()
        self.turtle.clear()