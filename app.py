# app.py

from flask import Flask
from routes.home_routes import home_bp
from routes.auth_routes import auth_bp
from routes.get_outfit_routes import outfit_bp
from routes.accessories_routes import accessories_bp
from routes.plan_ahead_routes import plan_bp

# Create Flask app
app = Flask(__name__)
app.secret_key = "your-flask-secret-key"

# Register the "home" blueprint with all pages (intro, wardrobe, etc.)
app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(outfit_bp)
app.register_blueprint(accessories_bp)
app.register_blueprint(plan_bp)

# Root route – just redirect to /intro
@app.route("/")
def index_redirect():
    from flask import redirect, url_for
    return redirect(url_for("home.intro"))


# Run Flask app (development mode)
if __name__ == "__main__":
    app.run(debug=True)
