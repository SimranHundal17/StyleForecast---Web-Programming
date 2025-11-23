# routes/profile_routes.py
# Routes for profile page (HTML + JSON API for profile.js)

from flask import render_template, request, jsonify
from routes import profile_bp
from model.login_model import get_current_user, update_user

# Try real auth, otherwise use simple stub
try:
    from utils.auth import token_required
except ImportError:
    from functools import wraps

    def token_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Call the original function with a fake current_user
            return f(current_user="Guest", *args, **kwargs)
        return wrapper


# ========== Profile page (HTML) ==========

@profile_bp.route("/profile", methods=["GET", "POST"])
@token_required
def profile(current_user):
    """
    Profile page with simple POST update of name/email.
    Uses in-memory user from model.login_model.
    """
    user = get_current_user()  # current in-memory user dict

    if request.method == "POST":
        name = (request.form.get("name") or user.get("name", "")).strip()
        email = (request.form.get("email") or user.get("email", "")).strip()

        # Update record (look up by current email)
        update_user(email=user["email"], data={"name": name, "email": email})

        # Re-read profile after update so we show fresh values
        user = get_current_user()

    return render_template(
        "profile.html",
        current_user=current_user,
        user=user,
    )


# ========== Profile JSON API (for static/profile.js) ==========

@profile_bp.route("/profile/data")
@token_required
def profile_data(current_user):
    """
    Return current profile as JSON for frontend JS (profile.js).
    """
    user = get_current_user()
    return jsonify({
        "name": user.get("name"),
        "email": user.get("email"),
        "style": user.get("style", "Casual"),
        "climate": user.get("climate", "Moderate"),
    })


@profile_bp.route("/profile/save", methods=["POST"])
@token_required
def profile_save(current_user):
    """
    Save updated profile info (in-memory via login_model).
    Called by profile.js as a JSON API.
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    new_data = {
        "name": data.get("name", user.get("name")),
        "email": data.get("email", user.get("email")),
        "style": data.get("style", user.get("style", "Casual")),
        "climate": data.get("climate", user.get("climate", "Moderate")),
    }

    update_user(email=user["email"], data=new_data)
    return jsonify({"ok": True})
