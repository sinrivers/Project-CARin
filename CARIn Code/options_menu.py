"""
options_menu.py
Simple options screen with a volume slider and a Back button.
Designed to be used with an existing pygame project.
"""

import pygame
import storage
import soundutils



class OptionsMenu:
    def __init__(self, screen, initial_volume=0.5):
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.running = True

        # Clamp initial volume
        self.volume = max(0.0, min(1.0, initial_volume))

        # --- Layout settings ---
        self.bg_color = (10, 10, 20)
        self.text_color = (255, 255, 255)
        self.accent_color = (255, 215, 0)

        # Slider bar (horizontal line) – made taller for easier clicking
        self.slider_rect = pygame.Rect(150, 180, 400, 20)
        self.handle_radius = 14
        self.dragging = False

        # Back button
        self.back_rect = pygame.Rect(260, 280, 200, 60)

        # Font
        self.title_font = pygame.font.SysFont("arial", 36)
        self.font = pygame.font.SysFont("arial", 24)

        # Set mixer volume if mixer is active
        self._apply_volume()

    # ----------------- internal helpers -----------------

    def _apply_volume(self):
            """
            Apply current volume to channels via soundutils and store globally.
            """
            storage.volume = self.volume
            soundutils.apply_volume()


    def _slider_pos_from_volume(self):
        """Get x position of the slider handle from current volume."""
        x = self.slider_rect.left + int(self.volume * self.slider_rect.width)
        y = self.slider_rect.centery
        return x, y

    def _volume_from_slider_pos(self, mouse_x):
        """Update volume based on mouse x position along the slider."""
        # Clamp within the slider bar
        left = self.slider_rect.left
        right = self.slider_rect.right
        mouse_x = max(left, min(right, mouse_x))
        # Map to 0.0–1.0
        rel = (mouse_x - left) / self.slider_rect.width
        self.volume = rel
        self._apply_volume()

    # ----------------- drawing -----------------

    def draw(self):
        self.screen.fill(self.bg_color)

        # Title
        title_surf = self.title_font.render("Options", True, self.text_color)
        self.screen.blit(
            title_surf,
            (
                self.screen.get_width() // 2 - title_surf.get_width() // 2,
                80,
            ),
        )

        # Volume label
        vol_percent = int(self.volume * 100)
        vol_text = self.font.render(f"Volume: {vol_percent}%", True, self.text_color)
        self.screen.blit(
            vol_text,
            (
                self.screen.get_width() // 2 - vol_text.get_width() // 2,
                140,
            ),
        )

        # Slider line
        pygame.draw.rect(self.screen, (80, 80, 80), self.slider_rect, border_radius=3)
        pygame.draw.rect(
            self.screen, self.accent_color, self.slider_rect, 2, border_radius=3
        )

        # Slider handle
        handle_x, handle_y = self._slider_pos_from_volume()
        pygame.draw.circle(
            self.screen, self.accent_color, (handle_x, handle_y), self.handle_radius
        )
        pygame.draw.circle(
            self.screen,
            (0, 0, 0),
            (handle_x, handle_y),
            self.handle_radius - 3,
            )

        # Back button
        pygame.draw.rect(
            self.screen, (40, 40, 40), self.back_rect, border_radius=10
        )
        pygame.draw.rect(
            self.screen, self.accent_color, self.back_rect, 3, border_radius=10
        )

        back_text = self.font.render("Back", True, self.text_color)
        self.screen.blit(
            back_text,
            (
                self.back_rect.centerx - back_text.get_width() // 2,
                self.back_rect.centery - back_text.get_height() // 2,
            ),
        )

        pygame.display.flip()

    # ----------------- event handling -----------------

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # left click
                mx, my = event.pos

                # 1) Back button first, so clicking Back doesn't move the slider
                if self.back_rect.collidepoint(mx, my):
                    self.running = False
                    return

                # 2) Slider handle / bar
                # make a generous hitbox around the handle
                hx, hy = self._slider_pos_from_volume()
                handle_hit = pygame.Rect(
                    hx - self.handle_radius * 2,
                    hy - self.handle_radius * 2,
                    self.handle_radius * 4,
                    self.handle_radius * 4,
                    )
                if handle_hit.collidepoint(mx, my) or self.slider_rect.collidepoint(
                        mx, my
                ):
                    self.dragging = True
                    self._volume_from_slider_pos(mx)

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                mx, my = event.pos
                self._volume_from_slider_pos(mx)

    # ----------------- main loop -----------------

    def run(self):
        """
        Run the options menu loop.
        Returns the final volume (0.0–1.0) when Back is pressed or window closed.
        """
        while self.running:
            for event in pygame.event.get():
                self.handle_event(event)

            self.draw()
            self.clock.tick(60)

        return self.volume


# Allow this file to be tested by running directly
if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    storage.volume = 0.5
    pygame.mixer.music.set_volume(storage.volume)

    screen = pygame.display.set_mode((720, 480))
    pygame.display.set_caption("Options Menu Test")

    # Optional: start playing some music to hear volume changes
    # pygame.mixer.music.load("some_song.ogg")
    # pygame.mixer.music.play(-1)

    options = OptionsMenu(screen, initial_volume=storage.volume)
    vol = options.run()
    print("Final volume:", vol)

    pygame.quit()
