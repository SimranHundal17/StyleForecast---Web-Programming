"""
Authentication routes: login and logout.
"""

from flask import render_template, request, redirect, url_for, session
import jwt
from datetime import datetime, timedelta
from routes import auth_bp
from model.login_model import verify_user, get_all_users
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
    email = request.form.get("email")
    password = request.form.get("password")

    user = verify_user(email, password)

    if user and user["password"] == password:
        # Generate JWT token
        token_payload = {
            "email": user["email"],
            "user_id": user["id"],
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        token = jwt.encode(token_payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

        # 🔧 Ensure token is a string
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        # Store in Flask session
        session["token"] = token
        session["email"] = user["email"]

        return redirect(url_for("outfit.get_outfit_page"))
    else:
        return render_template("login.html", error="Invalid email or password")

@auth_bp.route('/logout')
def logout():
    """
    Logout route that clears session and redirects to login.
    """
    session.pop('token', None)
    session.pop('email', None)
    return redirect(url_for('auth.login'))
