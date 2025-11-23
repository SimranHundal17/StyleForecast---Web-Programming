"""
Authentication routes: login, signup, and logout.
"""

from flask import render_template, request, redirect, url_for, session, jsonify
import jwt
from datetime import datetime, timedelta
from routes import auth_bp
from model.login_model import (
    verify_user,
    get_all_users,
    create_user,
    get_user_by_email
)
from utils.auth import JWT_SECRET_KEY, JWT_ALGORITHM


# ---------------------------------------
# LOGIN PAGE (GET)
# ---------------------------------------
@auth_bp.route('/login', methods=['GET'])
def login():
    """
    GET route to display the login page.
    """
    # If already logged in → redirect to homepage
    if 'token' in session:
        try:
            jwt.decode(session['token'], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return redirect(url_for('outfit.get_outfit_page'))
        except:
            session.pop('token', None)

    return render_template('login.html', users=get_all_users())


# ---------------------------------------
# LOGIN SUBMISSION (POST)
# ---------------------------------------
@auth_bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    user = verify_user(email, password)

    # Verify user exists and password matches
    if user and user["password"] == password:
        token_payload = {
            "email": user["email"],
            "user_id": user["id"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        }

        token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        session["token"] = token
        session["email"] = user["email"]

        # Respond with JSON instead of redirect
        return {"success": True, "redirect_url": url_for("outfit.get_outfit_page")}

    # Invalid credentials
    return {"success": False, "message": "Invalid email or password"}, 401


# ---------------------------------------
# LOGOUT
# ---------------------------------------
@auth_bp.route('/logout')
def logout():
    """
    Logout route that clears session and redirects to login.
    """
    session.pop('token', None)
    session.pop('email', None)
    return redirect(url_for('auth.login'))


# ---------------------------------------
# REAL SIGNUP (POST)
# ---------------------------------------
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data = request.json

    email = data.get("email")
    password = data.get("password")
    confirm = data.get("confirm_password")
    first = data.get("first_name")
    last = data.get("last_name")
    gender = data.get("gender")
    age = data.get("age")
    days_dirty = data.get("days_until_dirty")

    # Check required fields
    if not all([email, password, confirm, first, last, gender, age, days_dirty]):
        return jsonify({"success": False, "message": "Please fill all fields."}), 400

    if password != confirm:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400

    # Check if email already exists
    if get_user_by_email(email):
        return jsonify({"success": False, "message": "Email already registered."}), 400

    # Create the new user
    new_user = {
        "email": email,
        "password": password,  # (Password hashing can be added later)
        "first_name": first,
        "last_name": last,
        "gender": gender,
        "age": int(age),
        "days_until_dirty": int(days_dirty)
    }

    created = create_user(new_user)

    if created is None:
        return jsonify({"success": False, "message": "Unable to create user."}), 500

    return jsonify({"success": True, "message": "Account created successfully!"}), 201
