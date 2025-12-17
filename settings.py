from dataclasses import dataclass


@dataclass
class Settings:
    # Window / display
    WINDOW_WIDTH: int = 480
    WINDOW_HEIGHT: int = 320
    FPS: int = 30
    FULLSCREEN: bool = False  # True on Pi


    # Weather
    WEATHER_POLL_SECONDS: int = 600 # 10 minutes


    # Pet tuning (1% per hour = 1/60 per minute)
    STAT_DECAY_PER_MIN: float = 1.0 / 60.0  # 1% per hour for all stats
    FEED_AMOUNT: float = 25
    PLAY_AMOUNT: float = 25


    # Save file
    SAVE_PATH: str = "save.json"
    AUTOSAVE_SECONDS: int = 300  # Autosave every 5 minutes


settings = Settings()