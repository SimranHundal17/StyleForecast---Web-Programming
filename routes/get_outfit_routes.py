"""
Outfit generation routes.
"""

from flask import render_template, request, jsonify
from routes import outfit_bp
from model.get_outfit_model import generate_outfit, get_weather
from utils.auth import token_required


@outfit_bp.route('/get_outfit', methods=['GET'])
@token_required
def get_outfit_page(current_user):
    """
    Display the Get Outfit page (requires login).
    """
    return render_template('get_outfit.html', user=current_user)


@outfit_bp.route('/api/get_outfit', methods=['POST'])
@token_required
def api_generate_outfit(current_user):
    """
    POST: Generate outfit suggestions based on location and occasion.
    """
    data = request.get_json()
    location = data.get('location', 'New Delhi')
    occasion = data.get('occasion', 'Casual')

    outfit = generate_outfit(location, occasion)
    return jsonify(outfit)


@outfit_bp.route('/api/weather/<location>', methods=['GET'])
@token_required
def api_get_weather(current_user, location):
    """
    GET: Retrieve mock weather data for a location.
    """
    return jsonify(get_weather(location))
