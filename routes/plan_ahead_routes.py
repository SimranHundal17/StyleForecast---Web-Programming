"""
Plan Ahead routes.
"""

from flask import render_template, jsonify, request
from routes import plan_bp
from model.plan_ahead_model import get_all_plans, add_plan
from utils.auth import token_required


@plan_bp.route('/plan_ahead', methods=['GET'])
@token_required
def plan_ahead_page(current_user):
    """
    Display the Plan Ahead page (requires login).
    """
    return render_template('plan_ahead.html', user=current_user)


@plan_bp.route('/api/plans', methods=['GET'])
@token_required
def api_get_plans(current_user):
    """
    GET: Retrieve all planned events.
    """
    return jsonify(get_all_plans())


@plan_bp.route('/api/plans', methods=['POST'])
@token_required
def api_add_plan(current_user):
    """
    POST: Add a new plan (dummy data).
    """
    data = request.get_json()
    return jsonify(add_plan(data)), 201
