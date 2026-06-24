import os
import time
import pygame
from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS,
    CELL_SIZE, GRID_COLS, GRID_ROWS, GRID_X_OFFSET, GRID_Y_OFFSET,
    SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, SIDEBAR_HEIGHT,
    WEBCAM_PREVIEW_X, WEBCAM_PREVIEW_Y, WEBCAM_PREVIEW_WIDTH, WEBCAM_PREVIEW_HEIGHT,
    COLOR_BG, COLOR_SIDEBAR_BG, COLOR_GRID_LINE, COLOR_PATH, COLOR_PATH_ALPHA,
    COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY, COLOR_ACCENT, COLOR_BORDER, COLOR_SNAKE_HEAD,
    FONT_FAMILY, FONT_SIZE_TITLE, FONT_SIZE_SUBTITLE, FONT_SIZE_BODY, FONT_SIZE_SMALL,
    MODE_KEYBOARD, MODE_GESTURE, MODE_AUTO, get_font
)
from src.snake import Snake
from src.food import Food
from src.menu import Menu
from src.gesture_controller import GestureController
from src.auto_player import get_ai_move

# Game State Constants
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAMEOVER = 2

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Snake Vision AI & Autoplay")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        
        # Core game objects
        self.snake = Snake()
        self.food = Food()
        self.menu = Menu()
        self.gesture_controller = GestureController()
        
        # Game states
        self.state = STATE_MENU
        self.mode = MODE_KEYBOARD
        
        # Timing (decouple rendering FPS from snake movement speed)
        self.last_update_time = pygame.time.get_ticks()
        self.speed_multiplier = 1  # 1 = Normal, 2 = Fast, 5 = Turbo, 10 = Insane
        self.snake_update_delay = 100  # ms (10 updates per second)
        
        # High Score file
        self.highscore_file = "highscore.txt"
        self.high_score = self.load_high_score()
        
        # Game over countdown tracker
        self.game_over_start_time = 0
        self.game_over_duration = 5.0  # seconds
        
        # Track path list for Auto mode path visualization
        self.current_path = []
        
        # Load fonts for sidebar
        self.sidebar_title_font = get_font(FONT_SIZE_SUBTITLE, bold=True)
        self.sidebar_body_font = get_font(FONT_SIZE_BODY)
        self.sidebar_small_font = get_font(FONT_SIZE_SMALL)

    def load_high_score(self):
        """Loads high score from local file."""
        if os.path.exists(self.highscore_file):
            try:
                with open(self.highscore_file, "r") as f:
                    return int(f.read().strip())
            except Exception:
                pass
        return 0

    def save_high_score(self):
        """Saves high score to local file."""
        try:
            with open(self.highscore_file, "w") as f:
                f.write(str(self.high_score))
        except Exception:
            pass

    def run(self):
        """Main game loop executing at 60 FPS."""
        running = True
        while running:
            # Handle Pygame system events
            running = self.handle_events()
            
            # Update state based on active screen
            self.update()
            
            # Draw graphics
            self.draw()
            
            # Limit loop rate (run at smooth 60fps for animations and webcam preview)
            self.clock.tick(60)
            
        # Clean shutdown
        self.gesture_controller.stop()
        pygame.quit()

    def handle_events(self):
        """Processes keyboard/mouse events. Returns False if game exit requested."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state != STATE_MENU:
                        # Return to menu
                        self.gesture_controller.stop()
                        self.state = STATE_MENU
                    else:
                        return False
                        
                # Quick key shortcuts for menu
                if self.state == STATE_MENU:
                    if event.key in [pygame.K_1, pygame.K_KP1]:
                        self.start_game(MODE_KEYBOARD)
                    elif event.key in [pygame.K_2, pygame.K_KP2]:
                        self.start_game(MODE_GESTURE)
                    elif event.key in [pygame.K_3, pygame.K_KP3]:
                        self.start_game(MODE_AUTO)
                    elif event.key in [pygame.K_4, pygame.K_KP4, pygame.K_s]:
                        self.cycle_speed()
                        
                elif self.state == STATE_PLAYING and self.mode == MODE_KEYBOARD:
                    # Key directions for keyboard control mode
                    if event.key in [pygame.K_UP, pygame.K_w]:
                        self.snake.set_direction((0, -1))
                    elif event.key in [pygame.K_DOWN, pygame.K_s]:
                        self.snake.set_direction((0, 1))
                    elif event.key in [pygame.K_LEFT, pygame.K_a]:
                        self.snake.set_direction((-1, 0))
                    elif event.key in [pygame.K_RIGHT, pygame.K_d]:
                        self.snake.set_direction((1, 0))
                        
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.state == STATE_MENU:
                    clicked_val = self.menu.handle_click(event.pos)
                    if clicked_val is not None:
                        if clicked_val == -1:
                            return False  # Exit
                        elif clicked_val == 100:
                            self.cycle_speed()
                        else:
                            self.start_game(clicked_val)
                            
        return True

    def start_game(self, mode):
        """Initializes game objects and switches states."""
        self.mode = mode
        self.snake.reset()
        self.food.randomize_position(self.snake.body)
        self.current_path = []
        
        # Start/Stop webcam depending on mode
        if self.mode == MODE_GESTURE:
            self.gesture_controller.start()
        else:
            self.gesture_controller.stop()
            
        self.state = STATE_PLAYING
        self.last_update_time = pygame.time.get_ticks()

    def cycle_speed(self):
        """Cycles through game speed settings (1x, 2x, 5x, 10x, Custom)."""
        if self.speed_multiplier == 10:
            # Transition to Custom Speed input
            import tkinter as tk
            from tkinter import simpledialog
            
            # Hide the main tkinter root window
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True)  # Make it stay on top
            
            try:
                # Ask user for a custom speed multiplier
                custom_mult = simpledialog.askfloat(
                    "Custom Speed", 
                    "Enter speed multiplier (e.g. 1 to 50):\n(1x = Normal, 10x = Insane)", 
                    minvalue=0.1, 
                    maxvalue=100.0
                )
                if custom_mult is not None:
                    self.speed_multiplier = custom_mult
                    # 100ms divided by speed multiplier, clamped to at least 1ms delay
                    self.snake_update_delay = max(1, int(100 / custom_mult))
                    label = f"Custom ({custom_mult}x)"
                else:
                    # Cancelled, fallback to Normal
                    self.speed_multiplier = 1
                    self.snake_update_delay = 100
                    label = "Normal (1x)"
            except Exception:
                # Fallback if tkinter fails
                self.speed_multiplier = 1
                self.snake_update_delay = 100
                label = "Normal (1x)"
            finally:
                root.destroy()
        else:
            speeds = {
                1: (2, "Fast (2x)", 50),
                2: (5, "Turbo (5x)", 20),
                5: (10, "Insane (10x)", 10),
            }
            next_mult, label, delay = speeds.get(self.speed_multiplier, (1, "Normal (1x)", 100))
            self.speed_multiplier = next_mult
            self.snake_update_delay = delay
            
        # Update menu button text
        self.menu.update_speed_button_text(f"4. Speed: {label}")

    def trigger_game_over(self):
        """Sets state to game over and records the start timestamp."""
        self.state = STATE_GAMEOVER
        self.game_over_start_time = time.time()
        
        # Check and save high score
        if self.snake.score > self.high_score:
            self.high_score = self.snake.score
            self.save_high_score()
            
        # Stop webcam to release hardware
        self.gesture_controller.stop()

    def update(self):
        """Updates game state logic."""
        current_time = pygame.time.get_ticks()
        
        if self.state == STATE_PLAYING:
            # 1. Read input from gesture controller if in Gesture Mode
            if self.mode == MODE_GESTURE:
                gesture_dir = self.gesture_controller.get_direction()
                if gesture_dir:
                    self.snake.set_direction(gesture_dir)
                    
            # 2. Decouple movement logic using timer
            if current_time - self.last_update_time >= self.snake_update_delay:
                self.last_update_time = current_time
                
                # In Auto AI Mode, run pathfinding before moving
                if self.mode == MODE_AUTO:
                    head = self.snake.body[0]
                    ai_dir, path = get_ai_move(head, self.food.position, self.snake.body)
                    self.current_path = path
                    self.snake.set_direction(ai_dir)
                
                # In Gesture Mode, support AI assist when user stops pointing
                elif self.mode == MODE_GESTURE:
                    active_gesture = self.gesture_controller.get_direction()
                    if active_gesture is None:
                        # AI Assist Takeover using smart pathfinder
                        head = self.snake.body[0]
                        ai_dir, path = get_ai_move(head, self.food.position, self.snake.body)
                        self.current_path = path
                        self.snake.set_direction(ai_dir)
                    else:
                        # Clear path overlay when user is actively controlling
                        self.current_path = []
                
                # Check if snake will eat food
                next_head = (
                    self.snake.body[0][0] + self.snake.next_direction[0],
                    self.snake.body[0][1] + self.snake.next_direction[1]
                )
                eating = (next_head == self.food.position)
                
                # Perform physical move
                self.snake.move(grow=eating)
                
                # If food was eaten, spawn new food
                if eating:
                    self.food.randomize_position(self.snake.body)
                    self.current_path = []
                    
                # Check collisions (death)
                if self.snake.check_collision():
                    self.trigger_game_over()
                    
        elif self.state == STATE_GAMEOVER:
            # 5-second countdown logic returning to menu
            elapsed = time.time() - self.game_over_start_time
            if elapsed >= self.game_over_duration:
                self.state = STATE_MENU

    def draw(self):
        """Renders graphics onto the window."""
        # 1. Main Background
        self.screen.fill(COLOR_BG)
        
        # 2. Render contents based on state
        if self.state == STATE_MENU:
            self.menu.draw_main_menu(self.screen)
        else:
            # Playing or Game Over - Draw grid board and sidebar HUD
            self.draw_game_board()
            self.draw_sidebar()
            
            # Draw Path Overlay
            if self.state == STATE_PLAYING:
                self.draw_path_overlay()
                
            # Draw Entities
            self.food.draw(self.screen)
            self.snake.draw(self.screen)
            
            # If Game Over, draw overlay on top
            if self.state == STATE_GAMEOVER:
                elapsed = time.time() - self.game_over_start_time
                time_left = self.game_over_duration - elapsed
                self.menu.draw_game_over(
                    self.screen, 
                    self.snake.score, 
                    self.high_score, 
                    time_left, 
                    self.game_over_duration
                )
                
        pygame.display.flip()

    def draw_game_board(self):
        """Draws the playing grid layout with borders."""
        board_width = GRID_COLS * CELL_SIZE
        board_height = GRID_ROWS * CELL_SIZE
        
        # Board background card
        board_rect = pygame.Rect(GRID_X_OFFSET, GRID_Y_OFFSET, board_width, board_height)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BG, board_rect, border_radius=4)
        
        # Draw subtle grid lines
        for col in range(GRID_COLS + 1):
            x = GRID_X_OFFSET + col * CELL_SIZE
            pygame.draw.line(
                self.screen, 
                COLOR_GRID_LINE, 
                (x, GRID_Y_OFFSET), 
                (x, GRID_Y_OFFSET + board_height)
            )
        for row in range(GRID_ROWS + 1):
            y = GRID_Y_OFFSET + row * CELL_SIZE
            pygame.draw.line(
                self.screen, 
                COLOR_GRID_LINE, 
                (GRID_X_OFFSET, y), 
                (GRID_X_OFFSET + board_width, y)
            )
            
        # Outer boundary highlights
        pygame.draw.rect(self.screen, COLOR_BORDER, board_rect, width=2, border_radius=4)

    def draw_path_overlay(self):
        """Draws a premium glowing path overlay in Auto mode."""
        if not self.current_path or len(self.current_path) < 2:
            return
            
        # Draw lines connecting centers of cells along the path
        points = []
        for col, row in self.current_path:
            x = GRID_X_OFFSET + col * CELL_SIZE + CELL_SIZE // 2
            y = GRID_Y_OFFSET + row * CELL_SIZE + CELL_SIZE // 2
            points.append((x, y))
            
        # Draw translucent thick path background
        # Note: Pygame doesn't support thickness with alpha directly on draw.lines.
        # We can draw multiple small alpha circles on a scratch surface and blit it!
        overlay_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        
        # Draw circles at path nodes
        for pt in points[1:-1]:  # exclude head and food nodes for cleaner look
            pygame.draw.circle(overlay_surf, (*COLOR_PATH, COLOR_PATH_ALPHA), pt, 4)
            
        # Draw lines between consecutive path points
        for i in range(len(points) - 1):
            pygame.draw.line(
                overlay_surf, 
                (*COLOR_PATH, COLOR_PATH_ALPHA // 2), 
                points[i], 
                points[i+1], 
                width=3
            )
            
        self.screen.blit(overlay_surf, (0, 0))

    def draw_sidebar(self):
        """Draws the sidebar containing mode status, score cards, and webcam feed."""
        # Draw Sidebar card
        sidebar_rect = pygame.Rect(SIDEBAR_X, SIDEBAR_Y, SIDEBAR_WIDTH, SIDEBAR_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_SIDEBAR_BG, sidebar_rect, border_radius=8)
        pygame.draw.rect(self.screen, COLOR_BORDER, sidebar_rect, width=2, border_radius=8)
        
        # 1. Title
        title_surf = self.sidebar_title_font.render("GAME HUD", True, COLOR_SNAKE_HEAD)
        title_rect = title_surf.get_rect(midtop=(SIDEBAR_X + SIDEBAR_WIDTH // 2, SIDEBAR_Y + 16))
        self.screen.blit(title_surf, title_rect)
        
        # Divider line
        pygame.draw.line(
            self.screen, 
            COLOR_BORDER, 
            (SIDEBAR_X + 16, SIDEBAR_Y + 45), 
            (SIDEBAR_X + SIDEBAR_WIDTH - 16, SIDEBAR_Y + 45)
        )
        
        # 2. Mode information
        mode_names = {
            MODE_KEYBOARD: "KEYBOARD CONTROL",
            MODE_GESTURE: "GESTURE VISION",
            MODE_AUTO: "AI AUTOPLAY (BFS)"
        }
        mode_text = mode_names.get(self.mode, "UNKNOWN")
        
        mode_label = self.sidebar_small_font.render("ACTIVE MODE", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(mode_label, (SIDEBAR_X + 20, SIDEBAR_Y + 60))
        
        mode_val = self.sidebar_body_font.render(mode_text, True, COLOR_TEXT_PRIMARY)
        self.screen.blit(mode_val, (SIDEBAR_X + 20, SIDEBAR_Y + 80))
        
        # 3. Score Card
        score_label = self.sidebar_small_font.render("CURRENT SCORE", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(score_label, (SIDEBAR_X + 20, SIDEBAR_Y + 120))
        
        score_val = self.sidebar_title_font.render(str(self.snake.score), True, COLOR_ACCENT)
        self.screen.blit(score_val, (SIDEBAR_X + 20, SIDEBAR_Y + 140))
        
        # High Score Card
        hs_label = self.sidebar_small_font.render("HIGH SCORE", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(hs_label, (SIDEBAR_X + 20, SIDEBAR_Y + 190))
        
        hs_val = self.sidebar_body_font.render(str(self.high_score), True, COLOR_TEXT_PRIMARY)
        self.screen.blit(hs_val, (SIDEBAR_X + 20, SIDEBAR_Y + 210))
        
        # Divider
        pygame.draw.line(
            self.screen, 
            COLOR_BORDER, 
            (SIDEBAR_X + 16, SIDEBAR_Y + 250), 
            (SIDEBAR_X + SIDEBAR_WIDTH - 16, SIDEBAR_Y + 250)
        )
        
        # 4. Webcam Preview Widget
        preview_label = self.sidebar_small_font.render("WEBCAM FEED GESTURE HUD", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(preview_label, (WEBCAM_PREVIEW_X + 4, WEBCAM_PREVIEW_Y - 20))
        
        # Get frame surface from gesture controller (will return placeholder if not running)
        cam_surf = self.gesture_controller.get_preview_surface()
        self.screen.blit(cam_surf, (WEBCAM_PREVIEW_X, WEBCAM_PREVIEW_Y))
        
        # Draw border around webcam box
        cam_rect = pygame.Rect(WEBCAM_PREVIEW_X, WEBCAM_PREVIEW_Y, WEBCAM_PREVIEW_WIDTH, WEBCAM_PREVIEW_HEIGHT)
        pygame.draw.rect(self.screen, COLOR_BORDER, cam_rect, width=2)
        
        # Draw gesture helper indicators (overlay on webcam)
        if self.mode == MODE_GESTURE and self.gesture_controller.camera_available:
            g_dir = self.gesture_controller.get_direction()
            if g_dir:
                arrow_map = {
                    (0, -1): "↑ UP",
                    (0, 1): "↓ DOWN",
                    (-1, 0): "← LEFT",
                    (1, 0): "→ RIGHT"
                }
                dir_str = arrow_map.get(g_dir, "")
                overlay_text_surf = self.sidebar_title_font.render(dir_str, True, COLOR_ACCENT)
                # Background rect for overlay text
                text_w, text_h = overlay_text_surf.get_size()
                bg_rect = pygame.Rect(WEBCAM_PREVIEW_X + 8, WEBCAM_PREVIEW_Y + 8, text_w + 12, text_h + 6)
                pygame.draw.rect(self.screen, (18, 20, 28, 200), bg_rect, border_radius=4)
                self.screen.blit(overlay_text_surf, (WEBCAM_PREVIEW_X + 14, WEBCAM_PREVIEW_Y + 11))
                
        # 5. Quick guide text at the very bottom
        guide_y = WEBCAM_PREVIEW_Y + WEBCAM_PREVIEW_HEIGHT + 24
        
        guide_label = self.sidebar_small_font.render("CONTROLS", True, COLOR_TEXT_SECONDARY)
        self.screen.blit(guide_label, (SIDEBAR_X + 20, guide_y))
        
        guide_texts = {
            MODE_KEYBOARD: ["- [Arrow Keys] or [WASD]", "  to change direction", "- [ESC] to return to menu"],
            MODE_GESTURE: ["- Point index finger to steer", "- AI Assist takes over when", "  no hand/pointing is active", "- [ESC] to return to menu"],
            MODE_AUTO: ["- Bot playing automatically", "- Uses Breadth-First Search", "- [ESC] to return to menu"]
        }
        
        lines = guide_texts.get(self.mode, [])
        for i, line in enumerate(lines):
            line_surf = self.sidebar_small_font.render(line, True, COLOR_TEXT_PRIMARY)
            self.screen.blit(line_surf, (SIDEBAR_X + 20, guide_y + 16 + i * 16))
