from flask import Blueprint, render_template, request, jsonify, current_app
from routes import plan_bp  # make sure in routes/__init__.py you exported plan_bp = Blueprint('plan', __name__)
from model.plan_ahead_model import (
    get_all_plans,
    get_plans_for_date,
    add_plan_entry,
    add_plan_range,
    update_plan,
    update_plan_rating,
    delete_plan,
    delete_group
)
from model.get_outfit_model import generate_outfit
import traceback
import requests
from datetime import datetime, timezone

# token_required fallback
try:
    from utils.auth import token_required
except Exception:
    def token_required(f):
        def wrapper(*a, **kw):
            return f(current_user="Guest", *a, **kw)
        wrapper.__name__ = f.__name__
        return wrapper

@plan_bp.route("/plan_ahead")
@token_required
def plan_ahead_page(current_user):
    """
    Render Plan Ahead UI. Frontend JS will interact with API endpoints below.
    """
    return render_template("plan_ahead.html", user=current_user)


# list all plans
@plan_bp.route("/plan/plans", methods=["GET"])
@token_required
def api_get_plans(current_user):
    return jsonify(get_all_plans())


# get plans for a single date (YYYY-MM-DD)
@plan_bp.route("/plan/for_date", methods=["GET"])
@token_required
def api_get_for_date(current_user):
    date = request.args.get("date")
    if not date:
        return jsonify([]), 400
    return jsonify(get_plans_for_date(date))


# create plan(s)
@plan_bp.route("/plan/create", methods=["POST"])
@token_required
def api_create_plans(current_user):
    data = request.get_json() or {}
    start = data.get("start")
    end = data.get("end") or start
    location = data.get("location", "")
    lat = data.get("lat")
    lon = data.get("lon")
    occasion = data.get("occasion", "Casual")
    weather_override = data.get("weather")

    if not start:
        return jsonify({"error": "start date required"}), 400

    base = {
        "location": location,
        "lat": lat,
        "lon": lon,
        "occasion": occasion,
        "weather": weather_override or "",
        "outfit": [],
        "liked": False,
        "rating": None
    }

    try:
        created = add_plan_range(start, end, base)
        # try to generate outfit for each entry if lat/lon provided
        for c in created:
            try:
                if c.get("lat") and c.get("lon"):
                    res = generate_outfit(c["lat"], c["lon"], c["occasion"])
                    if not res.get("error"):
                        c["weather"] = res.get("weather", "")
                        c["outfit"] = res.get("outfit", [])
            except Exception:
                pass
        return jsonify(created), 201
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "could not create plans"}), 500


# update a single plan (fields)
@plan_bp.route("/plan/update", methods=["POST"])
@token_required
def api_update_plan(current_user):
    data = request.get_json() or {}
    pid = data.get("id")
    if not pid:
        return jsonify({"error": "id required"}), 400
    allowed = {}
    for key in ("location", "lat", "lon", "occasion", "weather", "outfit"):
        if key in data:
            allowed[key] = data[key]
    updated = update_plan(pid, **allowed)
    if not updated:
        return jsonify({"error": "not found"}), 404
    return jsonify(updated)


# rate / like single plan
@plan_bp.route("/plan/rate", methods=["POST"])
@token_required
def api_rate_plan(current_user):
    data = request.get_json() or {}
    pid = data.get("id")
    rating = data.get("rating")
    liked = data.get("liked")
    if not pid:
        return jsonify({"error": "id required"}), 400
    updated = update_plan_rating(pid, rating=rating, liked=liked)
    if not updated:
        return jsonify({"error": "not found"}), 404
    return jsonify(updated)


# delete single plan
@plan_bp.route("/plan/delete", methods=["POST"])
@token_required
def api_delete_plan(current_user):
    data = request.get_json() or {}
    pid = data.get("id")
    if not pid:
        return jsonify({"error": "id required"}), 400
    success = delete_plan(pid)
    if not success:
        return jsonify({"error": "not found"}), 404
    return jsonify({"success": True})


# delete whole group (range)
@plan_bp.route("/plan/delete_group", methods=["POST"])
@token_required
def api_delete_group(current_user):
    data = request.get_json() or {}
    gid = data.get("group_id")
    if not gid:
        return jsonify({"error": "group_id required"}), 400
    delete_group(gid)
    return jsonify({"success": True})


# NEW: get weather for a specific date
@plan_bp.route("/api/weather_for_date", methods=["GET"])
@token_required
def api_weather_for_date(current_user):
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    date_str = request.args.get("date")
    if not lat or not lon or not date_str:
        return jsonify({"error": "lat, lon and date required"}), 400

    try:
        target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
        today = datetime.now(timezone.utc).date()

        OPENWEATHER_API_KEY = current_app.config.get("OPENWEATHER_API_KEY")
        if not OPENWEATHER_API_KEY:
            return jsonify({"error": "OpenWeather API key not configured"}), 500

        url = f"https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&exclude=minutely,hourly,alerts&units=metric&appid={OPENWEATHER_API_KEY}"
        resp = requests.get(url)
        data = resp.json()

        if "daily" not in data:
            return jsonify({"error": "Weather data unavailable"}), 500

        weather_for_date = None
        for day in data["daily"]:
            day_date = datetime.fromtimestamp(day["dt"], tz=timezone.utc).date()
            if day_date == target_date:
                weather_for_date = day["weather"][0]["main"]
                break

        if not weather_for_date:
            return jsonify({"error": "Weather not available for this date"}), 404

        return jsonify({"weather": weather_for_date})
    except Exception:
        traceback.print_exc()
        return jsonify({"error": "Error fetching weather"}), 500
