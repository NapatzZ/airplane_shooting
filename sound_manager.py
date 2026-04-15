import pygame
import os
import time
from const import *

class SoundManager:
    """
    Manage all the sound effects for the game.
    """
    _initialized = False
    START_SOUND = None
    POWERUP_SOUND = None
    EXPLOSION_SOUND = None
    SHOOTING_SOUND = None

    @classmethod
    def init(cls):
        """Initialize the mixer and load sounds safely."""
        if cls._initialized:
            return
        
        try:
            # Better defaults for macOS/Linux compatibility
            pygame.mixer.pre_init(44100, -16, 2, 2048)
            pygame.mixer.init()
            
            # Load sounds
            cls.START_SOUND = pygame.mixer.Sound(START)
            cls.POWERUP_SOUND = pygame.mixer.Sound(POWERUP)
            cls.EXPLOSION_SOUND = pygame.mixer.Sound(EXPLOSION)
            cls.SHOOTING_SOUND = pygame.mixer.Sound(SHOOT)
            
            # Set volumes (0.0 to 1.0)
            cls.START_SOUND.set_volume(0.5)
            cls.SHOOTING_SOUND.set_volume(0.3)
            
            cls._initialized = True
            print("Sound system initialized.")
        except (pygame.error, FileNotFoundError) as e:
            print(f"Warning: Audio system failed to initialize. Error: {e}")
            cls._initialized = False

    @staticmethod
    def play_start_sound():
        """Play the start sound effect."""
        if SoundManager._initialized and SoundManager.START_SOUND:
            SoundManager.START_SOUND.play()

    @staticmethod
    def play_powerup_sound():
        """Play the power-up sound effect."""
        if SoundManager._initialized and SoundManager.POWERUP_SOUND:
            SoundManager.POWERUP_SOUND.play()

    @staticmethod
    def play_explosion_sound():
        """Play the explosion sound effect."""
        if SoundManager._initialized and SoundManager.EXPLOSION_SOUND:
            SoundManager.EXPLOSION_SOUND.play()

    @staticmethod
    def play_shooting_sound():
        """Play the shooting sound effect."""
        if SoundManager._initialized and SoundManager.SHOOTING_SOUND:
            SoundManager.SHOOTING_SOUND.play()

# Initialize sound at module level safely
SoundManager.init()
