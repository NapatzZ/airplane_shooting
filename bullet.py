import pygame  
from const import *
from ball import Ball
from sound_manager import * 

class Bullet(Ball):
    """
    A Bullet is a small projectile that can be fired by either the player or an enemy.
    It inherits from the Ball class, adding directional heading and owner attributes.
    """

    def __init__(self, x, y, vx, vy, owner):
        """
        Initialize a new Bullet instance and play the shooting sound effect.

        Args:
            x (float): The initial x-coordinate of the bullet.
            y (float): The initial y-coordinate of the bullet.
            vx (float): The horizontal velocity component of the bullet.
            vy (float): The vertical velocity component of the bullet.
            owner (str): The owner of the bullet, either PLAYER or ENEMY.
        """
        color = ORANGE if owner == PLAYER else RED
        super().__init__(size=5, x=x, y=y, vx=vx, vy=vy, color=color)
        self.owner = owner
        self.turtle.setheading(90 if owner == PLAYER else 270)
        self.turtle.shape("circle")
        self.turtle.shapesize(stretch_wid=0.5, stretch_len=0.5)
        self.turtle.color(self.color)
        self.turtle.goto(self.x, self.y)
        self.turtle.showturtle()

    def hide_bullet(self):
        """
        Hide the bullet's turtle representation from the screen.
        """
        self.turtle.hideturtle()

    def is_off_screen(self):
        """
        Check if the bullet has moved outside the boundaries of the screen.

        Returns:
            bool: True if the bullet is off screen, otherwise False.
        """
        return not (-SCREEN_WIDTH / 2 < self.x < SCREEN_WIDTH / 2 and -SCREEN_HEIGHT / 2 < self.y < SCREEN_HEIGHT / 2)

    def move(self):
        """
        Move the bullet according to its velocity, and update its on-screen position.
        """
        self.x += self.vx
        self.y += self.vy
        self.turtle.goto(self.x, self.y)

    def draw(self):
        """
        Draw the bullet on the screen. Since we are using shapes, this is handled by turtle.
        """
        pass

    def __str__(self):
        """
        Return a string representation of the bullet's state.

        Returns:
            str: A string detailing the bullet's position and velocity.
        """
        return f"Bullet at ({self.x}, {self.y}) with velocity ({self.vx}, {self.vy})"