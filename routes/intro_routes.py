from flask import render_template
from routes import home_bp

@home_bp.route("/intro")
def intro():
    """Public intro page."""
    return render_template("index.html")
