import json
import os
import time
from dataclasses import dataclass, asdict
from typing import Literal


@dataclass
class PetState:
    """Stores the pet's core stats."""
    hunger: float = 0.0    # 0 = full, 100 = starving (hunger bar: 100 - hunger)
    thirst: float = 0.0    # 0 = hydrated, 100 = dehydrated (thirst bar: 100 - thirst)
    happiness: float = 100.0  # 0 = sad, 100 = happy (heart bar)
    level: int = 1         # Pet's level
    last_level_update: float = 0.0  # Timestamp of last level change
    is_neglected: bool = False  # True when all bars reach zero


class Pet:
    """Controls state, actions, persistence, and mood for the digital pet."""
    def __init__(self, save_path: str):
        self.save_path = save_path
        self.state = PetState()
        self._last_update = time.time()
        self.load()
        
        # Initialize last_level_update if not set
        if self.state.last_level_update == 0.0:
            self.state.last_level_update = time.time()

    # ------------------------------
    # Persistence
    # ------------------------------
    def load(self):
        """Load the pet’s state from save file (if exists)."""
        if os.path.exists(self.save_path):
            try:
                with open(self.save_path, "r") as f:
                    data = json.load(f)
                self.state = PetState(**data)
                print(f"[PET] Loaded state from {self.save_path}")
            except Exception as e:
                print(f"[PET] Failed to load state: {e}")

    def save(self):
        """Save current state to JSON file."""
        try:
            with open(self.save_path, "w") as f:
                json.dump(asdict(self.state), f)
        except Exception as e:
            print(f"[PET] Failed to save state: {e}")

    # ------------------------------
    # Game logic
    # ------------------------------
    def tick(self, minutes_elapsed: float, decay_rate: float):
        """
        Advance the pet's stats by a given amount of real time.
        Called once per frame with the minutes elapsed.
        All stats decay at the same rate (1% per hour).
        """
        s = self.state

        # All stats decay at same rate
        s.hunger = min(100.0, s.hunger + decay_rate * minutes_elapsed)
        s.thirst = min(100.0, s.thirst + decay_rate * minutes_elapsed)
        s.happiness = max(0.0, s.happiness - decay_rate * minutes_elapsed)
        
        # Check if all bars are at zero (pet is neglected)
        food_bar = max(0, 100 - s.hunger)     # Inverted hunger
        water_bar = max(0, 100 - s.thirst)    # Inverted thirst
        heart_bar = s.happiness                # Direct happiness
        
        was_neglected = s.is_neglected
        s.is_neglected = (food_bar <= 0 and water_bar <= 0 and heart_bar <= 0)
        
        # If pet recovered from neglect, reset level update timer
        if was_neglected and not s.is_neglected:
            s.last_level_update = time.time()
        
        # Update level once per day (86400 seconds)
        now = time.time()
        time_since_level_update = now - s.last_level_update
        
        if time_since_level_update >= 86400:  # 24 hours
            days_elapsed = int(time_since_level_update / 86400)
            
            if s.is_neglected:
                # Decrease level when neglected
                s.level = max(1, s.level - days_elapsed)
            else:
                # Increase level when healthy
                s.level += days_elapsed
            
            # Update timestamp
            s.last_level_update = now

    # ------------------------------
    # Player actions
    # ------------------------------
    def feed(self, amount: float):
        """Reduce hunger (feed the pet)."""
        self.state.hunger = max(0.0, self.state.hunger - amount)
        print(f"[PET] Fed pet: hunger now {self.state.hunger:.1f}")

    def drink(self, amount: float):
        """Reduce thirst (give water to pet)."""
        self.state.thirst = max(0.0, self.state.thirst - amount)
        print(f"[PET] Pet drank water: thirst now {self.state.thirst:.1f}")

    def play(self, amount: float):
        """Increase happiness (play with pet)."""
        self.state.happiness = min(100.0, self.state.happiness + amount)
        print(f"[PET] Played with pet: happiness now {self.state.happiness:.1f}")

    def reset(self):
        """Reset all stats to defaults."""
        self.state = PetState()
        self.state.last_level_update = time.time()
        print("[PET] Reset to default state")

    # ------------------------------
    # Mood logic (used for sprite selection)
    # ------------------------------
    def mood(self) -> Literal["hungry", "thirsty", "sad", "happy"]:
        """
        Return the pet's current mood string, used by UI to pick sprite.
        Returns the mood for the lowest stat, or "happy" if all stats are good.
        """
        s = self.state
        
        # Calculate bar values (higher is better)
        food_bar = 100 - s.hunger
        water_bar = 100 - s.thirst
        heart_bar = s.happiness
        
        # If all stats are good (> 70%), pet is happy
        if food_bar > 70 and water_bar > 70 and heart_bar > 70:
            return "happy"
        
        # If any stat is critically low (< 30%), show that mood
        if food_bar < 30:
            return "hungry"
        if water_bar < 30:
            return "thirsty"
        if heart_bar < 30:
            return "sad"
        
        # Otherwise, find the lowest stat and show that mood
        min_stat = min(food_bar, water_bar, heart_bar)
        
        if min_stat == food_bar:
            return "hungry"
        elif min_stat == water_bar:
            return "thirsty"
        else:  # min_stat == heart_bar
            return "sad"
