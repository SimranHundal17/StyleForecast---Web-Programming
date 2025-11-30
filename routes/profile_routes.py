from flask import render_template, request, jsonify
from routes import profile_bp
from utils.auth import token_required
from model.login_model import get_user_by_email
from utils.db import db

users = db["users"]


@profile_bp.route("/", methods=["GET"])
@token_required
def profile(current_user):
    user = get_user_by_email(current_user)

    if not user:
        return "User not found", 404

    return render_template("profile.html", user=user)

@profile_bp.route("/data", methods=["GET"])
@token_required
def profile_data(current_user):
    """Return current user data as JSON for profile.js."""
    user = get_user_by_email(current_user)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # user from Mongo is a dict, we safely pick only needed fields
    first_name = user.get("first_name", "")
    last_name = user.get("last_name", "")
    full_name = (first_name + " " + last_name).strip() or user.get("name", "")

    return jsonify({
        "name": full_name,
        "email": user.get("email", ""),
        "first_name": first_name,
        "last_name": last_name,
        "gender": user.get("gender", ""),
        "age": user.get("age", ""),
        "days_until_dirty": user.get("days_until_dirty", "")
    })

@profile_bp.route("/update", methods=["POST"])
@token_required
def profile_update(current_user):
    """Update profile fields for current user (no password hashing)."""
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    update_data = {}

    # Basic profile fields
    for key in ["first_name", "last_name", "gender", "age", "days_until_dirty"]:
        if key in data:
            update_data[key] = data[key]

    # Handle password change
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if password or confirm_password:
        # Both fields must be present
        if not password or not confirm_password:
            return jsonify({
                "success": False,
                "message": "Both password and confirm_password are required"
            }), 400

        if password != confirm_password:
            return jsonify({
                "success": False,
                "message": "Passwords do not match"
            }), 400

        # Store password
        update_data["password"] = password

    # Apply update in Mongo
    users.update_one({"email": current_user}, {"$set": update_data})

    return jsonify({"success": True, "message": "Profile updated successfully"})
