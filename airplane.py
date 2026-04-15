import turtle
from const import *
from bullet import Bullet
import time
import math
import pygame
from sound_manager import * 

STATE_PATROL = "Patrol"
STATE_ATTACK = "Attack"

class Airplane:
    """
    A base class for all airplanes in the game, including the player and enemies.
    
    Airplanes have a position, velocity, health, and can shoot bullets. They also have
    an associated turtle object for graphical representation and can be destroyed upon
    taking sufficient damage.
    """

    def __init__(self, position, velocity, shape, health, size=40):
        """
        Initialize the airplane with given parameters.
        
        Args:
            position (tuple): The (x, y) coordinates of the airplane.
            velocity (tuple): The (vx, vy) velocity vector of the airplane.
            shape (str): The turtle shape representing the airplane.
            health (int): The health points of the airplane.
            size (int): The radius or half-diameter size of the airplane.
        """
        self.size = size
        self._shape = shape
        self._position = position
        self._velocity = velocity
        self._health = health

        self._turtle = turtle.Turtle()
        self._turtle.penup()
        self._turtle.screen.register_shape(shape)
        self._turtle.shape(shape)
        self._turtle.goto(self._position)
        self._turtle.showturtle()

        self._bullets = []
        self._explosion_images = EXPLOSION_FRAMES
        self._explosion_frame = 0
        self._is_destroyed = False

        self._explosion_turtle = turtle.Turtle()
        self._explosion_turtle.hideturtle()

    @property
    def position(self):
        """
        tuple: The current (x, y) position of the airplane.
        """
        return self._position

    @position.setter
    def position(self, position):
        """
        Set a new position for the airplane and move the turtle accordingly.
        
        Args:
            position (tuple): The new (x, y) position of the airplane.
        """
        self._position = position
        self._turtle.goto(self._position)

    @property
    def x(self):
        """
        float: The x-coordinate of the airplane's position.
        """
        return self._position[0]

    @property
    def y(self):
        """
        float: The y-coordinate of the airplane's position.
        """
        return self._position[1]

    @property
    def shape(self):
        """
        str: The current shape of the airplane.
        """
        return self._shape

    @shape.setter
    def shape(self, other):
        """
        Set a new shape for the airplane and update its turtle representation.
        
        Args:
            other (str): The new shape name.
        """
        self._turtle.screen.register_shape(other)
        self._turtle.shape(other)

    def move(self):
        """
        Move the airplane according to its velocity vector.
        """
        new_x = self._position[0] + self._velocity[0]
        new_y = self._position[1] + self._velocity[1]
        self._position = (new_x, new_y)
        self._turtle.goto(self._position)

    def take_damage(self, amount):
        """
        Reduce the airplane's health by a given amount and destroy it if health reaches zero or below.
        
        Args:
            amount (int): The amount of damage to inflict.
        """
        if self._is_destroyed:
            return
        self._health = max(0, self._health - amount)
        if self._health <= 0:
            self.destroy()

    def destroy(self):
        """Destroy the airplane by hiding it and playing an explosion animation."""
        SoundManager.play_explosion_sound()  # Play explosion sound
        self._is_destroyed = True
        self._health = 0
        self._turtle.hideturtle()
        self._turtle.clear()
        self.remove_bullets()
        self._handle_explosion_step()
        self._turtle.screen.update()
        self._explosion_turtle.clear()

    def _handle_explosion_step(self):
        """
        Handle a single step of the explosion animation. Calls itself via a timer until all frames have been displayed.
        """
        self._explosion_turtle.penup()
        self._turtle.clear()

        if self._explosion_frame < len(self._explosion_images):
            self._explosion_turtle.screen.register_shape(self._explosion_images[self._explosion_frame])
            self._explosion_turtle.shape(self._explosion_images[self._explosion_frame])
            self._explosion_turtle.goto(self._position)
            self._explosion_turtle.showturtle()
            self._explosion_frame += 1
            self._explosion_turtle.screen.ontimer(self._handle_explosion_step, EXPLOSION_DELAY)
        else:
            self._explosion_turtle.hideturtle()
            self._turtle.hideturtle()

    def add_bullet(self, bullet):
        """
        Add a bullet to the airplane's bullet list.
        
        Args:
            bullet (Bullet): The bullet object to add.
        """
        self._bullets.append(bullet)

    def update_bullets(self, target):
        """
        Move and handle collisions for the airplane's bullets.
        
        Args:
            target: The target object to check for bullet collisions.
        """
        for bullet in self._bullets[:]:
            bullet.move()
            if self._check_bullet_collision(bullet, target):
                bullet.hide_bullet()
                self._bullets.remove(bullet)
                target.take_damage(1)
            elif bullet.is_off_screen():
                bullet.hide_bullet()
                self._bullets.remove(bullet)

    def _check_bullet_collision(self, bullet, target):
        """
        Check if a bullet collides with a target.

        Args:
            bullet (Bullet): The bullet object.
            target: The target object (usually a PlayerAirplane or EnemyAirplane).
        
        Returns:
            bool: True if the bullet collided with the target, False otherwise.
        """
        return bullet.distance(target) < target.size + bullet.size

    def draw_bullets(self):
        """
        Make all bullets visible.
        """
        for bullet in self._bullets:
            bullet.turtle.showturtle()

    def remove_bullets(self):
        """
        Remove all bullets from the airplane, hiding them first.
        """
        for bullet in self._bullets:
            bullet.hide_bullet()
        self._bullets.clear()


class PlayerAirplane(Airplane):
    """
    The player's airplane class, which can be controlled by keyboard input, shoot bullets,
    and receive special abilities from mystery balls.
    """

    def __init__(self, position, velocity, shape, health, size=20):
        """
        Initialize the player's airplane.
        
        Args:
            position (tuple): Initial (x, y) position.
            velocity (tuple): Initial (vx, vy) velocity vector.
            shape (str): The turtle shape to represent the player airplane.
            health (int): The initial health of the player.
            size (int): The radius/size of the player's airplane.
        """
        super().__init__(position, velocity, shape, health, size)
        self._is_up_pressed = False
        self._is_left_pressed = False
        self._is_right_pressed = False
        self._is_down_pressed = False
        self._is_space_pressed = False

        self.is_tridirectional = False
        self.bullet_size = size
        self.speed_multiplier = 1
        self.last_shot_time = 0
        self.shot_cooldown = 0.3
        self.score = 0
        self.ability_activation_time = 0

    def press_up(self):
        """Set the flag indicating the up arrow key is pressed."""
        self._is_up_pressed = True

    def release_up(self):
        """Unset the flag indicating the up arrow key is pressed."""
        self._is_up_pressed = False

    def press_down(self):
        """Set the flag indicating the down arrow key is pressed."""
        self._is_down_pressed = True

    def release_down(self):
        """Unset the flag indicating the down arrow key is pressed."""
        self._is_down_pressed = False

    def press_left(self):
        """Set the flag indicating the left arrow key is pressed."""
        self._is_left_pressed = True

    def release_left(self):
        """Unset the flag indicating the left arrow key is pressed."""
        self._is_left_pressed = False

    def press_right(self):
        """Set the flag indicating the right arrow key is pressed."""
        self._is_right_pressed = True

    def release_right(self):
        """Unset the flag indicating the right arrow key is pressed."""
        self._is_right_pressed = False

    def press_space(self):
        """Set the flag indicating the space key is pressed and initiate a shoot action with shooting sound."""
        self._is_space_pressed = True
        self.shoot()
        SoundManager.play_shooting_sound()


    def release_space(self):
        """Unset the flag indicating the space key is pressed."""
        self._is_space_pressed = False

    def distance(self, other):
        """
        Calculate the distance between the player and another object.
        
        Args:
            other: Another object with x and y properties.
        
        Returns:
            float: The Euclidean distance between the player and the other object.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def activate_tridirectional_shooting(self):
        """
        Activate tri-directional shooting mode, allowing the player to shoot three bullets at once.
        """
        self.is_tridirectional = True
        self.ability_activation_time = time.time()

    def increase_health(self):
        """
        Increase the player's health by 1, capped at a maximum of 3.
        """
        self._health = min(3, self._health + 1)

    def double_speed(self):
        """
        Double the player's speed for a temporary period.
        """
        self.speed_multiplier = 1.8
        self.ability_activation_time = time.time()

    def deactivate_ability(self):
        """
        Deactivate any active special abilities, returning to normal state.
        """
        self.is_tridirectional = False
        self.speed_multiplier = 1.0

    def move_airplane_directional(self):
        """
        Move the player's airplane based on which directional keys are pressed,
        taking into account the current speed multiplier.
        """
        dx, dy = 0, 0

        if self._is_up_pressed:
            dy += PLAYER_SPEED * self.speed_multiplier + 0.5
        if self._is_down_pressed:
            dy -= PLAYER_SPEED * self.speed_multiplier + 0.5
        if self._is_left_pressed:
            dx -= PLAYER_SPEED * self.speed_multiplier
        if self._is_right_pressed:
            dx += PLAYER_SPEED * self.speed_multiplier

        new_x = self.x + dx
        new_y = self.y + dy

        # Boundary check
        if -SCREEN_WIDTH / 2 + self.size < new_x < SCREEN_WIDTH / 2 - self.size and \
           -SCREEN_HEIGHT / 2 + self.size < new_y < SCREEN_HEIGHT / 2 - self.size:
            self.position = (new_x, new_y)

        turtle.update()

    def update(self, enemies):
        """
        Update the player's state, handle abilities timeout, movement, and bullet collisions.
        
        Args:
            enemies (list): A list of enemy airplanes.
        """
        current_time = time.time()

        # Deactivate abilities if their lifetime has passed
        if self.is_tridirectional and (current_time - self.ability_activation_time) > MYSTERY_BALL_LIFETIME:
            self.deactivate_ability()

        self.move_airplane_directional()
        self.update_bullets(enemies)

    def update_bullets(self, enemies):
        """
        Move player's bullets and check for collisions with enemies.
        
        Args:
            enemies (list): A list of enemy airplanes.
        """
        for bullet in self._bullets[:]:
            bullet.move()
            for enemy in enemies:
                if self._check_bullet_collision(bullet, enemy):
                    self.handle_bullet_collision(bullet, enemy)
                    break

            if bullet.is_off_screen():
                bullet.hide_bullet()
                self._bullets.remove(bullet)

    def handle_bullet_collision(self, bullet, target):
        """
        Handle the event where a player bullet collides with an enemy target.
        
        Args:
            bullet (Bullet): The bullet that collided.
            target (Airplane): The enemy airplane that was hit.
        """
        target.take_damage(10)
        bullet.hide_bullet()
        self._bullets.remove(bullet)

    def shoot(self):
        """
        Shoot bullets based on the current shooting mode (normal or tri-directional),
        respecting the cooldown time.
        """
        current_time = time.time()
        cooldown = 0.5 if self.is_tridirectional else self.shot_cooldown

        if current_time - self.last_shot_time > cooldown:
            self.last_shot_time = current_time

            if self.is_tridirectional:
                angles = [120, 90, 60]
                for angle in angles:
                    dx = math.cos(math.radians(angle)) * 5
                    dy = math.sin(math.radians(angle)) * 5
                    bullet = Bullet(
                        x=self.x,
                        y=self.y + self.bullet_size + 5,
                        vx=dx,
                        vy=dy,
                        owner=PLAYER
                    )
                    self.add_bullet(bullet)
            else:
                bullet = Bullet(
                    x=self.x,
                    y=self.y + self.size + 5,
                    vx=0,
                    vy=BULLET_SPEED,
                    owner=PLAYER
                )
                self.add_bullet(bullet)


class EnemyAirplane(Airplane):
    """
    An enemy airplane that patrols and attacks the player.
    
    The enemy can switch states between Patrol and Attack depending on player distance and position.
    It moves downwards, can shoot bullets, and is destroyed upon taking enough damage or reaching the bottom.
    """

    def __init__(self, position, velocity, shape, health, size=20):
        """
        Initialize the enemy airplane with patrol and attack parameters.
        
        Args:
            position (tuple): Initial (x, y) position.
            velocity (tuple): Initial (vx, vy) velocity vector.
            shape (str): The turtle shape for the enemy airplane.
            health (int): The health points of the enemy.
            size (int): The radius/size of the enemy airplane.
        """
        super().__init__(position, velocity, shape, health, size)
        self.last_shot_time = 0
        self.shot_cooldown = 1.0
        self.max_bullets = 5
        self.bullet_count = 0

        # Increase attack distance by 1.5 times (200 -> 300)
        self.attack_distance = 300
        # Attack speed when in Attack state
        self.attack_speed = 8

        self.state = STATE_PATROL
        self.patrol_left_bound = -100
        self.patrol_right_bound = 100
        self.patrol_speed = 2
        self.moving_right = True

    def handle_state_machine(self, target):
        """
        Determine the current state (Patrol or Attack) of the enemy based on the target's position.
        
        Args:
            target (Airplane): The target airplane (usually the player).
        """
        if self._is_destroyed:
            return

        dist = self.distance(target)
        # Check if enemy is above the player
        if self.y > target.y:
            # If close enough, switch to Attack state
            if dist < self.attack_distance:
                self.state = STATE_ATTACK
            else:
                self.state = STATE_PATROL
        else:
            # If not above the player, remain in Patrol state
            self.state = STATE_PATROL

    def distance(self, other):
        """
        Calculate the distance between this enemy and another object.
        
        Args:
            other: Another object with x and y properties.
        
        Returns:
            float: The Euclidean distance between the enemy and the other object.
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx**2 + dy**2)

    def move_patrol(self):
        """
        Move the enemy horizontally between patrol bounds and downward at the patrol speed.
        """
        if self.moving_right:
            new_x = self.x + self.patrol_speed
            if new_x > self.patrol_right_bound:
                new_x = self.patrol_right_bound
                self.moving_right = False
        else:
            new_x = self.x - self.patrol_speed
            if new_x < self.patrol_left_bound:
                new_x = self.patrol_left_bound
                self.moving_right = True

        new_y = self.y - ENEMY_SPEED
        self.position = (new_x, new_y)

    def move_attack(self, target):
        """
        Move the enemy straight downward at a faster speed when in Attack state.
        
        Args:
            target (Airplane): The target airplane.
        """
        new_x = self.x
        new_y = self.y - self.attack_speed
        self.position = (new_x, new_y)

    def handle_shooting(self, target):
        """
        Handle enemy shooting behavior depending on its current state.
        
        Args:
            target (Airplane): The target airplane.
        """
        if self._is_destroyed:
            return

        # In Attack state, shoot faster and bullets move faster
        if self.state == STATE_ATTACK:
            attack_cooldown = max(0.5, self.shot_cooldown / 2.0)
            self.shoot_based_on_shape(target, attack_cooldown, enhanced_vy_multiplier=1.8)
        else:
            # Normal shooting outside of Attack state
            self.shoot_based_on_shape(target, self.shot_cooldown, enhanced_vy_multiplier=1.0)

    def shoot_based_on_shape(self, target, cooldown, enhanced_vy_multiplier=1.0):
        """
        Shoot bullets in patterns depending on the enemy's shape.
        
        Args:
            target (Airplane): The target airplane.
            cooldown (float): The time between allowed shots.
            enhanced_vy_multiplier (float): Multiplier for bullet vertical speed.
        """
        current_time = time.time()
        if self.shape == AIRPLANE_2:
            self.shoot_normal(current_time, cooldown, enhanced_vy_multiplier)
        elif self.shape == AIRPLANE_3:
            self.shoot_tri_directional(current_time, cooldown, enhanced_vy_multiplier)
        elif self.shape == AIRPLANE_4:
            self.shoot_with_limit(current_time, cooldown, enhanced_vy_multiplier)
        elif self.shape == AIRPLANE_5:
            self.shoot_fast(current_time, cooldown, enhanced_vy_multiplier)

    def shoot_normal(self, current_time, cooldown, enhanced_vy_multiplier):
        """
        Enemy shoots a single bullet straight down.
        
        Args:
            current_time (float): The current time for cooldown comparison.
            cooldown (float): Time interval between shots.
            enhanced_vy_multiplier (float): Vertical speed multiplier for bullets.
        """
        if current_time - self.last_shot_time > cooldown:
            self.last_shot_time = current_time
            bullet = Bullet(
                x=self.x,
                y=self.y - self.size - 5,
                vx=0,
                vy=-5 * enhanced_vy_multiplier,
                owner=ENEMY
            )
            self.add_bullet(bullet)

    def shoot_tri_directional(self, current_time, cooldown, enhanced_vy_multiplier):
        """
        Enemy shoots three bullets at slightly different angles downward.
        
        Args:
            current_time (float): The current time for cooldown comparison.
            cooldown (float): Time interval between shots.
            enhanced_vy_multiplier (float): Vertical speed multiplier for bullets.
        """
        if current_time - self.last_shot_time > cooldown:
            self.last_shot_time = current_time
            angles = [-100, -90, -80]
            for angle in angles:
                dx = math.cos(math.radians(angle)) * 5
                dy = math.sin(math.radians(angle)) * 5 * enhanced_vy_multiplier
                bullet = Bullet(
                    x=self.x,
                    y=self.y - self.size - 5,
                    vx=dx,
                    vy=dy,
                    owner=ENEMY
                )
                self.add_bullet(bullet)

    def shoot_with_limit(self, current_time, cooldown, enhanced_vy_multiplier):
        """
        Enemy shoots bullets but has a limit on how many bullets can be active at once.
        
        Args:
            current_time (float): The current time for cooldown comparison.
            cooldown (float): Time interval between shots.
            enhanced_vy_multiplier (float): Vertical speed multiplier for bullets.
        """
        if len(self._bullets) >= self.max_bullets:
            self._bullets[0].hide_bullet()
            self._bullets.pop(0)

        if current_time - self.last_shot_time > cooldown:
            self.last_shot_time = current_time
            bullet = Bullet(
                x=self.x,
                y=self.y - self.size - 5,
                vx=0,
                vy=-5 * enhanced_vy_multiplier,
                owner=ENEMY
            )
            self.add_bullet(bullet)

    def shoot_fast(self, current_time, cooldown, enhanced_vy_multiplier):
        """
        Enemy shoots bullets at the normal pattern but potentially with a shorter cooldown.
        
        Args:
            current_time (float): The current time for cooldown comparison.
            cooldown (float): Time interval between shots.
            enhanced_vy_multiplier (float): Vertical speed multiplier for bullets.
        """
        if current_time - self.last_shot_time > cooldown:
            self.last_shot_time = current_time
            bullet = Bullet(
                x=self.x,
                y=self.y - self.size - 5,
                vx=0,
                vy=-5 * enhanced_vy_multiplier,
                owner=ENEMY
            )
            self.add_bullet(bullet)

    def update(self, target):
        """
        Update the enemy airplane's state, movement, and bullets. Handle collisions with the player.
        
        Args:
            target (Airplane): The target airplane (usually the player).
        """
        if not self._is_destroyed:
            self.handle_state_machine(target)

            if self.state == STATE_PATROL:
                self.move_patrol()
            elif self.state == STATE_ATTACK:
                self.move_attack(target)

            # Check if the enemy has reached the bottom of the screen
            if self.y < -SCREEN_HEIGHT / 2 + self.size:
                # Reduce player health by 1 and destroy the enemy
                target.take_damage(1)
                self.destroy()

            self.update_bullets(target)
            self.handle_shooting(target)
        else:
            self.update_bullets(target)

    def update_bullets(self, target):
        """
        Move enemy bullets and handle collisions with the target (player).
        
        Args:
            target (Airplane): The target airplane (player).
        """
        for bullet in self._bullets[:]:
            bullet.move()
            if bullet.is_off_screen():
                bullet.hide_bullet()
                self._bullets.remove(bullet)
            elif self._check_bullet_collision(bullet, target):
                self.handle_bullet_collision(bullet, target)

    def handle_bullet_collision(self, bullet, target):
        """
        Handle bullet collision with the target (player), causing damage.
        
        Args:
            bullet (Bullet): The bullet that collided.
            target (Airplane): The target airplane that was hit.
        """
        target.take_damage(1)
        bullet.hide_bullet()
        self._bullets.remove(bullet)

    def remove_bullets(self):
        """
        Remove all bullets belonging to this enemy airplane.
        """
        for bullet in self._bullets:
            bullet.hide_bullet()
        self._bullets.clear()