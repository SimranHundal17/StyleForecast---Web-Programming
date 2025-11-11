# models/outfit_history_model.py

outfit_history = [
    {
        "id": 1,
        "date": "2025-11-09",
        "location": "New Delhi",
        "weather": "Sunny, 25°C",
        "outfit": ["👕 T-Shirt", "👖 Jeans", "👟 Sneakers"],
        "occasion": "College",
        "mood": "Casual",
        "rating": 4,
        "liked": True
    },
    {
        "id": 2,
        "date": "2025-11-08",
        "location": "Shimla",
        "weather": "Rainy, 12°C",
        "outfit": ["🧥 Sweater", "👖 Trousers", "🧣 Scarf", "☂️ Umbrella"],
        "occasion": "Vacation",
        "mood": "Cozy",
        "rating": 5,
        "liked": True
    }
]


def get_all_history():
    """Return all past outfits."""
    return outfit_history


def add_history_entry(entry):
    """Add a new outfit history record."""
    entry["id"] = len(outfit_history) + 1
    outfit_history.append(entry)
    return entry
