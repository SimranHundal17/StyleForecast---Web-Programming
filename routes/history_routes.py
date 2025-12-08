# routes/history_routes.py

from flask import render_template, jsonify, request
from routes import history_bp
from model.outfit_history_model import (
    get_all_history,
    delete_history_entry,
    add_history_entry
)

try:
    from utils.auth import token_required
except ImportError:
    from functools import wraps

    def token_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(current_user="Guest", *args, **kwargs)
        return wrapper


# ---------------------------------------------------------
# PAGE
# ---------------------------------------------------------
@history_bp.route("/")
@token_required
def outfit_history(current_user):
    return render_template("outfit_history.html", current_user=current_user)


# ---------------------------------------------------------
# FETCH ALL HISTORY
# ---------------------------------------------------------
@history_bp.route("/data")
@token_required
def history_data(current_user):
    entries = get_all_history()
    return jsonify(entries)


# ---------------------------------------------------------
# DELETE HISTORY ENTRY
# ---------------------------------------------------------
@history_bp.route("/api/delete/<int:entry_id>", methods=["DELETE"])
@token_required
def history_delete(current_user, entry_id):
    ok = delete_history_entry(entry_id)
    return jsonify({"ok": ok})


# ---------------------------------------------------------
# ADD HISTORY ENTRY (used by Plan Ahead auto-archive)
# ---------------------------------------------------------
@history_bp.route("/api/add_from_plan", methods=["POST"])
@token_required
def history_add_from_plan(current_user):
    """
    Called automatically when a planned date becomes a past date.
    The Plan Ahead JS sends:
        {
            "date": "...",
            "location": "...",
            "weather": "...",
            "outfit": [...],
            "occasion": "...",
            "mood": "",
            "rating": 0,
            "liked": true
        }
    """

    data = request.get_json() or {}

    entry = {
        "date":        data.get("date"),
        "location":    data.get("location", ""),
        "weather":     data.get("weather", ""),   # may include "(temp °C)"
        "outfit":      data.get("outfit", []),
        "occasion":    data.get("occasion", ""),
        "mood":        data.get("mood", ""),
        "rating":      data.get("rating", 0),
        "liked":       data.get("liked", True),   # archived outfits are always "liked"
    }

    new_entry = add_history_entry(entry)
    return jsonify(new_entry), 201
