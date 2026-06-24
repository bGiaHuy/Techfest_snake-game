import pygame

# Window settings
WINDOW_WIDTH = 1024
WINDOW_HEIGHT = 768
FPS = 10  # Classic snake speed (10 steps per second)

# Grid settings
CELL_SIZE = 24
GRID_COLS = 28
GRID_ROWS = 28
GRID_X_OFFSET = 32
GRID_Y_OFFSET = 48

# Sidebar settings
SIDEBAR_X = GRID_X_OFFSET + (GRID_COLS * CELL_SIZE) + 32
SIDEBAR_Y = GRID_Y_OFFSET
SIDEBAR_WIDTH = WINDOW_WIDTH - SIDEBAR_X - 32
SIDEBAR_HEIGHT = GRID_ROWS * CELL_SIZE

# Webcam preview settings (inside sidebar)
WEBCAM_PREVIEW_X = SIDEBAR_X
WEBCAM_PREVIEW_Y = SIDEBAR_Y + 300
WEBCAM_PREVIEW_WIDTH = SIDEBAR_WIDTH
WEBCAM_PREVIEW_HEIGHT = int(SIDEBAR_WIDTH * 3 / 4)  # 4:3 Aspect Ratio

# Premium Palette (RGB values)
COLOR_BG = (18, 20, 28)           # Deep Dark Slate Blue
COLOR_SIDEBAR_BG = (27, 30, 46)   # Slightly Lighter Blue-Gray
COLOR_GRID_LINE = (35, 40, 58)    # Clean, subtle grid lines
COLOR_SNAKE_HEAD = (0, 240, 255)  # Neon Cyan
COLOR_SNAKE_BODY_START = (0, 240, 255)
COLOR_SNAKE_BODY_END = (112, 0, 255) # Neon Purple
COLOR_FOOD = (255, 0, 85)         # Neon Pink/Red
COLOR_PATH = (57, 255, 20)        # Neon Green
COLOR_PATH_ALPHA = 100            # Transparency level for path overlay (0-255)
COLOR_TEXT_PRIMARY = (255, 255, 255)
COLOR_TEXT_SECONDARY = (139, 155, 180)
COLOR_ACCENT = (255, 170, 0)       # Amber Gold
COLOR_BORDER = (50, 58, 86)       # Border highlight for widgets
COLOR_BUTTON_HOVER = (43, 49, 74)

# Font sizes
FONT_FAMILY = "Segoe UI"  # Clean sans-serif available on Windows
FONT_SIZE_TITLE = 36
FONT_SIZE_SUBTITLE = 20
FONT_SIZE_BODY = 16
FONT_SIZE_SMALL = 12

# Game Modes
MODE_KEYBOARD = 0
MODE_GESTURE = 1
MODE_AUTO = 2

# Font Loader Helper (Python 3.14+ Windows Safe)
def get_font(size, bold=False):
    try:
        return pygame.font.SysFont(FONT_FAMILY, size, bold=bold)
    except Exception:
        return pygame.font.Font(None, size)

