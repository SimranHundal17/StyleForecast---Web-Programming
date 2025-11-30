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


# -----------------------
# LOGIN PAGE (GET)
# -----------------------
#@auth_bp.route('/login', methods=['GET'])
#def login():
    # If already logged in, redirect
#    if "token" in session:
#        try:
#            jwt.decode(session["token"], JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
#            return redirect(url_for("outfit.get_outfit_page"))
#        except:
#            session.clear()

#    return render_template('login.html')

@auth_bp.route('/login', methods=['GET'])
def login():
    # Always show login page, even if there is a token in session
    return render_template('login.html')


# -----------------------
# LOGIN SUBMISSION
# -----------------------
@auth_bp.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email")
    password = request.form.get("password")

    user = verify_user(email, password)

    if user:
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

        return {"success": True, "redirect_url": url_for("wardrobe.wardrobe")}

    return {"success": False, "message": "Invalid email or password"}, 401


# -----------------------
# SIGNUP
# -----------------------
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

    if not all([email, password, confirm, first, last, gender, age, days_dirty]):
        return jsonify({"success": False, "message": "Please fill all fields."}), 400

    if password != confirm:
        return jsonify({"success": False, "message": "Passwords do not match."}), 400

    if get_user_by_email(email):
        return jsonify({"success": False, "message": "Email already registered."}), 400

    new_user = {
        "email": email,
        "password": password,
        "first_name": first,
        "last_name": last,
        "gender": gender,
        "age": int(age),
        "days_until_dirty": int(days_dirty),
    }

    create_user(new_user)

    return jsonify({"success": True, "message": "Account created successfully!"}), 201


# -----------------------
# LOGOUT
# -----------------------
@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
