# models/outfit_model.py

outfit_templates = {
    "Casual": ["👕 T-Shirt", "👖 Jeans", "👟 Sneakers"],
    "Formal": ["👔 Shirt", "👖 Trousers", "👞 Shoes"],
    "Party": ["🧥 Jacket", "👕 Graphic Tee", "👖 Black Jeans", "👟 Sneakers"],
    "Gym": ["🏋️ Tank Top", "🩳 Shorts", "👟 Trainers"],
    "Rainy": ["🧥 Raincoat", "👖 Waterproof Pants", "☂️ Umbrella"]
}

weather_data = {
    "New Delhi": {"condition": "Sunny", "temp": 25},
    "Shimla": {"condition": "Rainy", "temp": 12},
    "Mumbai": {"condition": "Humid", "temp": 30}
}


def get_weather(location):
    """Get weather info for a location."""
    return weather_data.get(location, {"condition": "Unknown", "temp": 0})


def generate_outfit(location, occasion):
    """Generate outfit based on occasion and weather."""
    weather = get_weather(location)
    condition = weather["condition"]

    base_outfit = outfit_templates.get(occasion, outfit_templates["Casual"])

    if "Rain" in condition:
        base_outfit.append("☂️ Umbrella")
    elif weather["temp"] < 15:
        base_outfit.append("🧥 Sweater")

    return {
        "location": location,
        "weather": f"{condition}, {weather['temp']}°C",
        "occasion": occasion,
        "outfit": base_outfit
    }
