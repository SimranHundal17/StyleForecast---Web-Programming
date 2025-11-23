"""
Authentication routes: login and logout.
"""

from flask import render_template, request, redirect, url_for, session, jsonify
import jwt
from datetime import datetime, timedelta
from routes import auth_bp
from model.login_model import verify_user, get_all_users, find_user_by_email, create_user
from utils.auth import JWT_SECRET_KEY, JWT_ALGORITHM


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


@auth_bp.route("/login", methods=["POST"])
def login_post():
    """
    Handle login POST request.
    """
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

        # Respond with JSON (no redirect)
        return jsonify({"success": True, "redirect_url": url_for("outfit.get_outfit_page")})

    # Invalid credentials → respond with JSON
    return jsonify({"success": False, "message": "Invalid email or password"}), 401


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user from login.js signup mode.
    Returns JSON with success and message.
    """
    email = (request.form.get("email") or "").strip()
    password = (request.form.get("password") or "").strip()
    name = (request.form.get("name") or "").strip()  # сейчас из формы не идёт, но пусть будет

    if not email or not password:
        return jsonify({"success": False, "message": "Email and password are required."}), 400

    # check if user already exists
    if find_user_by_email(email) is not None:
        return jsonify({"success": False, "message": "User with this email already exists."}), 409

    try:
        user = create_user(email=email, password=password, name=name)
    except ValueError as e:
        return jsonify({"success": False, "message": str(e)}), 400

    # тут можно сразу авторизовать, но пока просто даём сообщение
    return jsonify({
        "success": True,
        "message": "Account created. You can now log in.",
    }), 201


@auth_bp.route('/logout')
def logout():
    """
    Logout route that clears session and redirects to login.
    """
    session.pop('token', None)
    session.pop('email', None)
    return redirect(url_for('auth.login'))