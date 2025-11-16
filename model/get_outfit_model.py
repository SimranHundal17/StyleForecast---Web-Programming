# model/get_outfit_model.py
import requests
import os

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(lat, lon):
    """
    Fetch weather using OpenWeather API with latitude and longitude.
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        data = requests.get(url).json()

        if data.get("cod") != 200:
            return {"error": "Invalid location"}

        return {
            "condition": data["weather"][0]["main"],
            "temp": round(data["main"]["temp"]),
            "humidity": data["main"]["humidity"],
            "wind": data["wind"]["speed"],
        }

    except:
        return {"error": "Unable to fetch weather"}


def generate_outfit(lat, lon, occasion):
    """
    Generate outfit suggestions based on weather + occasion.
    """
    weather = get_weather(lat, lon)

    if "error" in weather:
        return {"error": weather["error"]}

    condition = weather["condition"]
    temp = weather["temp"]
    humidity = weather["humidity"]
    wind = weather["wind"]

    outfit = []

    if occasion == "Casual":
        outfit = ["👕 T-Shirt", "👖 Jeans", "👟 Sneakers"]
    elif occasion == "Formal":
        outfit = ["👔 Shirt", "👖 Trousers", "👞 Dress Shoes"]
    elif occasion == "Party":
        outfit = ["🧥 Jacket", "👕 Graphic Tee", "👖 Black Jeans", "👟 Sneakers"]
    elif occasion == "Gym":
        outfit = ["🏋️ Tank Top", "🩳 Shorts", "👟 Trainers"]
    elif occasion == "Rainy":
        outfit = ["🧥 Raincoat", "👖 Waterproof Pants", "☂️ Umbrella"]

    # Weather Intelligence
    if "Rain" in condition:
        outfit += ["🧥 Raincoat", "☂️ Umbrella", "👢 Waterproof Shoes"]

    if "Snow" in condition:
        outfit += ["🧥 Heavy Coat", "🧣 Scarf", "🧤 Gloves", "👢 Winter Boots"]

    if temp > 30:
        outfit += ["🩳 Shorts", "👕 Light Cotton Tee"]
        if humidity > 75:
            outfit.append("💨 Breathable Fabric")

    elif 20 <= temp <= 30:
        outfit += ["👕 T-Shirt", "🧢 Cap"]

    elif 10 <= temp < 20:
        outfit += ["🧥 Light Jacket", "👟 Closed Shoes"]

    elif temp < 10:
        outfit += ["🧥 Thermal Jacket", "🧤 Gloves", "🧣 Scarf"]

    if wind > 10:
        outfit.append("🧥 Windbreaker")

    outfit = list(dict.fromkeys(outfit))

    return {
        "weather": f"{condition}, {temp}°C",
        "condition": condition,
        "temp": temp,
        "humidity": humidity,
        "wind": wind,
        "outfit": outfit,
    }
