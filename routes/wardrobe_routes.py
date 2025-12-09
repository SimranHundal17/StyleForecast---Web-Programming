# routes/wardrobe_routes.py

from flask import render_template, request, jsonify
from functools import wraps

# Import blueprint from routes/__init__.py
from routes import wardrobe_bp

# Import Model functions
from model.wardrobe_model import (
    get_all_items,
    get_items_by_filter,
    add_item,
    update_item_status,
    get_item_by_id,
    delete_item as delete_item_model,
)

# Fallback auth decorator (used only if utils.auth is not available)
try:
    from utils.auth import token_required
except ImportError:
    # Simple fake decorator for local testing
    def token_required(f):
        @wraps(f)
        def wrapper(*a, **kw):
            # Pass a dummy user if real auth is missing
            return f(current_user="Guest", *a, **kw)
        return wrapper


@wardrobe_bp.route("/")
@token_required
def wardrobe(current_user):
    """
    Render main wardrobe page (HTML).
    """
    return render_template("wardrobe.html", current_user=current_user)


@wardrobe_bp.route("/data")
@token_required
def wardrobe_data(current_user):
    """
    Return wardrobe items as JSON.    
    """
    filter_value = request.args.get("filter", "all")
    items = get_items_by_filter(filter_value)
    return jsonify(items)


@wardrobe_bp.route("/add-item", methods=["POST"])
@token_required
def add_item_route(current_user):
    """
    Add a new wardrobe item.    
    """
    try:
        # Read form fields from the request
        name = request.form.get("name", "").strip()
        category = request.form.get("category", "Casual")
        status = request.form.get("status", "Clean")
        color = request.form.get("color", "").strip()

        # Name is required
        if not name:
            return jsonify({"error": "Name is required"}), 400

        # Call model function to insert item into MongoDB
        new_item = add_item(name, category, status, color)
        # Return created item and HTTP 201 status
        return jsonify(new_item), 201

    except Exception as e:
        # Print error for debugging and return 500
        print(f"Error adding item: {e}")
        return jsonify({"error": str(e)}), 500


@wardrobe_bp.route("/update", methods=["POST"])
@token_required
def wardrobe_update(current_user):
    """
    Toggle item status Clean <-> Needs Wash.
    Data comes as JSON: {"id": ...}
    """
    try:
        # Read JSON body (or empty dict if no JSON)
        data = request.get_json() or {}
        item_id = data.get("id")

        # id is required to update an item
        if not item_id:
            return jsonify({"error": "ID is required"}), 400

        # Call model function to update status in MongoDB
        updated_item = update_item_status(int(item_id))

        # If item does not exist
        if not updated_item:
            return jsonify({"error": "Item not found"}), 404

        # Return updated item in JSON
        return jsonify({"ok": True, "item": updated_item}), 200

    except Exception as e:
        # Print error for debugging and return 500
        print(f"Error updating item: {e}")
        return jsonify({"error": str(e)}), 500


@wardrobe_bp.route("/api/items/<int:item_id>", methods=["DELETE"])
@token_required
def delete_item_route(current_user, item_id):
    """
    Delete item from wardrobe (and from dirty_items in model).
    """
    try:
        # Call model function to delete item from MongoDB
        ok = delete_item_model(item_id)

        if ok:
            # Successfully deleted
            return jsonify({"ok": True}), 200

        # Item not found in database
        return jsonify({"ok": False, "error": "not found"}), 404

    except Exception as e:
        # Print error for debugging and return 500
        print(f"Error deleting item: {e}")
        return jsonify({"ok": False, "error": str(e)}), 500
