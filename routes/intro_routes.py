"""
============================================================
routes/intro_routes.py — Public landing page routes
============================================================

Purpose:
- This file defines routes for the public intro (landing) page.
- It is the entry point of the application for non-authenticated users.

What this file does:
- Renders the main landing page (index.html).
- Does NOT require authentication.
- Does NOT interact with the database or user data.

Key concepts (exam notes):
- This route is public and accessible to everyone.
- It uses a Flask Blueprint to keep routes modular.
- The intro page explains what the app does and provides
  navigation to login / signup.

Typical flow:
1. User opens the root URL ("/").
2. app.py redirects the user to "/intro".
3. This route renders index.html.
"""

## Routes for the public landing (intro) page
from flask import render_template
from routes import intro_bp

# Render landing page (public page, no authentication)
@intro_bp.route("/intro")
def intro():
    return render_template("index.html")
