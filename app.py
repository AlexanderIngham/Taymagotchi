import os
import sys
import time
import asyncio
import pygame

from settings import settings
from weather import load_provider, Weather
from pet import Pet
from ui import Fonts, Sprites, draw_clock, draw_weather, draw_pet, draw_pet_status, draw_background, draw_status_bars, draw_level_indicator, draw_floating_hearts

BG = (255, 255, 255)


class App:
    def __init__(self):
        pygame.init()

        flags = pygame.FULLSCREEN if settings.FULLSCREEN else 0
        self.screen = pygame.display.set_mode((settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT), flags)
        pygame.display.set_caption("Clock + Weather + Pet")

        self.clock = pygame.time.Clock()
        self.fonts = Fonts()
        self.sprites = Sprites()

        # Weather provider (async)
        self.weather_provider = load_provider()
        self.weather: Weather | None = None
        self._last_weather_ts = 0

        # Pet system
        self.pet = Pet(save_path=settings.SAVE_PATH)

        # Touch/drag state
        self.dragged_emoji = None  # Which emoji is being dragged ("feed", "drink", "play")
        self.drag_pos = None       # Current position of drag
        self.emoji_rects = {}      # Emoji hitboxes
        self.pet_rect = None       # Pet hitbox

        # Floating hearts for feedback
        self.floating_hearts = []  # List of (x, y, age) tuples

        # Async event loop for background tasks
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

    def run(self):
        """Main synchronous entrypoint."""
        try:
            self.loop.run_until_complete(self._run_async())
        finally:
            self.loop.close()
            pygame.quit()

    async def _run_async(self):
        """Async main loop so we can await weather without blocking."""
        running = True
        next_weather_refresh = 0
        next_autosave = time.time() + settings.AUTOSAVE_SECONDS

        while running:
            dt_ms = self.clock.tick(settings.FPS)

            # Event handling
            running = self.handle_events()

            # Game logic
            minutes = dt_ms / 1000.0 / 60.0
            self.pet.tick(minutes, settings.STAT_DECAY_PER_MIN)

            # Weather update (every X seconds, async)
            now = time.time()
            if now > next_weather_refresh:
                asyncio.create_task(self.update_weather())
                next_weather_refresh = now + settings.WEATHER_POLL_SECONDS

            # Autosave every 5 minutes
            if now > next_autosave:
                self.pet.save()
                print(f"[AUTOSAVE] Pet state saved at {time.strftime('%H:%M:%S')}")
                next_autosave = now + settings.AUTOSAVE_SECONDS

            # Update floating hearts
            self.update_floating_hearts(dt_ms / 1000.0)

            # Draw frame
            self.draw()
            pygame.display.flip()

            # Let asyncio tasks run (weather fetch)
            await asyncio.sleep(0)

    def handle_events(self):
        """Process touch & window events."""
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                self.pet.save()
                return False

            # Touch/mouse events for drag and drop
            if e.type == pygame.MOUSEBUTTONDOWN:
                pos = e.pos
                # Check if touch started on an emoji
                for action_type, rect in self.emoji_rects.items():
                    if rect.collidepoint(pos):
                        self.dragged_emoji = action_type
                        self.drag_pos = pos
                        break
            
            elif e.type == pygame.MOUSEMOTION:
                if self.dragged_emoji:
                    self.drag_pos = e.pos
            
            elif e.type == pygame.MOUSEBUTTONUP:
                if self.dragged_emoji and self.drag_pos:
                    # Check if dropped on pet
                    if self.pet_rect and self.pet_rect.collidepoint(self.drag_pos):
                        # Perform the action
                        if self.dragged_emoji == "feed":
                            self.pet.feed(settings.FEED_AMOUNT)
                            self.spawn_floating_hearts()
                        elif self.dragged_emoji == "drink":
                            self.pet.drink(settings.FEED_AMOUNT)
                            self.spawn_floating_hearts()
                        elif self.dragged_emoji == "play":
                            self.pet.play(settings.PLAY_AMOUNT)
                            self.spawn_floating_hearts()
                
                # Reset drag state
                self.dragged_emoji = None
                self.drag_pos = None

            # Keep keyboard shortcuts for testing/debugging
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    self.pet.save()
                    return False
                if e.key == pygame.K_f:
                    self.pet.feed(settings.FEED_AMOUNT)
                    self.spawn_floating_hearts()
                if e.key == pygame.K_d:
                    self.pet.drink(settings.FEED_AMOUNT)
                    self.spawn_floating_hearts()
                if e.key == pygame.K_p:
                    self.pet.play(settings.PLAY_AMOUNT)
                    self.spawn_floating_hearts()
                if e.key == pygame.K_r:
                    self.pet.reset()
        return True

    def spawn_floating_hearts(self):
        """Spawn 3 hearts that float upward from the pet."""
        if not self.pet_rect:
            return
        
        # Spawn 3 hearts at staggered times (0ms, 100ms, 200ms)
        pet_center_x = self.pet_rect.centerx
        pet_top_y = self.pet_rect.top
        
        for i in range(3):
            # Stagger spawn time and horizontal position
            delay = i * 0.1  # 100ms delay between each heart
            x_offset = (i - 1) * 20  # Spread hearts horizontally
            self.floating_hearts.append({
                'x': pet_center_x + x_offset,
                'y': pet_top_y,
                'age': -delay,  # Negative age = delayed start
                'lifespan': 1.5  # Hearts live for 1.5 seconds
            })

    def update_floating_hearts(self, dt_seconds: float):
        """Update positions of floating hearts and remove expired ones."""
        # Update existing hearts
        for heart in self.floating_hearts[:]:
            heart['age'] += dt_seconds
            
            # Only move if age is positive (delay passed)
            if heart['age'] > 0:
                # Float upward (50 pixels per second)
                heart['y'] -= 50 * dt_seconds
            
            # Remove if expired
            if heart['age'] > heart['lifespan']:
                self.floating_hearts.remove(heart)

    async def update_weather(self):
        """Fetch weather asynchronously using python-weather."""
        try:
            self.weather = await self.weather_provider.get_async()
        except Exception as e:
            print(f"[WARN] Weather fetch failed: {e}")
            # keep last known weather or fallback
            if not self.weather:
                self.weather = Weather(0.0, "N/A", "clouds")

    def draw(self):
        self.screen.fill(BG)
        text_color = draw_background(self.screen, self.sprites, getattr(self, "weather", None))
        draw_clock(self.screen, self.fonts, text_color)
        if self.weather:
            draw_weather(self.screen, self.fonts, self.sprites, self.weather, text_color)
        
        # Draw pet and get its rect for collision detection
        pet_mood = self.pet.mood()
        self.pet_rect = draw_pet(self.screen, self.sprites, pet_mood)
        
        # Draw floating hearts
        draw_floating_hearts(self.screen, self.sprites, self.floating_hearts)
        
        # Draw pet status message
        draw_pet_status(self.screen, self.fonts, pet_mood, text_color)
        
        # Draw status bars and get icon rects for touch detection
        self.emoji_rects = draw_status_bars(
            self.screen, self.fonts, self.sprites, self.pet.state, text_color,
            self.dragged_emoji, self.drag_pos
        )
        
        draw_level_indicator(self.screen, self.fonts, self.pet.state.level, text_color)


if __name__ == "__main__":
    App().run()
