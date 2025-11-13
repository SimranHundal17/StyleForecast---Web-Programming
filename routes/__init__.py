# routes/__init__.py
# Create a Blueprint for all "home" pages (intro, wardrobe, history, profile).

from flask import Blueprint

# This blueprint will be registered in app.py as "home".
home_bp = Blueprint("home", __name__)
auth_bp = Blueprint("auth", __name__)
outfit_bp = Blueprint("outfit", __name__)
accessories_bp = Blueprint("accessories", __name__)
plan_bp = Blueprint("plan", __name__)