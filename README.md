# Snake Vision AI & Autoplay

An advanced, modern Snake game built with Pygame. It features three distinct ways to play:
1. **Keyboard Control**: Classic WASD or Arrow Keys.
2. **Gesture Vision**: Play using your hand gestures via webcam (using MediaPipe). Point to steer the snake! If you stop pointing, an AI Assist takes over automatically.
3. **AI Autoplay**: Watch a smart bot play the game perfectly using A* Search and Hamiltonian Cycle algorithms.

## Features
- **Premium Aesthetics**: Dark theme, neon accents, glowing food, particle effects, and high-DPI scaling.
- **Audio**: Procedurally generated beep sound effects (using numpy and Pygame).
- **Responsive Layout**: Resizable window with aspect-ratio preserving logic.

## Requirements
- Python 3.8+
- Webcam (for Gesture Mode)

## Installation

```bash
pip install -r requirements.txt
```

## Running the Game

```bash
python main.py
```

## How to Play
- **Menu**: Click on the modes to start. Click the speed button to cycle through speeds.
- **In-game**: Press `P` or `Space` to pause the game.
- **Esc**: Return to the main menu.
