import pygame
import time
import os
from const import *

def test_audio():
    print(f"Testing audio system...")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Checking for sound files...")
    
    sounds = [START, SHOOT, EXPLOSION, POWERUP]
    for s in sounds:
        exists = os.path.exists(s)
        print(f" - {s}: {'FOUND' if exists else 'MISSING'}")
        if not exists:
            return

    try:
        print("Initializing pygame mixer...")
        pygame.mixer.pre_init(44100, -16, 2, 2048)
        pygame.mixer.init()
        print(f"Mixer initialized. Driver: {pygame.mixer.get_init()}")
        
        print(f"Loading {START}...")
        sound = pygame.mixer.Sound(START)
        print("Playing sound for 2 seconds...")
        sound.play()
        time.sleep(2)
        print("Done.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_audio()
