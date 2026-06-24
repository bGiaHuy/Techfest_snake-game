# 🐍 Snake Vision AI & Autoplay

An elegant, modern Python Snake game built with **Pygame Community Edition**, featuring live hand gesture control (Computer Vision via **MediaPipe Hands** and **OpenCV**) and an automated AI solver (using **BFS shortest path search** with an advanced **Flood-Fill survival fallback**).

---

## ✨ Features

- **🎮 Mode 1: Keyboard Control**: Standard keyboard play (WASD or Arrow keys) with rapid-turn prevention buffering.
- **👁️ Mode 2: Gesture Control**:
  - Uses your webcam to detect hand skeletons in real-time.
  - Controls the snake direction by pointing your index finger relative to your wrist.
  - Embedded **Webcam HUD preview** in the sidebar displaying active skeletal landmarks.
  - Mirrored capture mapping for intuitive, responsive movement.
- **🤖 Mode 3: AI Autoplay (BFS Solver)**:
  - Finds the exact shortest path to the food on the grid in real-time.
  - **Visual Path Overlay**: Shows the planned path to the food as a glowing neon green trail.
  - **Flood-Fill Survival Fallback**: If the snake is blocked from reaching the food, it calculates the reachable space for each safe direction and picks the one leading to the largest contiguous open area. This keeps the bot alive much longer than random survival!
- **💎 Premium Design**:
  - Dark-mode slate color theme.
  - High-performance, silky smooth **60 FPS visual rendering** decoupled from game ticks (10 moves/sec).
  - Rounded body joints and eye orientation representing the direction of movement.
  - Floating glowing food animations.
  - **Visual Progress Ring** countdown on the Game Over screen.
  - High Score persistent tracking saved to `highscore.txt`.

---

## 🛠️ Architecture & Core Algorithms

### 1. BFS Pathfinding (AI Mode)
At each game update, the AI runs a **Breadth-First Search (BFS)** on the grid.
- **Vertices**: Grid squares $(x, y) \in [0, 27] \times [0, 27]$.
- **Edges**: 4-directional moves (Up, Down, Left, Right).
- **Obstacles**: Snake body segments (excluding the head).
- **Complexity**: $O(V + E) = O(N^2)$ where $N=28$, meaning search completes in less than a millisecond, making it extremely fast.

*Note: Since the grid is unweighted, BFS guarantees the same mathematical shortest path as Dijkstra or A\* but requires less overhead.*

### 2. Flood-Fill Survival Fallback
When no path to the food is available (e.g., the snake is boxed in by its own tail):
1. The AI scans all adjacent empty neighbors.
2. For each neighbor, it starts a BFS traversal to **count the total number of reachable empty squares** (Flood Fill).
3. The snake turns toward the neighbor with the **highest reachable count**, successfully avoiding trapping itself in tight pockets.

### 3. Gesture Vector Mapping (Webcam Mode)
1. Video is captured at ~30 FPS and flipped horizontally so the movement is natural (mirror-like).
2. MediaPipe Hands extracts the 2D coordinates of the **Wrist** ($W$) and the **Index Finger Tip** ($T$).
3. The displacement vector is calculated: $\vec{v} = T - W = (\Delta x, \Delta y)$.
4. If the vector magnitude $|\vec{v}| \ge 0.12$ (normalized threshold to prevent trembling/jitter):
   - If $|\Delta x| > |\Delta y|$:
     - $\Delta x > 0 \rightarrow$ **RIGHT**
     - $\Delta x < 0 \rightarrow$ **LEFT**
   - Else:
     - $\Delta y > 0 \rightarrow$ **DOWN**
     - $\Delta y < 0 \rightarrow$ **UP** (Note: screen y-coordinates increase downwards).

---

## 🚀 Installation & Running

### Prerequisites
- Python 3.7 or newer (Fully supports **Python 3.14**!)
- A webcam (for Gesture Mode)

### Step 1: Clone or place files in your directory
Make sure your directory structure matches:
```txt
snake-ai-gesture/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── game.py
│   ├── snake.py
│   ├── food.py
│   ├── gesture_controller.py
│   ├── auto_player.py
│   └── menu.py
└── highscore.txt (Auto-created)
```

### Step 2: Set up Virtual Environment & Install Dependencies
Open your command terminal in the project directory:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Windows (CMD):
.venv\Scripts\activate.bat
# Linux/macOS:
source .venv/bin/activate

# Install required libraries
pip install -r requirements.txt
```

### Step 3: Run the Game
```bash
python main.py
```

---

## 🕹️ Controls
- **Main Menu**:
  - Mouse click on buttons, OR press keys **`1`** (Keyboard), **`2`** (Gesture), **`3`** (Auto), or **`ESC`** to exit.
- **In-Game**:
  - **`ESC`**: Instantly return to Main Menu.
  - **Keyboard Mode**: Use Arrow keys or **`W, A, S, D`** to steer.
  - **Gesture Mode**: Show your hand to the camera and point with your index finger in the direction you want the snake to go.
  - **AI Mode**: Sit back and watch the AI play!
- **Game Over Screen**:
  - Shows final scores and high score indicators.
  - Automatically returns to the Main Menu after a **5-second countdown** (visualized via a progress ring).
