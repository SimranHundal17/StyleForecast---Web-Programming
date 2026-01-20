"""
============================================================
routes/profile_routes.py — User profile routes
============================================================

Purpose:
- This file handles everything related to the user profile.
- It renders the Profile page and provides JSON APIs for frontend updates.

What this file does:
- Shows the profile page for the logged-in user.
- Returns user profile data as JSON for profile.js.
- Allows the user to update profile information.
- Handles optional password changes securely.

Key concepts (exam notes):
- All routes are protected with token_required (JWT authentication).
- current_user is extracted from the JWT token and represents the user email.
- Passwords are never stored in plain text — bcrypt is used for hashing.
- Only allowed fields are updated to prevent accidental or unsafe changes.

Typical flow:
1. User opens the Profile page.
2. JWT token is validated.
3. Backend loads user data from MongoDB.
4. Profile page is rendered with existing user data.
5. Frontend can request or update profile data via JSON APIs.
"""

## Profile routes: render HTML page and provide JSON APIs for profile.js
from flask import render_template, request, jsonify
from routes import profile_bp
from utils.auth import token_required   # to protect routes with JWT
from model.login_model import get_user_by_email   # search user by email in MongoDB
from utils.db import db
import bcrypt   # for password hashing

# MongoDB collection for users
users = db["users"]

# Create profile page for the current user
@profile_bp.route("/", methods=["GET"])
@token_required
def profile(current_user):
# current_user is email from JWT token
    user = get_user_by_email(current_user)

    if not user:
        return "User not found", 404

    return render_template("profile.html", user=user)

# JSON API to get current user profile data
@profile_bp.route("/data", methods=["GET"])
@token_required
def profile_data(current_user):
# Return current user data as JSON for profile.js
    user = get_user_by_email(current_user)
    if not user:
        return jsonify({"error": "User not found"}), 404

# Safely pick only needed fields
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

# JSON API to update current user profile data
## If password is provided, it is hashed with bcrypt before storing. 
@profile_bp.route("/update", methods=["POST"])
@token_required
def profile_update(current_user):
    data = request.get_json()

    if not data:
        return jsonify({"success": False, "message": "No data received"}), 400

    update_data = {}

# Basic profile fields (non-sensitive)
    for key in ["first_name", "last_name", "gender", "age", "days_until_dirty"]:
        if key in data:
            update_data[key] = data[key]

# Handle password change (optional)
    password = data.get("password")
    confirm_password = data.get("confirm_password")

    if password or confirm_password:
# Both fields must be present
        if not password or not confirm_password:
            return jsonify({
                "success": False,
                "message": "Both password and confirm_password are required"
            }), 400
# Passwords must match
        if password != confirm_password:
            return jsonify({
                "success": False,
                "message": "Passwords do not match"
            }), 400

# Hash new password with bcrypt (salt is included in the hash)
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        update_data["password"] = hashed.decode("utf-8")

# Apply update in Mongo
    users.update_one({"email": current_user}, {"$set": update_data})

    return jsonify({"success": True, "message": "Profile updated successfully"})
