#!/usr/bin/env python3
"""Reset all saved pet data to defaults."""

import os
import json
import time

SAVE_PATH = "save.json"

def reset_save():
    """Delete the save file or reset it to default values."""
    # Default state (matches PetState defaults in pet.py)
    default_state = {
        "hunger": 0.0,
        "thirst": 0.0,
        "happiness": 100.0,
        "level": 1,
        "last_level_update": time.time(),
        "is_neglected": False
    }
    
    if os.path.exists(SAVE_PATH):
        # Show current state before reset
        try:
            with open(SAVE_PATH, "r") as f:
                old_state = json.load(f)
            print(f"Current save data:")
            print(f"  Level: {old_state.get('level', 'N/A')}")
            print(f"  Hunger: {old_state.get('hunger', 'N/A'):.1f}")
            print(f"  Thirst: {old_state.get('thirst', 'N/A'):.1f}")
            print(f"  Happiness: {old_state.get('happiness', 'N/A'):.1f}")
            print()
        except Exception as e:
            print(f"Could not read current save: {e}")
    else:
        print("No existing save file found.")
    
    # Confirm reset
    confirm = input("Are you sure you want to reset all save data? (y/N): ")
    if confirm.lower() != 'y':
        print("Reset cancelled.")
        return
    
    # Write default state
    with open(SAVE_PATH, "w") as f:
        json.dump(default_state, f)
    
    print()
    print("Save data has been reset!")
    print(f"  Level: 1")
    print(f"  Hunger: 0.0 (fully fed)")
    print(f"  Thirst: 0.0 (fully hydrated)")
    print(f"  Happiness: 100.0 (happy)")


if __name__ == "__main__":
    reset_save()

