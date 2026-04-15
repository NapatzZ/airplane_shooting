import turtle
import tkinter as tk
import random
import csv
import os
from const import *
from airplane import PlayerAirplane, EnemyAirplane
from mystery import MysteryBall
from bullet import Bullet
from sound_manager import * 

class GameController:
    """
    Control the Airplane Shooting Game.

    This class handles the game lifecycle: showing the login screen, starting the game,
    updating objects, handling collisions, ending the game, saving scores, and displaying
    a scoreboard.
    """

    def __init__(self):
        """Initialize the game controller and set up the initial login screen."""
        # Initial Setup
        self.screen = turtle.Screen()
        self.screen.setup(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
        self.screen.title("Airplane Shooting Game")
        self.screen.bgcolor(BLACK)
        self.screen.tracer(0)
        self.canvas = self.screen.getcanvas()

        # Register image shapes
        self.screen.register_shape(HEART_FULL)
        self.screen.register_shape(HEART_BROKE)
        self.screen.register_shape(AIRPLANE_LOGO)
        self.screen.register_shape(PLAYER_PIC)

        # Turtle for login/logo
        self.logo_turtle = turtle.Turtle()
        self.logo_turtle.hideturtle()
        self.logo_turtle.penup()
        self.logo_turtle.shape(AIRPLANE_LOGO)
        self.logo_turtle.goto(0, 100)
        self.logo_turtle.showturtle()

        # Turtle for welcome message
        self.welcome_turtle = turtle.Turtle()
        self.welcome_turtle.hideturtle()
        self.welcome_turtle.penup()
        self.welcome_turtle.color(WHITE)
        self.welcome_turtle.goto(0, -50)
        self.welcome_turtle.write(
            "Welcome to Airplane Shooting Game!",
            align="center",
            font=("Arial", 24, "bold")
        )

        # Turtle for username instruction
        self.instruction_turtle = turtle.Turtle()
        self.instruction_turtle.hideturtle()
        self.instruction_turtle.penup()
        self.instruction_turtle.color(WHITE)
        self.instruction_turtle.goto(0, -150)
        self.instruction_turtle.write(
            "Please enter your username:",
            align="center",
            font=("Arial", 16, "normal")
        )

        # Turtle for game over message
        self.game_over_turtle = turtle.Turtle()
        self.game_over_turtle.hideturtle()
        self.game_over_turtle.penup()

        # Turtle for scoreboard display
        self.scoreboard_turtle = turtle.Turtle()
        self.scoreboard_turtle.hideturtle()
        self.scoreboard_turtle.penup()
        self.scoreboard_turtle.color(WHITE)

        # Turtle for displaying score and hearts
        self.display_turtle = turtle.Turtle()
        self.display_turtle.hideturtle()
        self.display_turtle.penup()

        # Attributes for game state
        self.score_text = None
        self.player = None
        self.username = ""
        self.current_input = ""
        self.bg_images = []
        self.bg_ids = []
        self.mystery_balls = []
        self.enemies = []
        self.last_score_used_to_spawn = -1
        self.game_started = False
        self.difficulty_multiplier = 1.0

        self.login_screen()

    def login_screen(self):
        """
        Set up the login screen with changing background colors and a rotating/flipping logo.
        Binds keys for username input and starting the game.
        """
        SoundManager.play_start_sound()  # Play start sound on login screen
        self.change_background_color()
        self.rotate_logo()
        self.flip_logo()

        # Bind keys for username input
        self.screen.listen()
        self.screen.onkeypress(self.start_game, "Return")
        self.screen.onkeypress(self.backspace, "BackSpace")
        for char in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789":
            self.screen.onkeypress(lambda c=char: self.add_char(c), char)

    def add_char(self, char):
        """
        Add a character to the current username input and update the display.

        Args:
            char (str): The character to add.
        """
        if not self.game_started:
            self.current_input += char
            self.update_username_display()

    def backspace(self):
        """Remove the last character from the current username input and update the display."""
        if not self.game_started and len(self.current_input) > 0:
            self.current_input = self.current_input[:-1]
            self.update_username_display()

    def update_username_display(self):
        """Update the on-screen username input display."""
        self.instruction_turtle.clear()
        self.instruction_turtle.write(
            f"Please enter your username: {self.current_input}",
            align="center",
            font=("Arial", 16, "normal")
        )

    def start_game(self):
        """Start the main game once the username is confirmed."""
        if self.game_started:
            return

        self.game_started = True
        self.username = self.current_input if self.current_input else "Player"

        # Clear login screen elements
        self.logo_turtle.hideturtle()
        self.welcome_turtle.clear()
        self.instruction_turtle.clear()

        # Set main game background
        self.screen.bgcolor(SKYBLUE)

        self.spawn_background()
        self.initialize_game_objects()
        self.bind_keys()
        self.game_loop()

    def change_background_color(self):
        """Periodically change the background color on the login screen."""
        if self.game_started:
            return
        new_color = random.choice(LOGIN_BG_COLORS)
        self.screen.bgcolor(new_color)
        self.screen.ontimer(self.change_background_color, 1000)  # Change every second

    def rotate_logo(self, angle=0):
        """
        Rotate the logo continuously on the login screen.

        Args:
            angle (int): The current angle of rotation.
        """
        if self.game_started:
            return
        self.logo_turtle.setheading(angle)
        self.screen.update()
        self.screen.ontimer(lambda: self.rotate_logo((angle + LOGO_ROTATION_SPEED) % 360), 50)

    def flip_logo(self):
        """Flip the logo periodically on the login screen."""
        if self.game_started:
            return
        current_heading = self.logo_turtle.heading()
        new_heading = (current_heading + 180) % 360
        self.logo_turtle.setheading(new_heading)
        self.screen.update()
        self.screen.ontimer(self.flip_logo, LOGO_FLIP_INTERVAL)

    def spawn_background(self):
        """Load and place background images that scroll continuously."""
        for path in BG_IMAGE_PATHS:
            try:
                img = tk.PhotoImage(file=path)
                self.bg_images.append(img)
            except tk.TclError:
                print(f"Error loading background image: {path}")

        if not self.bg_images:
            print("No background images loaded.")
            return

        bg_width = self.bg_images[0].width()
        bg_height = self.bg_images[0].height()
        x_position = (SCREEN_WIDTH - bg_width) // 2 - 300

        for i, img in enumerate(self.bg_images):
            bg_id = self.canvas.create_image(
                x_position, i * bg_height, anchor='nw', image=img
            )
            self.bg_ids.append(bg_id)

        self.scroll_background()

    def scroll_background(self):
        """Scroll the background images downwards."""
        for bg_id in self.bg_ids:
            self.canvas.move(bg_id, 0, SCROLL_SPEED)
            x, y = self.canvas.coords(bg_id)
            if y >= SCREEN_HEIGHT:
                max_y = min([self.canvas.coords(b)[1] for b in self.bg_ids])
                self.canvas.coords(bg_id, x, max_y - self.bg_images[0].height())
        self.screen.update()
        self.screen.ontimer(self.scroll_background, int(1000 / FPS))

    def initialize_game_objects(self):
        """Initialize player and other game objects."""
        self.player = PlayerAirplane(
            position=(0, -200),
            velocity=(0, 0),
            shape=PLAYER_PIC,
            health=3,
            size=40
        )

    def bind_keys(self):
        """Bind the control keys for player movement and actions."""
        self.screen.onkeypress(self.player.press_up, "Up")
        self.screen.onkeyrelease(self.player.release_up, "Up")
        self.screen.onkeypress(self.player.press_left, "Left")
        self.screen.onkeyrelease(self.player.release_left, "Left")
        self.screen.onkeypress(self.player.press_right, "Right")
        self.screen.onkeyrelease(self.player.release_right, "Right")
        self.screen.onkeypress(self.player.press_down, "Down")
        self.screen.onkeyrelease(self.player.release_down, "Down")
        self.screen.onkeypress(self.player.press_space, "space")
        self.screen.onkeyrelease(self.player.release_space, "space")
        self.screen.listen()

    def display_score(self):
        """Display the player's current score and level."""
        if self.score_text:
            self.score_text.clear()
        else:
            self.score_text = turtle.Turtle()
            self.score_text.hideturtle()
            self.score_text.penup()
            self.score_text.color(WHITE)
        self.score_text.goto(0, SCREEN_HEIGHT / 2 - 50)
        level = int((self.difficulty_multiplier - 1) * 10) + 1
        self.score_text.write(
            f"{self.username} Score: {self.player.score} | Level: {level}",
            align="center",
            font=("Arial", 20, "normal")
        )

    def health_ui(self):
        """Display the player's health as hearts."""
        self.display_turtle.clear()
        health = max(0, min(self.player._health, 3))
        hearts = [HEART_FULL] * health + [HEART_BROKE] * (3 - health)
        for i, heart in enumerate(hearts):
            self.display_image(-200 + i * 40, -300, heart)

    def display_image(self, x, y, image_shape):
        """
        Stamp an image at a specific coordinate.

        Args:
            x (float): The x-coordinate.
            y (float): The y-coordinate.
            image_shape (str): The turtle shape to stamp.
        """
        self.display_turtle.goto(x, y)
        self.display_turtle.shape(image_shape)
        self.display_turtle.stamp()

    def spawn_mystery_ball(self):
        """Spawn a mystery ball with a random type at a random position."""
        mystery_types = [1, 2, 3]
        mystery_type = random.choice(mystery_types)
        mystery_ball = MysteryBall(
            size=20,
            x=random.randint(-SCREEN_WIDTH // 2 + 50, SCREEN_WIDTH // 2 - 50),
            y=SCREEN_HEIGHT // 2 - 50,
            vx=0,
            vy=-5,
            color="red",
            ball_type=mystery_type
        )
        self.mystery_balls.append(mystery_ball)

    def spawn_enemy(self):
        """Spawn an enemy airplane at a random position without overlapping existing enemies."""
        shapes = [AIRPLANE_2, AIRPLANE_3, AIRPLANE_4, AIRPLANE_5]
        random_shape = random.choice(shapes)
        
        # Safer spawning logic
        max_attempts = 10
        for _ in range(max_attempts):
            x_pos = random.randint(-SCREEN_WIDTH // 2 + 50, SCREEN_WIDTH // 2 - 50)
            y_pos = SCREEN_HEIGHT // 2 - 50
            overlap = False
            for enemy in self.enemies:
                if abs(x_pos - enemy.x) < enemy.size * 2 and abs(y_pos - enemy.y) < enemy.size * 2:
                    overlap = True
                    break
            if not overlap:
                new_enemy = EnemyAirplane(
                    position=(x_pos, y_pos),
                    velocity=(0, 0),
                    shape=random_shape,
                    health=3,
                    size=40
                )
                # Apply difficulty scaling to enemy speed
                new_enemy.patrol_speed *= self.difficulty_multiplier
                new_enemy.attack_speed *= self.difficulty_multiplier
                self.enemies.append(new_enemy)
                break

    def display_game_over(self):
        """
        Display the Game Over screen, prompt for restart, save the score to CSV, and show the scoreboard.
        """
        self.screen.bgcolor(GAME_OVER_BG_COLOR)
        self.game_over_turtle.goto(0, 0)
        self.game_over_turtle.color(GAME_OVER_COLOR)
        self.game_over_turtle.write(
            GAME_OVER_TEXT,
            align="center",
            font=GAME_OVER_FONT
        )
        self.health_ui()  # Show hearts
        self.save_score_to_csv()
        self.show_scoreboard()

        # Restart prompt
        self.game_over_turtle.goto(0, -50)
        self.game_over_turtle.write(
            "Press 'R' to Restart",
            align="center",
            font=("Arial", 16, "normal")
        )
        self.screen.onkeypress(self.restart_game, "r")
        self.screen.listen()

    def save_score_to_csv(self):
        """Save the player's username and score to a CSV file."""
        filename = "scores.csv"
        file_exists = os.path.isfile(filename)

        with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            # Write header if file does not exist
            if not file_exists:
                writer.writerow(["username", "score"])
            writer.writerow([self.username, self.player.score])

    def show_scoreboard(self):
        """
        Show the top scores from the CSV file on screen after the game is over.
        The scoreboard is shown below the Game Over message.
        """
        filename = "scores.csv"
        if not os.path.isfile(filename):
            return

        scores = []
        with open(filename, mode='r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    score = int(row["score"])
                    scores.append((row["username"], score))
                except ValueError:
                    continue

        # Sort scores in descending order by score
        scores.sort(key=lambda x: x[1], reverse=True)

        self.scoreboard_turtle.clear()
        self.scoreboard_turtle.goto(0, -150)
        self.scoreboard_turtle.write(
            "Scoreboard",
            align="center",
            font=("Arial", 20, "bold")
        )

        # Show top 5 scores
        y_offset = -180
        for i, (user, score) in enumerate(scores[:5], start=1):
            self.scoreboard_turtle.goto(0, y_offset)
            self.scoreboard_turtle.write(
                f"{i}. {user}: {score}",
                align="center",
                font=("Arial", 16, "normal")
            )
            y_offset -= 30

    def restart_game(self):
        """
        Restart the game from the beginning.
        This method re-initializes the GameController and starts fresh.
        """
        self.screen.clear()
        self.__init__()

    def game_loop(self):
        """
        Main game loop: update the player, enemies, mystery balls,
        check for game over, and schedule the next frame.
        """
        self.player.update(self.enemies)
        self.health_ui()
        self.display_score()

        if self.player._health <= 0:
            self.display_game_over()
            self.screen.update()
            return

        # Increase difficulty based on score
        self.difficulty_multiplier = 1.0 + (self.player.score // 10) * 0.1

        for ball in self.mystery_balls[:]:
            ball.move()
            if self.player.distance(ball) < self.player.size + ball.size:
                ball.activate_ability(self.player)
                self.mystery_balls.remove(ball)
            elif ball.is_off_screen():
                ball._hide_ball()
                self.mystery_balls.remove(ball)

        for enemy in self.enemies[:]:
            enemy.update(self.player)
            if enemy._is_destroyed:
                self.enemies.remove(enemy)
                self.player.score += 1

        if not self.enemies:
            num_enemies = random.randint(1, min(4 + int(self.player.score // 20), 8))
            for _ in range(num_enemies):
                self.spawn_enemy()

        if self.player.score % 7 == 0 and self.player.score != self.last_score_used_to_spawn:
            self.spawn_mystery_ball()
            self.last_score_used_to_spawn = self.player.score

        self.screen.update()
        self.screen.ontimer(self.game_loop, int(1000 / FPS))


if __name__ == "__main__":
    game = GameController()
    turtle.tracer(0)
    turtle.mainloop()