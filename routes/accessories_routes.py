"""
accessories_routes.py

This file defines all Flask routes related to accessories.
It connects HTTP requests from the frontend to the accessories model
and ensures that only authenticated users can access these routes.
"""

from flask import render_template, jsonify, request
from routes import accessories_bp
from model.accessories_model import get_all_accessories, add_accessory, remove_accessory, update_accessory
from utils.auth import token_required


@accessories_bp.route('/', methods=['GET'])
@token_required
def accessories_page(current_user):
    """
    Render the accessories page UI.
    Accessible only to logged-in users.
    """
    return render_template('accessories.html')


@accessories_bp.route('/api/accessories', methods=['GET'])
@token_required
def api_get_accessories(current_user):
    """
    API endpoint to fetch all accessories.
    Returns data in JSON format for frontend usage.
    Only returns accessories for the current user.
    """
    return jsonify(get_all_accessories(current_user))


@accessories_bp.route('/api/accessories', methods=['POST'])
@token_required
def api_add_accessory(current_user):
    """
    API endpoint to add a new accessory.
    Expects accessory data in JSON format.
    Accessory will be associated with current user.
    """
    data = request.get_json()
    return jsonify(add_accessory(data["name"], data["type"], current_user)), 201


@accessories_bp.route('/api/accessories/<accessory_id>', methods=['DELETE'])
@token_required
def api_delete_accessory(current_user, accessory_id):
    """
    API endpoint to delete an accessory using its ID.
    Only deletes if accessory belongs to current user.
    """
    remove_accessory(accessory_id, current_user)
    return jsonify({"success": True})


@accessories_bp.route('/api/accessories/<accessory_id>', methods=['POST'])
@token_required
def api_update_accessory(current_user, accessory_id):
    """Update an accessory (name/type). Expects JSON body with 'name' and/or 'type'."""
    data = request.get_json() or {}
    name = data.get('name')
    type_ = data.get('type')
    if name is None and type_ is None:
        return jsonify({'error': 'No updatable fields provided'}), 400

    updated = update_accessory(accessory_id, name=name, type_=type_, user_email=current_user)
    if not updated:
        return jsonify({'error': 'Update failed'}), 500

    return jsonify(updated), 200
