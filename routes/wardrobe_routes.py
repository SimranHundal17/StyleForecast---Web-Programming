# routes/wardrobe_routes.py

from flask import render_template, request, jsonify
from functools import wraps

# Import blueprint from routes/__init__.py
from routes import wardrobe_bp

# Import model functions
from model.wardrobe_model import (
    get_all_items,
    get_items_by_filter,
    add_item,
    update_item_status,
    get_item_by_id
)

# Fake auth fallback
try:
    from utils.auth import token_required
except ImportError:
    def token_required(f):
        @wraps(f)
        def wrapper(*a, **kw):
            return f(current_user="Guest", *a, **kw)
        return wrapper


@wardrobe_bp.route("/")
@token_required
def wardrobe(current_user):
    """Render wardrobe page."""
    return render_template("wardrobe.html", current_user=current_user)


@wardrobe_bp.route("/data")
@token_required
def wardrobe_data(current_user):
    """API endpoint to get filtered wardrobe items."""
    filter_value = request.args.get("filter", "all")
    items = get_items_by_filter(filter_value)
    return jsonify(items)


@wardrobe_bp.route("/add-item", methods=["POST"])
@token_required
def add_item_route(current_user):
    """Add a new wardrobe item."""
    try:
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "Casual")
        status = request.form.get("status", "Clean")
        color = request.form.get("color", "").strip()
        
        if not name:
            return jsonify({"error": "Name is required"}), 400
        
        new_item = add_item(name, category, status, color)
        return jsonify(new_item), 201
        
    except Exception as e:
        print(f"Error adding item: {e}")
        return jsonify({"error": str(e)}), 500


@wardrobe_bp.route("/update", methods=["POST"])
@token_required
def wardrobe_update(current_user):
    """Toggle item status between Clean and Needs Wash."""
    try:
        data = request.get_json()
        item_id = data.get("id")
        
        if not item_id:
            return jsonify({"error": "ID is required"}), 400
        
        updated_item = update_item_status(int(item_id))
        
        if not updated_item:
            return jsonify({"error": "Item not found"}), 404
        
        return jsonify({"ok": True, "item": updated_item}), 200
        
    except Exception as e:
        print(f"Error updating item: {e}")
        return jsonify({"error": str(e)}), 500
    
@wardrobe_bp.route("/api/items/<int:item_id>", methods=["DELETE"])
@token_required
def delete_item(current_user, item_id):
    """
    Delete wardrobe item by ID (in-memory).
    Used by wardrobe.js via fetch DELETE.
    """
    items = get_all_items()

    # We modify the list in-place so change persists in memory
    for idx, it in enumerate(items):
        if it.get("id") == item_id:
            del items[idx]
            return jsonify({"ok": True})

    return jsonify({"ok": False, "error": "not found"}), 404
