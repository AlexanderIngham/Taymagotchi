import pygame
import datetime as dt
from settings import settings


class Fonts:
    """Load and scale fonts dynamically based on display height."""
    def __init__(self):
        self.large = pygame.font.Font("assets/fonts/Inter-Bold.ttf", int(settings.WINDOW_HEIGHT * 0.22))
        self.medium = pygame.font.Font("assets/fonts/Inter-Bold.ttf", int(settings.WINDOW_HEIGHT * 0.10))
        self.small = pygame.font.Font("assets/fonts/Inter-Regular.ttf", int(settings.WINDOW_HEIGHT * 0.06))
        self.tiny_bold = pygame.font.Font("assets/fonts/Inter-Bold.ttf", int(settings.WINDOW_HEIGHT * 0.04))


class Sprites:
    """Load and manage pet and weather sprites."""
    def __init__(self):
        # Pet sprites (you can replace these PNGs later with real art)
        self.pet_idle_1 = self._load("assets/sprites/pet_idle_1.png")
        self.pet_idle_2 = self._load("assets/sprites/pet_idle_2.png")
        self.pet_sleep = self._load("assets/sprites/pet_idle_1.png")
        self.pet_happy = self._load("assets/sprites/pet_idle_1.png")
        self.pet_hungry = self._load("assets/sprites/pet_idle_1.png")
        self.pet_blink = self._load("assets/sprites/pet_idle_1.png", optional=True)

        # Weather icons
        self.weather = {
            "clear": self._load("assets/sprites/weather/clear.png"),
            "clouds": self._load("assets/sprites/weather/clouds.png"),
            "rain": self._load("assets/sprites/weather/rain.png"),
            "snow": self._load("assets/sprites/weather/snow.png"),
            "mist": self._load("assets/sprites/weather/mist.png"),
        }

        # Backgrounds
        self.backgrounds = {
            "clear_night": self._load("assets/sprites/backgrounds/clear_night.jpg", optional=True),
            "clear": self._load("assets/sprites/backgrounds/clear.png", optional=True),
            "clouds_night": self._load("assets/sprites/backgrounds/clouds_night.jpg", optional=True),
            "clouds": self._load("assets/sprites/backgrounds/clouds.jpg", optional=True),
            "mist_night": self._load("assets/sprites/backgrounds/mist_night.jpg", optional=True),
            "mist": self._load("assets/sprites/backgrounds/mist.png", optional=True),
            "rain_night": self._load("assets/sprites/backgrounds/rain_night.jpg", optional=True),
            "rain": self._load("assets/sprites/backgrounds/rain.jpg", optional=True),
            "snow_night": self._load("assets/sprites/backgrounds/snow_night.png", optional=True),
            "snow": self._load("assets/sprites/backgrounds/snow.jpg", optional=True),
        }
        # Default background (used before weather loads)
        #self.default_background = self._load("assets/sprites/backgrounds/mountain-trees.png", optional=True)
        
        self.default_background = self._load("assets/sprites/backgrounds/rain.jpg", optional=True)
        
        # Text colors for each background (white or black)
        self.text_colors = {
            "clear_night": (255, 255, 255),
            "clear": (20, 20, 20),
            "clouds_night": (255, 255, 255),
            "clouds": (20, 20, 20),
            "mist_night": (255, 255, 255),      
            "mist": (20, 20, 20),
            "rain_night": (255, 255, 255),
            "rain": (255, 255, 255),
            "snow_night": (255, 255, 255),
            "snow": (20, 20, 20),
            "default": (20, 20, 20),
        }

        # Timing for simple idle animation
        self._last_idle_swap = 0
        self._idle_toggle = False

    def _load(self, path, optional=False):
        """Safely load images with transparency."""
        try:
            img = pygame.image.load(path).convert_alpha()
            return img
        except FileNotFoundError:
            if optional:
                return None
            surf = pygame.Surface((64, 64), pygame.SRCALPHA)
            surf.fill((200, 200, 200, 255))
            pygame.draw.rect(surf, (120, 120, 120), surf.get_rect(), 2)
            return surf

    # ------------------------------------------------------------
    # Sprite selection
    # ------------------------------------------------------------
    def pet_for_mood(self, mood: str, now_ms: int) -> pygame.Surface:
        """Select correct sprite based on mood + idle timing."""
        # Simple animation between idle frames
        if now_ms - self._last_idle_swap > 800:
            self._idle_toggle = not self._idle_toggle
            self._last_idle_swap = now_ms

        # Map moods to sprites
        if mood == "happy" and self.pet_happy:
            return self.pet_happy
        if mood == "hungry" and self.pet_hungry:
            return self.pet_hungry
        if mood == "thirsty" and self.pet_idle_2:
            # Use idle_2 for thirsty (or create a dedicated sprite)
            return self.pet_idle_2
        if mood == "sad" and self.pet_sleep:
            # Use sleep sprite for sad (or create a dedicated sprite)
            return self.pet_sleep

        # Default idle animation
        if self._idle_toggle and self.pet_idle_2:
            return self.pet_idle_2
        return self.pet_idle_1 or self.pet_idle_2


# ------------------------------------------------------------
# Drawing functions
# ------------------------------------------------------------

def draw_clock(surface: pygame.Surface, fonts: Fonts, text_color=(20, 20, 20)):
    """Draw the current time and date."""
    now = dt.datetime.now()
    time_str = now.strftime("%H:%M")
    date_str = now.strftime("%a, %b %d")

    # Use slightly lighter shade for date (blend with text_color)
    date_color = tuple(min(255, c + 20) if c < 128 else max(0, c - 20) for c in text_color)

    time_surf = fonts.large.render(time_str, True, text_color)
    date_surf = fonts.small.render(date_str, True, date_color)

    surface.blit(time_surf, (int(settings.WINDOW_WIDTH * 0.04), int(settings.WINDOW_HEIGHT * 0.05)))
    surface.blit(date_surf, (int(settings.WINDOW_WIDTH * 0.05), int(settings.WINDOW_HEIGHT * 0.30)))


def draw_weather(surface, fonts: Fonts, sprites, weather, text_color=(20, 20, 20)):
    """Draw current weather using emojis instead of images."""
    if not weather:
        return

    # Pick emoji
    emoji_map = {
        "clear": "☀️",
        "clouds": "☁️",
        "rain": "🌧️",
        "snow": "❄️",
        "mist": "🌫️",
    }
    emoji = emoji_map.get(weather.icon_key, "🌤️")

    # Choose position and render
    x = settings.WINDOW_WIDTH - int(settings.WINDOW_WIDTH * 0.05)
    y = int(settings.WINDOW_HEIGHT * 0.05)

    emoji_font = pygame.font.SysFont("Segoe UI Emoji", int(settings.WINDOW_HEIGHT * 0.18))
    emoji_surf = emoji_font.render(emoji, True, text_color)
    surface.blit(emoji_surf, (x - emoji_surf.get_width(), y))

    # Draw temperature + condition text (slightly lighter/darker for condition)
    cond_color = tuple(min(255, c + 40) if c < 128 else max(0, c - 40) for c in text_color)
    
    temp_text = f"{int(round(weather.temp_c))}°"
    cond_text = weather.condition
    temp_surf = fonts.medium.render(temp_text, True, text_color)
    cond_surf = fonts.small.render(cond_text, True, cond_color)

    surface.blit(temp_surf, (x - emoji_surf.get_width() - temp_surf.get_width() - 12, y + 8))
    surface.blit(cond_surf, (x - emoji_surf.get_width() - cond_surf.get_width() - 12,
                             y + temp_surf.get_height() + 8))



def draw_pet(surface: pygame.Surface, sprites: Sprites, mood: str):
    """Draw pixel-art pet with crisp edges (no blur).
    Returns the rect of the pet for touch detection."""
    now_ms = pygame.time.get_ticks()
    sprite = sprites.pet_for_mood(mood, now_ms)

    # --- pixel-perfect scaling ---
    scale_factor = 8  # try 4, 6, 8 depending on your display
    target_w = sprite.get_width() * scale_factor
    target_h = sprite.get_height() * scale_factor
    scaled = pygame.transform.scale(sprite, (target_w, target_h))

    # Center bottom (leave space for status bars and status text)
    x = (settings.WINDOW_WIDTH - target_w) // 2
    y = settings.WINDOW_HEIGHT - target_h - int(settings.WINDOW_HEIGHT * 0.19)

    surface.blit(scaled, (x, y))
    
    # Return pet rect for collision detection
    return pygame.Rect(x, y, target_w, target_h)


def draw_floating_hearts(surface: pygame.Surface, fonts: Fonts, floating_hearts: list, text_color=(20, 20, 20)):
    """Draw floating hearts animation."""
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", int(settings.WINDOW_HEIGHT * 0.06))
    
    for heart in floating_hearts:
        # Only draw if delay has passed (age > 0)
        if heart['age'] > 0:
            # Calculate fade based on age
            alpha = max(0, min(255, int(255 * (1 - heart['age'] / heart['lifespan']))))
            
            # Render heart emoji
            heart_surf = emoji_font.render("❤️", True, text_color)
            
            # Apply alpha (fade out)
            if alpha < 255:
                heart_surf.set_alpha(alpha)
            
            # Draw at current position
            surface.blit(heart_surf, (int(heart['x']), int(heart['y'])))


def draw_pet_status(surface: pygame.Surface, fonts: Fonts, mood: str, text_color=(20, 20, 20)):
    """Draw the pet status message below the pet."""
    now = dt.datetime.now()
    
    # Determine time of day
    if 5 <= now.hour < 12:
        time_of_day = "morning"
    elif 12 <= now.hour < 18:
        time_of_day = "afternoon"
    elif 18 <= now.hour < 22:
        time_of_day = "evening"
    else:
        time_of_day = "night"
    
    # Create status message
    status_text = f"Good {time_of_day} Tay, Stotch is currently {mood}"
    
    # Render text with tiny bold font
    status_surf = fonts.tiny_bold.render(status_text, True, text_color)
    
    # Center horizontally, position below pet
    x = (settings.WINDOW_WIDTH - status_surf.get_width()) // 2
    y = settings.WINDOW_HEIGHT - int(settings.WINDOW_HEIGHT * 0.17)
    
    surface.blit(status_surf, (x, y))


def draw_status_bars(surface: pygame.Surface, fonts: Fonts, pet_state, text_color=(20, 20, 20), dragged_emoji=None, drag_pos=None):
    """Draw hunger, thirst, and happiness bars at the bottom with emoji labels.
    Returns a dict mapping emoji to their rect positions for touch detection."""
    # Calculate bar values (0-100, higher is better)
    food_level = max(0, 100 - pet_state.hunger)    # Invert: 100 = well fed
    water_level = max(0, 100 - pet_state.thirst)   # Invert: 100 = hydrated
    heart_level = pet_state.happiness               # Direct: 100 = happy
    
    # Bar settings
    bar_height = int(settings.WINDOW_HEIGHT * 0.035)
    bar_width = int(settings.WINDOW_WIDTH * 0.20)  # Slightly smaller bars
    bar_spacing = int(settings.WINDOW_WIDTH * 0.02)  # Less spacing between bars
    y_position = settings.WINDOW_HEIGHT - int(settings.WINDOW_HEIGHT * 0.08)
    
    # Emoji font
    emoji_font = pygame.font.SysFont("Segoe UI Emoji", int(settings.WINDOW_HEIGHT * 0.05))
    
    # Define bars: (emoji, value, color_full, color_empty, action_type)
    bars = [
        ("🍔", food_level, (76, 175, 80), (200, 200, 200), "feed"),     # Green for food
        ("💧", water_level, (33, 150, 243), (200, 200, 200), "drink"),  # Blue for water
        ("❤️", heart_level, (244, 67, 54), (200, 200, 200), "play"),    # Red for happiness
    ]
    
    # Calculate total width and position to right of level indicator
    emoji_width = int(settings.WINDOW_HEIGHT * 0.05)
    emoji_spacing = 12  # Space between emoji and bar
    total_width = len(bars) * (bar_width + emoji_width + emoji_spacing) + (len(bars) - 1) * bar_spacing
    
    # Start after level indicator (with more margin for 3-digit levels)
    level_text_width = int(settings.WINDOW_WIDTH * 0.18)  # More space for 3-digit levels
    start_x = level_text_width
    
    emoji_rects = {}  # Store emoji positions for hit detection
    
    # Draw each bar
    for i, (emoji, value, color_full, color_empty, action_type) in enumerate(bars):
        x = start_x + i * (bar_width + emoji_width + emoji_spacing + bar_spacing)
        emoji_y = y_position - int(bar_height * 0.2)
        
        # Skip drawing if this emoji is being dragged
        if dragged_emoji != action_type:
            # Draw emoji
            emoji_surf = emoji_font.render(emoji, True, text_color)
            surface.blit(emoji_surf, (x, emoji_y))
            
            # Store emoji rect for touch detection
            emoji_rects[action_type] = pygame.Rect(x, emoji_y, emoji_surf.get_width(), emoji_surf.get_height())
        else:
            # Still store the rect even when dragging
            emoji_surf = emoji_font.render(emoji, True, text_color)
            emoji_rects[action_type] = pygame.Rect(x, emoji_y, emoji_surf.get_width(), emoji_surf.get_height())
        
        bar_x = x + emoji_width + emoji_spacing  # More space between emoji and bar
        
        # Draw background bar (empty)
        bg_rect = pygame.Rect(bar_x, y_position, bar_width, bar_height)
        pygame.draw.rect(surface, color_empty, bg_rect, border_radius=int(bar_height * 0.3))
        
        # Draw filled bar (current value)
        if value > 0:
            fill_width = int(bar_width * (value / 100))
            fill_rect = pygame.Rect(bar_x, y_position, fill_width, bar_height)
            pygame.draw.rect(surface, color_full, fill_rect, border_radius=int(bar_height * 0.3))
        
        # Draw border
        border_color = tuple(max(0, c - 60) for c in text_color)
        pygame.draw.rect(surface, border_color, bg_rect, width=2, border_radius=int(bar_height * 0.3))
    
    # Draw dragged emoji at cursor position if dragging
    if dragged_emoji and drag_pos:
        emoji_map = {"feed": "🍔", "drink": "💧", "play": "❤️"}
        if dragged_emoji in emoji_map:
            emoji_surf = emoji_font.render(emoji_map[dragged_emoji], True, text_color)
            # Center the emoji on the cursor
            drag_x = drag_pos[0] - emoji_surf.get_width() // 2
            drag_y = drag_pos[1] - emoji_surf.get_height() // 2
            surface.blit(emoji_surf, (drag_x, drag_y))
    
    return emoji_rects


def draw_level_indicator(surface: pygame.Surface, fonts: Fonts, level: int, text_color=(20, 20, 20)):
    """Draw the pet's level indicator."""
    # Level text - use tiny bold font for smaller size
    level_text = f"Lv {level}"
    
    # Render text with tiny bold font
    level_surf = fonts.tiny_bold.render(level_text, True, text_color)
    
    # Position at bottom left, vertically aligned with status bars
    x = int(settings.WINDOW_WIDTH * 0.03)
    # Align with status bar y_position
    bar_y_position = settings.WINDOW_HEIGHT - int(settings.WINDOW_HEIGHT * 0.08)
    bar_height = int(settings.WINDOW_HEIGHT * 0.035)
    # Center the level text vertically with the bars
    y = bar_y_position + (bar_height - level_surf.get_height()) // 2
    
    # Draw the level text
    surface.blit(level_surf, (x, y))

def draw_background(surface: pygame.Surface, sprites: Sprites, weather):
    """
    Draw the correct background based on weather and time of day.
    - Uses default background until weather loads.
    - Switches to night version if time is between 7pm and 6am.
    - Returns the appropriate text color for the background.
    """
    # Check if it's nighttime (7pm - 6am)
    now = dt.datetime.now()
    is_night = now.hour >= 19 or now.hour < 6
    
    # Determine which background key to use
    bg_key = None
    if weather and weather.icon_key:
        if is_night:
            night_key = f"{weather.icon_key}_night"
            # Use night version if available, otherwise fall back to day version
            if night_key in sprites.backgrounds and sprites.backgrounds[night_key]:
                bg_key = night_key
            else:
                bg_key = weather.icon_key
        else:
            bg_key = weather.icon_key
    
    # Get the background image
    if bg_key and bg_key in sprites.backgrounds and sprites.backgrounds[bg_key]:
        bg = sprites.backgrounds[bg_key]
    else:
        bg = sprites.default_background
        bg_key = "default"

    # Draw the background
    if bg:
        # Scale to fit the entire screen
        bg_scaled = pygame.transform.scale(bg, (settings.WINDOW_WIDTH, settings.WINDOW_HEIGHT))
        surface.blit(bg_scaled, (0, 0))
    else:
        # fallback plain background color
        surface.fill((255, 255, 255))
    
    # Return the appropriate text color for this background
    text_color = sprites.text_colors.get(bg_key, sprites.text_colors["default"])
    return text_color

