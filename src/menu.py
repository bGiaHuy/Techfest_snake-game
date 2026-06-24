import math
import pygame
from src.config import (
    WINDOW_WIDTH, WINDOW_HEIGHT,
    COLOR_BG, COLOR_SIDEBAR_BG, COLOR_TEXT_PRIMARY, COLOR_TEXT_SECONDARY,
    COLOR_ACCENT, COLOR_BORDER, COLOR_BUTTON_HOVER, COLOR_SNAKE_HEAD,
    COLOR_FOOD,
    FONT_FAMILY, FONT_SIZE_TITLE, FONT_SIZE_SUBTITLE, FONT_SIZE_BODY,
    MODE_KEYBOARD, MODE_GESTURE, MODE_AUTO, get_font
)

class Button:
    def __init__(self, x, y, width, height, text, value, is_accent=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.value = value
        self.is_accent = is_accent
        
    def draw(self, screen, mouse_pos, font):
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        # Color selections based on state
        if is_hovered:
            bg_color = COLOR_BUTTON_HOVER
            border_color = COLOR_SNAKE_HEAD if not self.is_accent else COLOR_ACCENT
        else:
            bg_color = COLOR_SIDEBAR_BG
            border_color = COLOR_BORDER
            
        # Draw button background
        pygame.draw.rect(screen, bg_color, self.rect, border_radius=8)
        # Draw glowing border
        pygame.draw.rect(screen, border_color, self.rect, width=2, border_radius=8)
        
        # Draw text
        text_color = COLOR_TEXT_PRIMARY if is_hovered or self.is_accent else COLOR_TEXT_SECONDARY
        text_surf = font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)
        
        return is_hovered

class Menu:
    def __init__(self):
        # Load fonts
        self.title_font = get_font(FONT_SIZE_TITLE, bold=True)
        self.subtitle_font = get_font(FONT_SIZE_SUBTITLE)
        self.body_font = get_font(FONT_SIZE_BODY)
        
        # Setup buttons
        btn_w, btn_h = 320, 50
        start_x = (WINDOW_WIDTH - btn_w) // 2
        
        self.buttons = [
            Button(start_x, 260, btn_w, btn_h, "1. Keyboard Control (Normal)", MODE_KEYBOARD),
            Button(start_x, 320, btn_w, btn_h, "2. Gesture Control (Webcam)", MODE_GESTURE),
            Button(start_x, 380, btn_w, btn_h, "3. AI Autoplay (BFS Solver)", MODE_AUTO),
            Button(start_x, 440, btn_w, btn_h, "4. Speed: Normal (1x)", 100),
            Button(start_x, 510, btn_w, btn_h, "Exit Game", -1, is_accent=True)
        ]
        
    def draw_main_menu(self, screen):
        """
        Draws the main menu with a beautiful glassmorphism panel and gradient titles.
        """
        screen.fill(COLOR_BG)
        
        # Draw background grid decoration (subtle)
        grid_spacing = 30
        for x in range(0, WINDOW_WIDTH, grid_spacing):
            pygame.draw.line(screen, (22, 26, 38), (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, grid_spacing):
            pygame.draw.line(screen, (22, 26, 38), (0, y), (WINDOW_WIDTH, y))
            
        # Draw Menu Central Panel
        panel_w, panel_h = 500, 550
        panel_x = (WINDOW_WIDTH - panel_w) // 2
        panel_y = (WINDOW_HEIGHT - panel_h) // 2
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(screen, COLOR_SIDEBAR_BG, panel_rect, border_radius=15)
        pygame.draw.rect(screen, COLOR_BORDER, panel_rect, width=2, border_radius=15)
        
        # Draw Game Title (Glowing gradient simulation)
        title_surf = self.title_font.render("SNAKE VISION AI", True, COLOR_SNAKE_HEAD)
        title_rect = title_surf.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 60))
        
        # Glowing shadow
        shadow_surf = self.title_font.render("SNAKE VISION AI", True, (0, 100, 120))
        screen.blit(shadow_surf, (title_rect.x + 2, title_rect.y + 2))
        screen.blit(title_surf, title_rect)
        
        # Subtitle
        sub_surf = self.subtitle_font.render("Play with your hands or watch AI solve it", True, COLOR_TEXT_SECONDARY)
        sub_rect = sub_surf.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 110))
        screen.blit(sub_surf, sub_rect)
        
        # Draw controls hint
        hint_text = "Select a mode below or press corresponding key [1, 2, 3, 4]"
        hint_surf = self.body_font.render(hint_text, True, COLOR_TEXT_SECONDARY)
        hint_rect = hint_surf.get_rect(center=(WINDOW_WIDTH // 2, panel_y + 180))
        screen.blit(hint_surf, hint_rect)
        
        # Draw Buttons
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            btn.draw(screen, mouse_pos, self.body_font)
            
    def handle_click(self, pos):
        """
        Returns the mode value associated with the clicked button, or None if no click.
        """
        for btn in self.buttons:
            if btn.rect.collidepoint(pos):
                return btn.value
        return None

    def update_speed_button_text(self, new_text):
        """Updates the text of the speed button."""
        for btn in self.buttons:
            if btn.value == 100:
                btn.text = new_text
                break

    def draw_game_over(self, screen, score, high_score, time_left, max_time=5.0):
        """
        Draws a semi-transparent game over overlay with a spinning countdown ring.
        """
        # Create a semi-transparent surface for glassmorphism overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((12, 14, 20, 210))  # Semi-transparent dark background
        screen.blit(overlay, (0, 0))
        
        # Central card
        card_w, card_h = 440, 360
        card_x = (WINDOW_WIDTH - card_w) // 2
        card_y = (WINDOW_HEIGHT - card_h) // 2
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        
        pygame.draw.rect(screen, COLOR_SIDEBAR_BG, card_rect, border_radius=12)
        pygame.draw.rect(screen, COLOR_BORDER, card_rect, width=2, border_radius=12)
        
        # GAME OVER title
        go_surf = self.title_font.render("GAME OVER", True, COLOR_FOOD)
        go_rect = go_surf.get_rect(center=(WINDOW_WIDTH // 2, card_y + 50))
        screen.blit(go_surf, go_rect)
        
        # Scores
        score_surf = self.subtitle_font.render(f"Final Score: {score}", True, COLOR_TEXT_PRIMARY)
        score_rect = score_surf.get_rect(center=(WINDOW_WIDTH // 2, card_y + 120))
        screen.blit(score_surf, score_rect)
        
        hs_color = COLOR_ACCENT if score >= high_score and score > 0 else COLOR_TEXT_SECONDARY
        hs_prefix = "★ NEW HIGH SCORE: " if score >= high_score and score > 0 else "High Score: "
        hs_surf = self.body_font.render(f"{hs_prefix}{high_score}", True, hs_color)
        hs_rect = hs_surf.get_rect(center=(WINDOW_WIDTH // 2, card_y + 160))
        screen.blit(hs_surf, hs_rect)
        
        # Countdown Arc & Info
        time_left = max(0.0, min(time_left, max_time))
        percent = time_left / max_time
        
        # Draw circular countdown ring
        ring_center = (WINDOW_WIDTH // 2, card_y + 250)
        ring_radius = 36
        ring_rect = pygame.Rect(ring_center[0] - ring_radius, ring_center[1] - ring_radius, ring_radius * 2, ring_radius * 2)
        
        # Background arc (dim)
        pygame.draw.circle(screen, (40, 48, 70), ring_center, ring_radius, width=4)
        
        # Active countdown arc (neon cyan)
        # Angles are in radians. 0 is pointing right, positive is clockwise in Pygame's draw.arc.
        # We want it to decrease counterclockwise.
        start_angle = -math.pi / 2
        end_angle = start_angle + (2 * math.pi * percent)
        
        # Draw arc only if percentage > 0
        if percent > 0.001:
            pygame.draw.arc(screen, COLOR_SNAKE_HEAD, ring_rect, start_angle, end_angle, width=5)
            
        # Draw number of seconds left inside the ring
        seconds_text = str(math.ceil(time_left))
        sec_surf = self.subtitle_font.render(seconds_text, True, COLOR_TEXT_PRIMARY)
        sec_rect = sec_surf.get_rect(center=ring_center)
        screen.blit(sec_surf, sec_rect)
        
        # Text instructions below ring
        prompt_surf = self.body_font.render("Returning to menu...", True, COLOR_TEXT_SECONDARY)
        prompt_rect = prompt_surf.get_rect(center=(WINDOW_WIDTH // 2, card_y + 315))
        screen.blit(prompt_surf, prompt_rect)
