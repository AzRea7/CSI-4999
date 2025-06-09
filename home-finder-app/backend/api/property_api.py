import requests
from flask import Blueprint, jsonify, request
from utils.config import API_KEYS

property_api = Blueprint('property_api', __name__)

@property_api.route('/api/search', methods=['GET'])
def search_zillow():
    location = request.args.get('location', 'San Francisco')
    print("📍 Requested location:", location)

    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
    params = {
        "location": location,
        "status_type": "ForSale",
        "limit": "10",
        "sort": "Newest"
    }

    headers = {
        "X-RapidAPI-Key": API_KEYS.get("zillow_key"),
        "X-RapidAPI-Host": API_KEYS.get("zillow_host")
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        print("🌐 Zillow API status:", response.status_code)

        data = response.json()
        print("📦 Raw data keys:", list(data.keys()))

        simplified = []
        for prop in data.get("props", []):
            photos = prop.get("carouselPhotos") or []
            image_url = photos[0]["url"] if photos else None

            simplified.append({
                "address": prop.get("address"),
                "bedrooms": prop.get("bedrooms"),
                "bathrooms": prop.get("bathrooms"),
                "image": image_url
            })

        print(f"✅ Returning {len(simplified)} homes")
        return jsonify(simplified)

    except Exception as e:
        print("❌ API ERROR:", e)
        return jsonify({"error": str(e)}), 500
