import pygame
from src.config import (
    CELL_SIZE, GRID_X_OFFSET, GRID_Y_OFFSET, GRID_COLS, GRID_ROWS,
    COLOR_SNAKE_HEAD, COLOR_SNAKE_BODY_START, COLOR_SNAKE_BODY_END
)

class Snake:
    def __init__(self):
        self.reset()
        
    def reset(self):
        # Starts in the middle, facing RIGHT
        self.body = [(10, 14), (9, 14), (8, 14)]
        self.direction = (1, 0)      # (dx, dy)
        self.next_direction = (1, 0) # Buffered direction input
        self.score = 0
        
    def set_direction(self, new_dir):
        """
        Validates and buffers the next direction.
        Prevents instant 180-degree self-collision.
        """
        # Ensure new_dir is opposite of current movement
        if (new_dir[0] + self.direction[0] == 0) and (new_dir[1] + self.direction[1] == 0):
            return
        self.next_direction = new_dir

    def move(self, grow=False):
        """
        Advances the snake by one step.
        If grow is True, the snake tail is preserved (score increases).
        """
        self.direction = self.next_direction
        dx, dy = self.direction
        head_x, head_y = self.body[0]
        
        new_head = (head_x + dx, head_y + dy)
        self.body.insert(0, new_head)
        
        if not grow:
            self.body.pop()
        else:
            self.score += 1
            
    def check_collision(self):
        """
        Returns True if the head collides with boundaries or its own body.
        """
        head_x, head_y = self.body[0]
        
        # Boundary check
        if head_x < 0 or head_x >= GRID_COLS or head_y < 0 or head_y >= GRID_ROWS:
            return True
            
        # Self collision check
        if self.body[0] in self.body[1:]:
            return True
            
        return False

    def draw(self, screen):
        """
        Draws the snake with gradient-colored segments, rounded joints,
        and eyes that look in the moving direction.
        """
        n_segments = len(self.body)
        
        # Draw body segments (from tail to head)
        for i in reversed(range(n_segments)):
            x, y = self.body[i]
            
            # Calculate coordinates
            rect_x = GRID_X_OFFSET + x * CELL_SIZE + 1
            rect_y = GRID_Y_OFFSET + y * CELL_SIZE + 1
            rect_size = CELL_SIZE - 2
            
            # Interpolate color (gradient from head to tail)
            if i == 0:
                color = COLOR_SNAKE_HEAD
            else:
                # Interpolation ratio
                t = i / max(1, n_segments - 1)
                r = int(COLOR_SNAKE_BODY_START[0] * (1 - t) + COLOR_SNAKE_BODY_END[0] * t)
                g = int(COLOR_SNAKE_BODY_START[1] * (1 - t) + COLOR_SNAKE_BODY_END[1] * t)
                b = int(COLOR_SNAKE_BODY_START[2] * (1 - t) + COLOR_SNAKE_BODY_END[2] * t)
                color = (r, g, b)
            
            # Draw segment
            rect = pygame.Rect(rect_x, rect_y, rect_size, rect_size)
            pygame.draw.rect(screen, color, rect, border_radius=6)
            
            # Additional details for the head
            if i == 0:
                self._draw_eyes(screen, rect_x, rect_y, rect_size)

    def _draw_eyes(self, screen, hx, hy, size):
        """
        Helper to draw two white eyes with black pupils on the head,
        facing the current direction of movement.
        """
        dx, dy = self.direction
        eye_color = (255, 255, 255)
        pupil_color = (0, 0, 0)
        
        eye_radius = size // 6
        pupil_radius = size // 12
        
        # Calculate eye coordinates relative to the head rect
        # Left-relative and Right-relative offsets based on movement direction
        if dx == 1:   # Right
            eye1 = (hx + size * 0.7, hy + size * 0.25)
            eye2 = (hx + size * 0.7, hy + size * 0.75)
            pupil1 = (hx + size * 0.8, hy + size * 0.25)
            pupil2 = (hx + size * 0.8, hy + size * 0.75)
        elif dx == -1: # Left
            eye1 = (hx + size * 0.3, hy + size * 0.25)
            eye2 = (hx + size * 0.3, hy + size * 0.75)
            pupil1 = (hx + size * 0.2, hy + size * 0.25)
            pupil2 = (hx + size * 0.2, hy + size * 0.75)
        elif dy == 1:  # Down
            eye1 = (hx + size * 0.25, hy + size * 0.7)
            eye2 = (hx + size * 0.75, hy + size * 0.7)
            pupil1 = (hx + size * 0.25, hy + size * 0.8)
            pupil2 = (hx + size * 0.75, hy + size * 0.8)
        else:          # Up (default fallback)
            eye1 = (hx + size * 0.25, hy + size * 0.3)
            eye2 = (hx + size * 0.75, hy + size * 0.3)
            pupil1 = (hx + size * 0.25, hy + size * 0.2)
            pupil2 = (hx + size * 0.75, hy + size * 0.2)
            
        # Draw white circles
        pygame.draw.circle(screen, eye_color, (int(eye1[0]), int(eye1[1])), eye_radius)
        pygame.draw.circle(screen, eye_color, (int(eye2[0]), int(eye2[1])), eye_radius)
        # Draw pupils
        pygame.draw.circle(screen, pupil_color, (int(pupil1[0]), int(pupil1[1])), pupil_radius)
        pygame.draw.circle(screen, pupil_color, (int(pupil2[0]), int(pupil2[1])), pupil_radius)
