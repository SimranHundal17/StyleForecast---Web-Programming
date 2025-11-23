from flask import render_template
from routes import intro_bp

# no auth needed for intro page
@intro_bp.route("/intro")
def intro():
    return render_template("index.html")

