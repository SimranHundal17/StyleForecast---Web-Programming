"""
Accessory management routes.
"""

from flask import render_template, jsonify, request
from routes import accessories_bp
from model.accessories_model import get_all_accessories, add_accessory, remove_accessory
from utils.auth import token_required


@accessories_bp.route('/accessories', methods=['GET'])
@token_required
def accessories_page(current_user):
    """
    Display the Accessories page (requires login).
    """
    return render_template('accessories.html', user=current_user)


@accessories_bp.route('/api/accessories', methods=['GET'])
@token_required
def api_get_accessories(current_user):
    """
    GET: Retrieve all accessories.
    """
    return jsonify(get_all_accessories())


@accessories_bp.route('/api/accessories', methods=['POST'])
@token_required
def api_add_accessory(current_user):
    """
    POST: Add a new accessory.
    """
    data = request.get_json()
    name = data.get('name')
    type_ = data.get('type')
    return jsonify(add_accessory(name, type_)), 201


@accessories_bp.route('/api/accessories/<int:accessory_id>', methods=['DELETE'])
@token_required
def api_delete_accessory(current_user, accessory_id):
    """
    DELETE: Remove an accessory by ID.
    """
    remove_accessory(accessory_id)
    return jsonify({"message": f"Accessory {accessory_id} removed"})
