import json
import random
import os
import logging

logger = logging.getLogger(__name__)

def load_random_lore():
    """
    Loads the Yeti Lore JSON and returns a formatted string containing 
    a random selection of sightings, nomenclature, and scientific facts.
    """
    try:
        # Resolve absolute path to json
        base_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(base_dir, "yeti_lore.json")
        
        with open(json_path, "r") as f:
            data = json.load(f)
            
        # Select random items
        sighting = random.choice(data.get("sightings", []))
        name = random.choice(data.get("names", []))
        science = random.choice(data.get("science_myth", []))
        
        lore_text = (
            f"\n- Memory ({sighting['year']}): {sighting['event']} - \"{sighting['memory']}\""
            f"\n- Knowledge: The name '{name['term']}' means '{name['meaning']}'. {name['context']}"
            f"\n- Perspective: On {science['topic']} - {science['perspective']}"
        )
        return lore_text
        
    except Exception as e:
        logger.error(f"Failed to load lore: {e}")
        # Fallback if file missing
        return "\n- Memory: I remember the ice of the Menlung Glacier."
