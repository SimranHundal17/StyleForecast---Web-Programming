# app.py

from flask import Flask
from routes.home_routes import home_bp

# Create Flask app
app = Flask(__name__)

# Register the "home" blueprint with all pages (intro, wardrobe, etc.)
app.register_blueprint(home_bp)

# Secret key (needed if you use sessions/forms later)
app.config["SECRET_KEY"] = "our_secret_key_to_local_dev"

# Root route – just redirect to /intro
@app.route("/")
def index_redirect():
    from flask import redirect, url_for
    return redirect(url_for("home.intro"))


# Run Flask app (development mode)
if __name__ == "__main__":
    app.run(debug=True)
