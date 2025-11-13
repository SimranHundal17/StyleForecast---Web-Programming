from flask import render_template, jsonify
from routes import home_bp
from model.outfit_history_model import get_all_history

try:
    from utils.auth import token_required
except:
    def token_required(f):
        def wrapper(*a, **kw):
            return f(current_user="Guest", *a, **kw)
        return wrapper

@home_bp.route("/outfit_history")
@token_required
def outfit_history(current_user):
    entries = get_all_history()
    return render_template("outfit_history.html", entries=entries, current_user=current_user)

@home_bp.route("/history/data")
@token_required
def history_data(current_user):
    return jsonify(get_all_history())
