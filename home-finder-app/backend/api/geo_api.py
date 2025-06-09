import requests
from flask import Blueprint, request, jsonify
from utils.config import API_KEYS

geo_api = Blueprint('geo_api', __name__)

@geo_api.route('/api/geocode', methods=['GET'])
def geocode():
    location = request.args.get('location', '')
    if not location:
        return jsonify({"error": "Missing location parameter"}), 400

    url = "https://api.opencagedata.com/geocode/v1/json"
    params = {
        "q": location,
        "key": API_KEYS["geocoding"]
    }

    response = requests.get(url, params=params)
    return jsonify(response.json())
