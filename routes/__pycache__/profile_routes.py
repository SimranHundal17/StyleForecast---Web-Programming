from flask import render_template, jsonify, request
from routes import home_bp
from model.login_model import get_current_user, update_user

try:
    from utils.auth import token_required
except:
    def token_required(f):
        def wrapper(*a, **kw):
            return f(current_user="Guest", *a, **kw)
        return wrapper

# In-memory profile
_profile = {
    "name": "Jane Doe",
    "email": "jane@example.com",
    "style": "Casual",
    "climate": "Moderate",
}

@home_bp.route("/profile", methods=["GET", "POST"])
@token_required
def profile(current_user):
    user = get_current_user()

    if request.method == "POST":
        update_user(
            email=user["email"],
            data={
                "name": request.form.get("name"),
                "email": request.form.get("email")
            }
        )
        user = get_current_user()

    return render_template("profile.html", current_user=current_user, user=user)

@home_bp.route("/profile/data")
@token_required
def profile_data(current_user):
    return jsonify(_profile)

@home_bp.route("/profile/save", methods=["POST"])
@token_required
def profile_save(current_user):
    data = request.get_json() or {}
    _profile.update(data)
    return jsonify({"ok": True})
