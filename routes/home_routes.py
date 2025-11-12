# routes/home_routes.py
# Routes for intro page, wardrobe, outfit history, profile and other pages.

from flask import render_template, redirect, request, url_for
from routes import home_bp
from model.wardrobe_model import get_all_items, add_item as add_wardrobe_item
from model.outfit_history_model import get_all_history
from model.login_model import get_current_user, update_user

# Try to import token_required decorator (login protection).
try:
    from utils.auth import token_required
except ImportError:
    # Fallback: simple stub if auth is not implemented yet.
    def token_required(f):
        def wrapper(*args, **kwargs):
            # Call the original function with fake current_user.
            return f(current_user="Guest", *args, **kwargs)

        wrapper.__name__ = f.__name__
        return wrapper


# ========== Intro page ==========

@home_bp.route("/intro")
def intro():
    """
    Public intro page, no login required.
    """
    return render_template("index.html")


# ========== Wardrobe page ==========

@home_bp.route("/wardrobe")
@token_required
def wardrobe(current_user):
    """
    Wardrobe page - shows all items from wardrobe_model.
    """
    items = get_all_items()  # list of dicts with clothes
    return render_template("wardrobe.html", items=items, current_user=current_user)


# ========== Add new clothing item ==========

@home_bp.route("/add-item", methods=["POST"])
@token_required
def add_item_route(current_user):
    """
    Handle form POST for adding a new clothing item.
    """
    # Read data from form fields (name/category/status).
    name = request.form.get("name")
    category = request.form.get("category")
    status = request.form.get("status")

    # Optional extra fields (if you add them later in HTML).
    occasion = request.form.get("occasion", "Casual")
    color = request.form.get("color", "Unknown")

    # Build dict that matches wardrobe_model structure.
    new_item = {
        "name": name,
        "category": category or "Other",
        "status": status or "Clean",
        "occasion": occasion,
        "color": color,
        "wear_count": 0,
    }

    # Use model function to add the item to in-memory list.
    add_wardrobe_item(new_item)

    # After adding – redirect back to wardrobe page.
    return redirect(url_for("home.wardrobe"))


# ========== Outfit history page ==========

@home_bp.route("/outfit_history")
@token_required
def outfit_history(current_user):
    """ Outfit history page. """
    entires = get_all_history()
    return render_template("outfit_history.html", current_user=current_user, entires=entires)


# ========== Profile page ==========

@home_bp.route("/profile", methods=["GET", "POST"])
@token_required
def profile(current_user):
    """Profile page with simple POST update of name/email."""
    user = get_current_user()   # берём «текущего» пользователя из in-memory

    if request.method == "POST":
        name  = request.form.get("name")  or user["name"]
        email = request.form.get("email") or user["email"]

        # Обновляем запись (по текущему email)
        update_user(email=user["email"], data={"name": name, "email": email})

        # перечитываем профиль после апдейта
        user = get_current_user()

    return render_template(
        "profile.html",
        current_user=current_user,
        user=user,
    )

# ========== Accessories page ==========

@home_bp.route("/accessories")
def accessories():
    """
    Accessories page for now just renders accessories.html template.
    """
    return render_template("accessories.html")

# ========== Login page ==========

@home_bp.route("/login")
def login():
    """
    Temporary login page route (just renders login.html).
    """
    return render_template("login.html")

# ========== Get Outfit page ==========

@home_bp.route("/get-outfit")
def get_outfit():
    """
    Get Outfit page for now just renders get_outfit.html template.
    """
    return render_template("get_outfit.html")


# ========== Plan Ahead page ==========

@home_bp.route("/plan-ahead")
def plan_ahead():
    """
    Plan Ahead page for now just renders plan_ahead.html template.
    """
    return render_template("plan_ahead.html")
