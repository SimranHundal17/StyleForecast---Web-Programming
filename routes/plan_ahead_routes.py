from flask import Blueprint, render_template, request, jsonify, current_app
from datetime import datetime
import requests
import traceback

from model.plan_ahead_model import (
    serialize_plan, get_all_plans, get_plan_by_id,
    get_plans_for_date, add_plan_entry, add_plan_range,
    update_plan, delete_plan, delete_group, archive_past_plans
)

plan_bp = Blueprint("plan", __name__)

@plan_bp.route("/plan_ahead")
def plan_ahead_page():
    return render_template("plan_ahead.html")

@plan_bp.route("/plan/plans")
def api_plans():
    try:
        archive_past_plans()
        plans = get_all_plans()
        return jsonify([serialize_plan(p) for p in plans])
    except:
        traceback.print_exc()
        return jsonify([])

@plan_bp.route("/plan/create", methods=["POST"])
def api_create():
    try:
        data = request.json
        start = data["start"]
        end = data.get("end", start)

        base = {
            "location": data.get("location", ""),
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "occasion": data.get("occasion", "Casual"),
            "weather": data.get("weather", ""),
            "temp": data.get("temp"),
            "description": data.get("description"),
            "outfit": []
        }

        created = add_plan_range(start, end, base)
        return jsonify([serialize_plan(c) for c in created]), 201

    except:
        traceback.print_exc()
        return jsonify({"error": "failed"}), 500

@plan_bp.route("/plan/update", methods=["POST"])
def api_update():
    try:
        data = request.json
        pid = data["id"]

        allowed = ["location", "lat", "lon", "occasion",
                   "weather", "temp", "description", "outfit"]

        update_fields = {k: data[k] for k in allowed if k in data}

        updated = update_plan(pid, **update_fields)
        return jsonify(serialize_plan(updated))

    except:
        traceback.print_exc()
        return jsonify({"error": "failed"}), 500

@plan_bp.route("/plan/delete", methods=["POST"])
def api_delete():
    try:
        delete_plan(request.json["id"])
        return jsonify({"success": True})
    except:
        traceback.print_exc()
        return jsonify({"success": False})

@plan_bp.route("/plan/delete_group", methods=["POST"])
def api_delete_group():
    try:
        delete_group(request.json["group_id"])
        return jsonify({"success": True})
    except:
        traceback.print_exc()
        return jsonify({"success": False})

@plan_bp.route("/plan_ahead/api/weather_for_date")
def weather_for_date():
    try:
        lat = request.args["lat"]
        lon = request.args["lon"]
        date_str = request.args["date"]

        key = current_app.config["OPENWEATHER_API_KEY"]

        url = (
            f"https://api.openweathermap.org/data/2.5/forecast?"
            f"lat={lat}&lon={lon}&units=metric&appid={key}"
        )

        r = requests.get(url).json()
        if "list" not in r:
            return jsonify({"error": "Weather unavailable"}), 500

        target = datetime.strptime(date_str, "%Y-%m-%d").date()

        for e in r["list"]:
            dt = datetime.strptime(e["dt_txt"], "%Y-%m-%d %H:%M:%S").date()
            if dt == target:
                return jsonify({
                    "weather": e["weather"][0]["main"],
                    "description": e["weather"][0]["description"],
                    "temp": e["main"]["temp"]
                })

        return jsonify({"error": "Weather not available"}), 404

    except:
        traceback.print_exc()
        return jsonify({"error": "failed"}), 500
    