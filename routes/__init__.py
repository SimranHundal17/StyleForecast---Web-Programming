# routes/__init__.py
# Create a Blueprint for all "home" pages (intro, wardrobe, history, profile).

from flask import Blueprint

# This blueprint will be registered in app.py as "home".
home_bp = Blueprint("home", __name__)
