"""
accessories_routes.py

This file defines all Flask routes related to accessories.
It connects HTTP requests from the frontend to the accessories model
and ensures that only authenticated users can access these routes.
"""

from flask import render_template, jsonify, request
from routes import accessories_bp
from model.accessories_model import get_all_accessories, add_accessory, remove_accessory
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
    """
    return jsonify(get_all_accessories())


@accessories_bp.route('/api/accessories', methods=['POST'])
@token_required
def api_add_accessory(current_user):
    """
    API endpoint to add a new accessory.
    Expects accessory data in JSON format.
    """
    data = request.get_json()
    return jsonify(add_accessory(data["name"], data["type"])), 201


@accessories_bp.route('/api/accessories/<accessory_id>', methods=['DELETE'])
@token_required
def api_delete_accessory(current_user, accessory_id):
    """
    API endpoint to delete an accessory using its ID.
    """
    remove_accessory(accessory_id)
    return jsonify({"success": True})
