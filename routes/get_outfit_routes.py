# routes/get_outfit_routes.py
from flask import render_template, request, jsonify
from routes import outfit_bp
from model.get_outfit_model import generate_outfit
from model.outfit_history_model import add_history_entry   # ✅ NEW IMPORT
from utils.auth import token_required
import requests
import os
from datetime import datetime

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")


# ---------------------------------------------------------
# PAGE RENDER
# ---------------------------------------------------------
@outfit_bp.route("/get_outfit", methods=["GET"])
@token_required
def get_outfit_page(current_user):
    return render_template("get_outfit.html", user=current_user)


# ---------------------------------------------------------
# AUTOCOMPLETE
# ---------------------------------------------------------
@outfit_bp.route("/api/location/autocomplete", methods=["GET"])
@token_required
def autocomplete(current_user):
    query = request.args.get("q", "")

    if not query:
        return jsonify([])

    url = (
        "http://api.openweathermap.org/geo/1.0/direct"
        f"?q={query}&limit=5&appid={OPENWEATHER_API_KEY}"
    )
    results = requests.get(url).json()

    suggestions = []
    for loc in results:
        label = loc.get("name", "")

        if loc.get("state"):
            label += f", {loc['state']}"

        label += f", {loc.get('country', '')}"

        suggestions.append({
            "label": label,
            "lat": loc.get("lat"),
            "lon": loc.get("lon")
        })

    return jsonify(suggestions)


# ---------------------------------------------------------
# REVERSE GEOCODING
# ---------------------------------------------------------
@outfit_bp.route("/api/location/reverse", methods=["GET"])
@token_required
def reverse_geocode(current_user):
    lat = request.args.get("lat")
    lon = request.args.get("lon")

    if not lat or not lon:
        return jsonify({"error": "Missing coordinates"}), 400

    url = (
        "http://api.openweathermap.org/geo/1.0/reverse"
        f"?lat={lat}&lon={lon}&limit=1&appid={OPENWEATHER_API_KEY}"
    )
    result = requests.get(url).json()

    if not result:
        return jsonify({"error": "Location not found"}), 404

    loc = result[0]

    label = loc.get("name", "")

    if loc.get("state"):
        label += f", {loc['state']}"

    label += f", {loc.get('country', '')}"

    return jsonify({
        "label": label,
        "lat": loc.get("lat"),
        "lon": loc.get("lon")
    })


# ---------------------------------------------------------
# GENERATE OUTFIT
# ---------------------------------------------------------
@outfit_bp.route("/api/get_outfit", methods=["POST"])
@token_required
def api_generate_outfit(current_user):
    data = request.get_json()
    lat = data.get("lat")
    lon = data.get("lon")
    occasion = data.get("occasion")

    if not lat or not lon:
        return jsonify({"error": "Missing location"}), 400

    result = generate_outfit(lat, lon, occasion)
    return jsonify(result)


# ---------------------------------------------------------
# SAVE OUTFIT INTO IN-MEMORY MODEL
# ---------------------------------------------------------
@outfit_bp.route("/api/save_outfit", methods=["POST"])
@token_required
def save_outfit(current_user):
    data = request.get_json()

    outfit = data.get("outfit")
    weather = data.get("weather")
    location = data.get("location")
    occasion = data.get("occasion")
    rating = data.get("rating")

    if not outfit or not weather or not location:
        return jsonify({"error": "Missing outfit data"}), 400

    entry = {
        "date": data.get("date") or datetime.now().strftime("%Y-%m-%d"),
        "location": location,
        "weather": weather,
        "outfit": outfit,
        "occasion": occasion,
        "rating": rating,
        "liked": True,
        "mood": occasion  # safe default
    }

    add_history_entry(entry)

    return jsonify({"success": True})
