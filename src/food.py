import random
import pygame
from src.config import CELL_SIZE, GRID_X_OFFSET, GRID_Y_OFFSET, GRID_COLS, GRID_ROWS, COLOR_FOOD

class Food:
    def __init__(self):
        self.position = (0, 0)
        self.respawn_count = 0  # To track stats or trigger animations
        
    def randomize_position(self, snake_body):
        """
        Positions the food at a random grid square not occupied by the snake.
        """
        while True:
            pos = (random.randint(0, GRID_COLS - 1), random.randint(0, GRID_ROWS - 1))
            if pos not in snake_body:
                self.position = pos
                break
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
        pygame.draw.circle(glow_surf, (*glow_color, 40), (CELL_SIZE, CELL_SIZE), CELL_SIZE * 0.9)
        pygame.draw.circle(glow_surf, (*glow_color, 90), (CELL_SIZE, CELL_SIZE), CELL_SIZE * 0.6)
        screen.blit(glow_surf, (center_x - CELL_SIZE, center_y - CELL_SIZE))
        
        # Core solid food circle
        pygame.draw.circle(screen, COLOR_FOOD, (center_x, center_y), CELL_SIZE // 3)
        # Bright center highlight
        pygame.draw.circle(screen, (255, 200, 220), (center_x - 1, center_y - 1), CELL_SIZE // 6)
