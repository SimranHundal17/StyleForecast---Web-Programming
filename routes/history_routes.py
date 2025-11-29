# routes/history_routes.py

from flask import render_template, jsonify
from routes import history_bp
from model.outfit_history_model import get_all_history, delete_history_entry

try:
    from utils.auth import token_required
except ImportError:
    from functools import wraps

    def token_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):            
            return f(current_user="Guest", *args, **kwargs)
        return wrapper


@history_bp.route("/")
@token_required
def outfit_history(current_user):
    return render_template("outfit_history.html", current_user=current_user)


@history_bp.route("/data")
@token_required
def history_data(current_user):
    entries = get_all_history()       # <-- now pulling from Mongo
    return jsonify(entries)


@history_bp.route("/api/delete/<int:entry_id>", methods=["DELETE"])
@token_required
def history_delete(current_user, entry_id):
    ok = delete_history_entry(entry_id)
    return jsonify({"ok": ok})