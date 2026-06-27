import random
import pygame
from src.config import CELL_SIZE, GRID_X_OFFSET, GRID_Y_OFFSET, GRID_COLS, GRID_ROWS, COLOR_FOOD

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.respawn_count = 0  # To track stats or trigger animations
        self.all_positions = {(x, y) for x in range(GRID_COLS) for y in range(GRID_ROWS)}
        
    def randomize_position(self, snake_body):
        """
        Positions the food at a random grid square not occupied by the snake.
        """
        available = list(self.all_positions - set(snake_body))
        if available:
            self.position = random.choice(available)
        self.respawn_count += 1

    def draw(self, screen):
        """
        Draws the food with a premium glowing neon effect.
        """
        col, row = self.position
        # Compute exact screen coordinate of the center of the cell
        center_x = GRID_X_OFFSET + col * CELL_SIZE + CELL_SIZE // 2
        center_y = GRID_Y_OFFSET + row * CELL_SIZE + CELL_SIZE // 2
        
        # Outer glow: concentric semi-transparent circles
        glow_color = COLOR_FOOD
        
        # Draw outer glows with alpha blending
        # Pygame surface with SRCALPHA for alpha effects
        glow_surf = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
        
        # Center of glow_surf is (CELL_SIZE, CELL_SIZE)
        import time, math
        pulse = (math.sin(time.time() * 6) + 1) / 2 # 0 to 1
        glow_radius_1 = CELL_SIZE * (0.8 + 0.2 * pulse)
        glow_radius_2 = CELL_SIZE * (0.5 + 0.2 * pulse)
        
        pygame.draw.circle(glow_surf, (*glow_color, 40), (CELL_SIZE, CELL_SIZE), glow_radius_1)
        pygame.draw.circle(glow_surf, (*glow_color, 90), (CELL_SIZE, CELL_SIZE), glow_radius_2)
        screen.blit(glow_surf, (center_x - CELL_SIZE, center_y - CELL_SIZE))
        
        # Core solid food circle
        pygame.draw.circle(screen, COLOR_FOOD, (center_x, center_y), CELL_SIZE // 3)
        # Bright center highlight
        pygame.draw.circle(screen, (255, 200, 220), (center_x - 1, center_y - 1), CELL_SIZE // 6)
