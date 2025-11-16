# routes/home_routes.py
# Routes for intro page, wardrobe, outfit history, profile and other pages.

from flask import render_template, redirect, request, url_for, jsonify
from routes import home_bp
from model.wardrobe_model import get_all_items, add_item as add_wardrobe_item
from model.outfit_history_model import get_all_history
from model.login_model import get_current_user, update_user

# Try to import token_required decorator (login protection).
try:
    from utils.auth import token_required
except ImportError:
    # Simple fallback stub if auth is not implemented yet.
    from functools import wraps

    def token_required(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Call the original function with fake current_user.
            return f(current_user="Guest", *args, **kwargs)

        return wrapper


# ========== Intro page ==========

@home_bp.route("/intro")
def intro():
    """
    Public intro page, no login required.
    """
    return render_template("index.html")


# ========== Wardrobe page (HTML) ==========

@home_bp.route("/wardrobe")
@token_required
def wardrobe(current_user):
    """
    Wardrobe page - shows all items from wardrobe_model.
    HTML uses items for initial render, JS can also load via /wardrobe/data.
    """
    items = get_all_items()  # list of dicts with clothes
    return render_template("wardrobe.html", items=items, current_user=current_user)


# ========== Add new clothing item (HTML form POST) ==========

@home_bp.route("/add-item", methods=["POST"])
@token_required
def add_item_route(current_user):
    """
    Handle form POST for adding a new clothing item.
    Data comes from wardrobe modal form on wardrobe.html.
    """
    # Read and normalize data from form fields.
    name = (request.form.get("name") or "").strip()
    category = (request.form.get("category") or "Other").strip()
    status = (request.form.get("status") or "Clean").strip()
    occasion = (request.form.get("occasion") or "Casual").strip()
    color = (request.form.get("color") or "Unknown").strip()

    # Do not add items without a name.
    if not name:
        return redirect(url_for("home.wardrobe"))

    # Build dict that matches wardrobe_model structure.
    new_item = {
        "name": name,
        "category": category or "Other",
        "status": status or "Clean",
        "occasion": occasion or "Casual",
        "color": color or "Unknown",
        "wear_count": 0,
    }

    # Use model function to add the item to in-memory list.
    add_wardrobe_item(new_item)

    # After adding - redirect back to wardrobe page.
    return redirect(url_for("home.wardrobe"))


# ========== Outfit history page (HTML) ==========

@home_bp.route("/outfit_history")
@token_required
def outfit_history(current_user):
    """
    Outfit history page - server render using hardcoded history list.
    """
    entries = get_all_history()
    return render_template(
        "outfit_history.html",
        current_user=current_user,
        entries=entries,
    )


@home_bp.route("/history/data")
@token_required
def history_data(current_user):
    """
    Return outfit history as JSON for frontend JS (outfit_history.js).
    """
    return jsonify(get_all_history())


# ========== Profile page (HTML) ==========

@home_bp.route("/profile", methods=["GET", "POST"])
@token_required
def profile(current_user):
    """
    Profile page with simple POST update of name/email.
    Uses in-memory user from login_model.
    """
    user = get_current_user()   # get the current in-memory user

    if request.method == "POST":
        name = (request.form.get("name") or user["name"]).strip()
        email = (request.form.get("email") or user["email"]).strip()

        # Update record (lookup by current email).
        update_user(email=user["email"], data={"name": name, "email": email})

        # Re-read profile after update.
        user = get_current_user()

    return render_template(
        "profile.html",
        current_user=current_user,
        user=user,
    )


# ========== Profile JSON API (for profile.js) ==========

@home_bp.route("/profile/data")
@token_required
def profile_data(current_user):
    """
    Return current profile as JSON for frontend JS.
    Delegates to login_model.get_current_user.
    """
    user = get_current_user()
    return jsonify({
        "name": user.get("name"),
        "email": user.get("email"),
        "style": user.get("style", "Casual"),
        "climate": user.get("climate", "Moderate"),
    })


@home_bp.route("/profile/save", methods=["POST"])
@token_required
def profile_save(current_user):
    """
    Save updated profile info (in-memory via login_model).
    Called by profile.js as JSON API.
    """
    user = get_current_user()
    data = request.get_json(silent=True) or {}

    new_data = {
        "name": data.get("name", user.get("name")),
        "email": data.get("email", user.get("email")),
        "style": data.get("style", user.get("style", "Casual")),
        "climate": data.get("climate", user.get("climate", "Moderate")),
    }

    update_user(email=user["email"], data=new_data)
    return jsonify({"ok": True})


# ==========================
# JSON API for Wardrobe Page
# ==========================

def _icon_for(category: str) -> str:
    """
    Helper: return a suitable emoji for a given clothing category.
    Does not modify the original data.
    """
    cat = (category or "").lower()
    if "shirt" in cat:
        return "👕"
    if "jacket" in cat:
        return "🧥"
    if "pant" in cat or "jean" in cat or "trouser" in cat:
        return "👖"
    if "shoe" in cat or "sneaker" in cat:
        return "👟"
    return "👚"


@home_bp.route("/wardrobe/data")
@token_required
def wardrobe_data(current_user):
    """
    Return wardrobe items as JSON with optional filtering via query params.
    Supported query param:
      - filter: 'all' | 'needs' | 'clean' | category name
        (e.g. 'casual', 'formal', 'gym', 'party', 'outdoor')
    Used by static/wardrobe.js.
    """
    raw = get_all_items()

    # Read filter from query string (e.g., /wardrobe/data?filter=needs).
    f = (request.args.get("filter") or "all").strip().lower()

    # Filter logic (simple, case-insensitive).
    def match(item: dict) -> bool:
        if f in ("all", "", None):
            return True

        status = (item.get("status") or "").lower()
        category = (item.get("category") or "").lower()

        if f in ("needs", "needs wash"):
            return status == "needs wash"
        if f in ("clean",):
            return status == "clean"

        # Treat any other value as a category filter.
        return f in category

    filtered = [it for it in raw if match(it)]

    # Enrich with icon on the fly (do not mutate original).
    enriched = []
    for it in filtered:
        row = dict(it)
        row["icon"] = row.get("icon") or _icon_for(row.get("category"))
        enriched.append(row)

    return jsonify(enriched)


@home_bp.route("/wardrobe/update", methods=["POST"])
@token_required
def wardrobe_update(current_user):
    """
    Switch item status (Clean <-> Needs Wash) by given ID.
    Called by wardrobe.js via fetch POST.
    """
    data = request.get_json(silent=True) or {}
    item_id = data.get("id")

    # Validate and convert id to integer.
    try:
        item_id = int(item_id)
    except (TypeError, ValueError):
        return jsonify({"ok": False, "error": "id must be integer"}), 400

    items = get_all_items()
    for it in items:
        if it.get("id") == item_id:
            status_now = (it.get("status") or "").lower()
            it["status"] = "Needs Wash" if status_now == "clean" else "Clean"
            return jsonify({"ok": True})

    return jsonify({"ok": False, "error": "not found"}), 404


