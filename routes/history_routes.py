# routes/history_routes.py
# All routes related to outfit history (HTML + JSON API).

from flask import render_template, jsonify
from routes import home_bp
from model.outfit_history_model import get_all_history

try:
    from utils.auth import token_required
except ImportError:
    from functools import wraps

    def token_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):            
            return f(current_user="Guest", *args, **kwargs)
        return wrapper


@home_bp.route("/outfit_history")
@token_required
def outfit_history(current_user):
    """Render Outfit History page using hardcoded list."""
    entries = get_all_history()
    return render_template(
        "outfit_history.html",
        entries=entries,
        current_user=current_user,
    )


@home_bp.route("/history/data")
@token_required
def history_data(current_user):
    """Return outfit history as JSON for outfit_history.js."""
    return jsonify(get_all_history())
