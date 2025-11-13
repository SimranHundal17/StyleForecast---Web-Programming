from flask import render_template, request, jsonify, redirect, url_for
from routes import home_bp
from model.wardrobe_model import get_all_items, add_item as add_wardrobe_item

# fake auth fallback
try:
    from utils.auth import token_required
except:
    def token_required(f):
        def wrapper(*a, **kw):
            return f(current_user="Guest", *a, **kw)
        return wrapper

# Helper for icons
def _icon_for(category: str) -> str:
    c = (category or "").lower()
    if "shirt" in c: return "👕"
    if "jacket" in c: return "🧥"
    if "pant" in c or "jean" in c or "trouser" in c: return "👖"
    if "shoe" in c or "sneaker" in c: return "👟"
    return "👚"

# Wardrobe page
@home_bp.route("/wardrobe")
@token_required
def wardrobe(current_user):
    items = get_all_items()
    return render_template("wardrobe.html", items=items, current_user=current_user)

# Add Item
@home_bp.route("/add-item", methods=["POST"])
@token_required
def add_item_route(current_user):
    name = request.form.get("name")
    category = request.form.get("category")
    status = request.form.get("status")

    new_item = {
        "name": name,
        "category": category or "Other",
        "status": status or "Clean",
        "occasion": request.form.get("occasion", "Casual"),
        "color": request.form.get("color", "Unknown"),
        "wear_count": 0,
    }

    add_wardrobe_item(new_item)
    return redirect(url_for("home.wardrobe"))

# JSON: get filtered items
@home_bp.route("/wardrobe/data")
@token_required
def wardrobe_data(current_user):
    f = (request.args.get("filter") or "all").lower()
    raw = get_all_items()

    def match(it):
        status = (it.get("status") or "").lower()
        category = (it.get("category") or "").lower()

        if f in ("all", ""): return True
        if f in ("needs", "needs wash"): return status == "needs wash"
        if f == "clean": return status == "clean"
        return f in category

    enriched = []
    for item in raw:
        if match(item):
            row = dict(item)
            row["icon"] = row.get("icon") or _icon_for(row.get("category"))
            enriched.append(row)

    return jsonify(enriched)

# JSON: toggle status
@home_bp.route("/wardrobe/update", methods=["POST"])
@token_required
def wardrobe_update(current_user):
    data = request.get_json() or {}
    item_id = data.get("id")
    if not item_id:
        return jsonify({"ok": False, "error": "id required"}), 400

    for it in get_all_items():
        if it.get("id") == int(item_id):
            it["status"] = "Needs Wash" if it["status"] == "Clean" else "Clean"
            return jsonify({"ok": True})

    return jsonify({"ok": False, "error": "not found"}), 404
