# app.py
"""
StyleForecast - Flask Web Application Entry Point

Core responsibilities:
1. Load environment variables from .env (API keys, JWT secret, etc.)
2. Initialize Flask app and MongoDB database
3. Register all route blueprints (intro, auth, wardrobe, etc.)
4. Configure app settings (SECRET_KEY, API keys)
5. Define root route that redirects to intro page

Architecture:
- Models (model/): Business logic and database operations
- Routes (routes/): HTTP endpoints organized by feature (blueprints)
- Utils (utils/): Shared utilities (auth, database connection)
- Static (static/): CSS, JavaScript, and frontend assets
- Templates (templates/): HTML pages with Flask/Jinja2

Key Integrations:
- MongoDB: Database for user data, wardrobe, accessories, history
- JWT: Authentication tokens stored in session
- Groq API: LLM for outfit generation
- OpenWeather API: Weather data for location-based outfit suggestions
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file FIRST, before importing anything that needs them.
# Use an explicit path (relative to this file) so it works even if the app is
# started from a different working directory.
# Use override=True so local dev uses the values in this repo even if Windows/User
# env vars contain stale values (common source of Groq 401 invalid_api_key confusion).
_HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(dotenv_path=os.path.join(_HERE, ".env"), override=True)

# Now import db after env vars are loaded
from utils.db import db   # initializes MongoDB connection

from flask import Flask, redirect, url_for  # Flask framework and redirect utilities

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

# Store API key in Flask config for use in routes
app.config["OPENWEATHER_API_KEY"] = os.getenv("OPENWEATHER_API_KEY")

# =====================================================
# REGISTER ROUTE BLUEPRINTS
# =====================================================
# Each blueprint handles a specific feature area:
# - intro: Landing page and app overview
# - auth: Login, signup, JWT token management
# - wardrobe: User clothing item management
# - get_outfit: Single-day outfit generation
# - accessories: Optional accessory management
# - plan_ahead: Multi-day outfit planning
# - history: Saved outfit history and statistics
# - profile: User profile and preferences

from routes.intro_routes import intro_bp
from routes.auth_routes import auth_bp
from routes.wardrobe_routes import wardrobe_bp
from routes.get_outfit_routes import outfit_bp
from routes.history_routes import history_bp
from routes.accessories_routes import accessories_bp
from routes.plan_ahead_routes import plan_bp
from routes.profile_routes import profile_bp

# Register blueprints
app.register_blueprint(intro_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(wardrobe_bp)
app.register_blueprint(outfit_bp)
app.register_blueprint(history_bp)
app.register_blueprint(accessories_bp)
app.register_blueprint(plan_bp)
app.register_blueprint(profile_bp)

# Root route – redirect to intro page
@app.route("/")
def index_redirect():
    """
    Redirect root path to intro page.
    
    Blueprint: "intro", view-function: "intro"
    """
    return redirect(url_for("intro.intro"))

# =====================================================
# RUN THE APPLICATION
# =====================================================
if __name__ == "__main__":
    app.run(debug=True)