# Airplane Shooting Game

A fun and interactive airplane shooting game built with Python's `turtle` and `pygame` modules.

## Features
- **Player Movement:** Use arrow keys to navigate your airplane.
- **Shooting:** Press `Space` to shoot bullets at incoming enemies.
- **Enemies:** Multiple types of enemy airplanes with unique patterns.
- **Power-ups:** Collect mystery balls for special abilities (Tri-directional shots, Health boost, Speed boost).
- **Scoreboard:** Tracks your score and displays the top 5 players.
- **Difficulty Scaling:** Game gets harder (faster enemies, more spawns) as your score increases!

## Requirements
- Python 3.10+
- `pygame` (for sound management)
- `tkinter` (usually bundled with Python)

## How to Run Locally

1.  **Install dependencies:**
    ```bash
    pip install pygame
    ```
2.  **Run the game:**
    ```bash
    python main.py
    ```

## Running with Docker (macOS)

Since this is a GUI application, you need an X11 server to display the game window from the container.

1.  **Install XQuartz:**
    ```bash
    brew install --cask xquartz
    ```
2.  **Configure XQuartz:**
    - Open XQuartz.
    - Go to `Settings` -> `Security`.
    - Check **"Allow connections from network clients"**.
    - Restart XQuartz.
3.  **Allow Local Connections:**
    In your terminal, run:
    ```bash
    xhost +localhost
    ```
4.  **Build and Run with Docker Compose:**
    ```bash
    docker compose up --build
    ```

> **Note:** When running via Docker, sound is disabled by default to avoid hardware compatibility issues. To hear the game, please run it locally using Python.


## Controls
- **Up/Down/Left/Right:** Move Airplane
- **Space:** Shoot
- **Return (Enter):** Start Game / Confirm Username
- **R:** Restart Game (on Game Over screen)
- **Backspace:** Delete character in username input

## File Structure
- `main.py`: The entry point and game controller.
- `airplane.py`: Logic for player and enemy airplanes.
- `bullet.py`: Bullet movement and collision.
- `mystery.py`: Power-up ball logic.
- `sound_manager.py`: Handles all sound effects.
- `const.py`: Game constants and configuration.
- `picture/`: Assets for airplanes, backgrounds, and explosions.
- `sfx/`: Sound effect files.
