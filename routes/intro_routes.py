from flask import render_template
from routes import intro_bp

# Intro page route
@intro_bp.route("/intro")
def intro():
    return render_template("index.html")
