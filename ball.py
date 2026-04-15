import turtle
import math
from const import *

class Ball:
    """
    A Ball object represents a moving circular particle with methods for collision detection
    and response against other balls, walls, and paddles. It uses turtle graphics for its
    on-screen representation.
    """

    def __init__(self, size, x, y, vx, vy, color):
        """
        Initialize a Ball with the given parameters.

        Args:
            size (int): The radius of the ball.
            x (float): The initial x-coordinate of the ball's center.
            y (float): The initial y-coordinate of the ball's center.
            vx (float): The initial horizontal velocity of the ball.
            vy (float): The initial vertical velocity of the ball.
            color (str): The color of the ball (currently unused if the ball uses a shape).
        """
        self.size = size
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.mass = 100 * size ** 2
        self.count = 0
        self.canvas_width = turtle.screensize()[0]
        self.canvas_height = turtle.screensize()[1]
        self.turtle = turtle.Turtle()
        self.turtle.penup()

    def bounce_off_vertical_wall(self):
        """
        Reverse the horizontal velocity of the ball to simulate a bounce off a vertical wall.
        Increments the collision count of the ball.
        """
        self.vx = -self.vx
        self.count += 1

    def bounce_off_horizontal_wall(self):
        """
        Reverse the vertical velocity of the ball to simulate a bounce off a horizontal wall.
        Increments the collision count of the ball.
        """
        self.vy = -self.vy
        self.count += 1

    def bounce_off(self, that):
        """
        Update the velocities of this ball and another ball (`that`) to simulate an elastic
        collision between two balls.

        Args:
            that (Ball): Another Ball instance with which this ball collides.
        """
        dx = that.x - self.x
        dy = that.y - self.y
        dvx = that.vx - self.vx
        dvy = that.vy - self.vy
        dvdr = dx * dvx + dy * dvy
        dist = self.size + that.size

        magnitude = 2 * self.mass * that.mass * dvdr / ((self.mass + that.mass) * dist)

        fx = magnitude * dx / dist
        fy = magnitude * dy / dist

        self.vx += fx / self.mass
        self.vy += fy / self.mass
        that.vx -= fx / that.mass
        that.vy -= fy / that.mass

        self.count += 1
        that.count += 1

    def distance(self, that):
        """
        Compute the Euclidean distance between the centers of this ball and another ball.

        Args:
            that (Ball): Another Ball instance.

        Returns:
            float: The distance between the centers of the two balls.
        """
        return math.sqrt((that.y - self.y) ** 2 + (that.x - self.x) ** 2)

    def time_to_hit(self, that):
        """
        Calculate the time until this ball collides with another ball, if ever.

        Args:
            that (Ball): Another Ball instance.

        Returns:
            float: The time in seconds until collision, or math.inf if no collision occurs.
        """
        if self is that:
            return math.inf
        dx = that.x - self.x
        dy = that.y - self.y
        dvx = that.vx - self.vx
        dvy = that.vy - self.vy
        dvdr = dx * dvx + dy * dvy
        if dvdr > 0:
            return math.inf
        dvdv = dvx ** 2 + dvy ** 2
        if dvdv == 0:
            return math.inf
        drdr = dx ** 2 + dy ** 2
        sigma = self.size + that.size
        d = (dvdr ** 2) - dvdv * (drdr - sigma ** 2)
        if d < 0:
            return math.inf
        t = -(dvdr + math.sqrt(d)) / dvdv
        return t if t > 0 else math.inf

    def time_to_hit_vertical_wall(self):
        """
        Calculate the time until this ball hits a vertical wall, if ever.

        Returns:
            float: The time in seconds until the ball hits a vertical wall, or math.inf if it won't.
        """
        if self.vx > 0:
            return (self.canvas_width - self.x - self.size) / self.vx
        elif self.vx < 0:
            return (self.canvas_width + self.x - self.size) / (-self.vx)
        return math.inf

    def time_to_hit_horizontal_wall(self):
        """
        Calculate the time until this ball hits a horizontal wall, if ever.

        Returns:
            float: The time in seconds until the ball hits a horizontal wall, or math.inf if it won't.
        """
        if self.vy > 0:
            return (self.canvas_height - self.y - self.size) / self.vy
        elif self.vy < 0:
            return (self.canvas_height + self.y - self.size) / (-self.vy)
        return math.inf

    def time_to_hit_paddle(self, paddle):
        """
        Calculate the time until this ball hits a paddle, if ever.

        Args:
            paddle: A paddle object that has location, width, and height attributes.

        Returns:
            float: The time in seconds until the ball hits the paddle, or math.inf if it won't.
        """
        if (self.vy > 0) and ((self.y + self.size) > (paddle.location[1] - paddle.height / 2)):
            return math.inf
        if (self.vy < 0) and ((self.y - self.size) < (paddle.location[1] + paddle.height / 2)):
            return math.inf

        dt = (math.sqrt((paddle.location[1] - self.y) ** 2) - self.size - paddle.height / 2) / abs(self.vy)
        paddle_left_edge = paddle.location[0] - paddle.width / 2
        paddle_right_edge = paddle.location[0] + paddle.width / 2
        if paddle_left_edge - self.size <= self.x + (self.vx * dt) <= paddle_right_edge + self.size:
            return dt
        return math.inf

    def bounce_off_paddle(self):
        """
        Simulate a vertical bounce by reversing the vertical velocity when hitting a paddle.
        Increments the collision count of the ball.
        """
        self.vy = -self.vy
        self.count += 1

    def __str__(self):
        """
        Return a string representation of the ball's current state.

        Returns:
            str: A string containing the ball's x, y, vx, vy, and collision count.
        """
        return f"{self.x}:{self.y}:{self.vx}:{self.vy}:{self.count}"