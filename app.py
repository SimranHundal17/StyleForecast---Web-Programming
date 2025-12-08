# app.py
import os
from utils.db import db   # initializes MongoDB one time
from dotenv import load_dotenv
load_dotenv()

from flask import Flask, redirect, url_for

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")

app.config["OPENWEATHER_API_KEY"] =  os.getenv("OPENWEATHER_API_KEY")

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
    return redirect(url_for("intro.intro"))  # blueprint "intro", view-function intro

if __name__ == "__main__":
    app.run(debug=True)

