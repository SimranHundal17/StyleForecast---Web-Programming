"""
get_outfit_model.py

This file is responsible for handling weather data retrieval and
generating outfit suggestions based on weather conditions and occasion.

It acts as a logic layer that connects external weather data with
outfit recommendation rules.
"""

import requests
import os

# Fetching OpenWeather API key from environment variables for security
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


def get_weather(lat, lon):
    """
    Fetch weather data from OpenWeather API using latitude and longitude.

    Returns basic weather details like condition, temperature,
    humidity, and wind speed.
    """

    # OpenWeather API endpoint with required query parameters
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric"

    try:
        # Sending request to OpenWeather API and converting response to JSON
        data = requests.get(url).json()

        # Checking if the API response is successful
        if data.get("cod") != 200:
            return {"error": "Invalid location"}

        # Extracting only the required weather information
        return {
            "condition": data["weather"][0]["main"],
            "temp": round(data["main"]["temp"]),
            "humidity": data["main"]["humidity"],
            "wind": data["wind"]["speed"],
        }

    except:
        # Handles network errors, API downtime, or unexpected response formats
        return {"error": "Unable to fetch weather"}


def generate_outfit(lat, lon, occasion):
    """
    Generate outfit suggestions based on weather conditions and occasion.

    Uses weather data such as temperature, rain, snow, humidity,
    and wind to enhance outfit recommendations.
    """

    # Fetch weather information for the given location
    weather = get_weather(lat, lon)

    # If weather data could not be retrieved, return error immediately
    if "error" in weather:
        return {"error": weather["error"]}

    # Storing weather details in separate variables for clarity
    condition = weather["condition"]
    temp = weather["temp"]
    humidity = weather["humidity"]
    wind = weather["wind"]

    outfit = []

    # Base outfit selection depending on occasion
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

    # Additional outfit items based on weather conditions
    if "Rain" in condition:
        outfit += ["🧥 Raincoat", "☂️ Umbrella", "👢 Waterproof Shoes"]

    if "Snow" in condition:
        outfit += ["🧥 Heavy Coat", "🧣 Scarf", "🧤 Gloves", "👢 Winter Boots"]

    # Temperature-based outfit adjustments
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

    # Wind-based adjustment
    if wind > 10:
        outfit.append("🧥 Windbreaker")

    # Removing duplicate outfit items while preserving order
    outfit = list(dict.fromkeys(outfit))

    return {
        "weather": f"{condition}, {temp}°C",
        "condition": condition,
        "temp": temp,
        "humidity": humidity,
        "wind": wind,
        "outfit": outfit,
    }
