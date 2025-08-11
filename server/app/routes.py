from flask import Blueprint, jsonify, request
import os
import json
import numpy as np
from openai import OpenAI, RateLimitError
from pymongo import MongoClient
from bson.objectid import ObjectId
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId
import traceback
from joblib import load
import requests

# Test at http://localhost:5000/api/tasks/generate

api = Blueprint("api", __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MODEL_PATH = os.path.join(os.path.dirname(__file__), "house_price_model.joblib")
model = load(MODEL_PATH)

@api.route("/tasks/generate", methods=["POST"])
def generate_tasks():

    data = request.get_json()
    credit_score = data.get("credit_score")
    refinancing_info = data.get("refinancing_info")
    user_id = data.get("user_id")

    house = db["Home"].find_one({"listedById": user_id})
    house_details = ""
    if house:
        house_details = f"The user is interested in a house titled '{house['title']}' priced at ${house['price']}. "

    prompt = (
        f"The user has a credit score of {credit_score}. {refinancing_info}. "
        f"{house_details}"
        "Generate a JSON array of 5-7 tasks to help this user through buying or refinancing a home. "
        "Each task should be an object with the following fields:\n"
        "- title (string)\n"
        "- category (string; one of: finance, legal, inspection, research, insurance, planning, move-in)\n"
        "- due_date (string; realistic value like 'within 2 weeks', 'before closing')\n"
        "- priority (string; one of: low, medium, high)\n"
        "Return only raw JSON, no markdown, no explanation, no formatting, just the JSON array."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            n=1
        )
        reply = response.choices[0].message.content.strip()
        print("\n GPT raw reply:\n", reply)
    except RateLimitError:
        return jsonify({"error": "OpenAI quota exceeded. Please check your API limits."}), 429
    except Exception as e:
        print(" GPT error:", e)
        traceback.print_exc()
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    try:
        task_objects = json.loads(reply)
    except json.JSONDecodeError:
        print(" Failed to parse GPT response as JSON.")
        traceback.print_exc()
        return jsonify({"error": "Failed to parse AI response as JSON."}), 500

    # Optional: Validate structure of tasks
    required_keys = {"title", "category", "due_date", "priority"}
    for i, task in enumerate(task_objects):
        missing = required_keys - task.keys()
        if missing:
            print(f" Task {i} is missing fields: {missing}")

    db["Task"].delete_many({"userId": user_id})
    new_tasks = []
    for task in task_objects:
        doc = {
            "title": task["title"],
            "category": task["category"],
            "due_date": task["due_date"],
            "priority": task["priority"],
            "completed": False,
            "userId": user_id
        }
        result = db["Task"].insert_one(doc)

        # Serialize safely
        new_tasks.append({
            "id": str(result.inserted_id),
            "title": task["title"],
            "category": task["category"],
            "due_date": task["due_date"],
            "priority": task["priority"],
            "completed": False,
            "userId": str(user_id)
        })


    return jsonify({"tasks": new_tasks}), 201



@api.route("/tasks", methods=["GET"])
def get_tasks():
    user_id = request.args.get("user_id")
    query = {"userId": user_id} if user_id else {}

    cursor = db["Task"].find(query)
    tasks = [{
    "id": str(t["_id"]),
    "title": t.get("title", ""),
    "completed": t.get("completed", False),
    "category": t.get("category", ""),
    "priority": t.get("priority", "low"),
    "due_date": t.get("due_date", "TBD")
    } for t in cursor]

    return jsonify({"tasks": tasks})


@api.route("/tasks/<task_id>", methods=["GET"])
def get_task_by_id(task_id):
    try:
        task = db["Task"].find_one({"_id": ObjectId(task_id)})
        if not task:
            return jsonify({"error": "Task not found"}), 404

        return jsonify({
            "id": str(task["_id"]),
            "title": task["title"],
            "completed": task.get("completed", False)
        })
    except Exception as e:
        return jsonify({"error": f"Invalid ID or error occurred: {str(e)}"}), 400
    
@api.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    email = data.get("email")
    name = data.get("name")
    password = data.get("password")

    if db["User"].find_one({"email": email}):
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = generate_password_hash(password)
    result = db["User"].insert_one({
        "name": name,
        "email": email,
        "password": hashed_pw
    })

    return jsonify({"id": str(result.inserted_id), "email": email}), 201

@api.route('/init-text-index', methods=['POST'])
def create_text_index():
    db.homes.create_index([
        ('title', 'text'),
        ('description', 'text'),
        ('address', 'text'),
    ])
    return jsonify({'message': 'Text index created'}), 200


# app/routes.py
@api.route("/users", methods=["GET"])
def get_users():
    users_cursor = db["User"].find()
    users = [{"id": str(user["_id"]), "name": user["name"], "email": user["email"]} for user in users_cursor]
    return jsonify({"users": users})

@api.route("/login", methods=["POST"])
def login_user():
    data = request.get_json()
    email = data.get("email")
    password = data.get("password")

    user = db["User"].find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "id": str(user["_id"]),
        "email": user["email"],
        "name": user["name"]
    }), 200

@api.route("/tasks/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    try:
        result = db["Task"].delete_one({"_id": ObjectId(task_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Task not found"}), 404
        return jsonify({"message": "Task deleted"}), 200
    except Exception as e:
        return jsonify({"error": f"Invalid task ID or delete failed: {str(e)}"}), 400

# ------ FORECAST ------
@api.route("/forecast/favorites", methods=["GET"])
def forecast_all_favorites():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"error": "userId is required"}), 400

    # Find all favorites for the user
    favorites = list(db["Favorite"].find({"userId": user_id}))
    if not favorites:
        return jsonify({"error": "No favorites found"}), 404

    current_year = 2025
    results = []

    for fav in favorites:
        base_price = fav.get("price")
        if not base_price:
            continue  # Skip if no price is stored

        forecast = []
        for i in range(1, 6):  # Predict next 5 years
            year = str(current_year + i)
            if year in model:
                forecast.append({
                    "date": year,
                    "price": round(base_price * (model[year] / list(model.values())[0]), 2)
                })

        results.append({
            "home": {
                "zpid": fav.get("zpid"),
                "title": fav.get("title"),
                "city": fav.get("city"),
                "price": base_price,
                "bedrooms": fav.get("bedrooms"),
                "bathrooms": fav.get("bathrooms"),
                "image": fav.get("image")
            },
            "forecast": forecast
        })

    return jsonify({"forecasts": results})






# ------ CHAT BOT ------
@api.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_message = data.get("message")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful real estate assistant."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
        )
        reply = response.choices[0].message.content.strip()
        return jsonify({ "reply": reply })
    except Exception as e:
        return jsonify({ "error": str(e) }), 500

# ------ SEARCH HOMES ------
@api.route("/search", methods=["GET"])
def search_homes():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"results": []})

    RAPIDAPI_KEY = os.getenv("ZILLOW_API_KEY")
    if not RAPIDAPI_KEY:
        return jsonify({"error": "ZILLOW_API_KEY not configured"}), 500

    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "zillow-com1.p.rapidapi.com"
    }

    url = "https://zillow-com1.p.rapidapi.com/propertyExtendedSearch"
    params = {
        "location": query,
        "status_type": "ForSale",   # Or "ForRent" if you want rentals
        "home_type": "Houses"       # Optional: can remove if you want all types
    }

    try:
        resp = requests.get(url, headers=headers, params=params)
        data = resp.json()

        import json
        print("RAW ZILLOW RESPONSE:")
        print(json.dumps(data, indent=2))


        # Directly get props array
        items = data.get("props", [])
        results = []

        for item in items:
            results.append({
                "id": str(item.get("zpid", "")),
                "title": item.get("address", "").split(",")[0] if item.get("address") else "Unknown",
                "city": extract_city(item.get("address", "")),
                "price": item.get("price", 0),
                "bedrooms": item.get("bedrooms", 0),
                "bathrooms": item.get("bathrooms", 0),
                "image": item.get("imgSrc")
            })

        return jsonify({"results": results})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

def extract_city(address):
    """Extract city from Zillow's address string."""
    try:
        parts = address.split(",")
        return parts[1].strip() if len(parts) > 1 else "Unknown"
    except Exception:
        return "Unknown"

def parse_property_summary(item):
    """Map Zillow search result to our frontend format."""
    return {
        "id": str(item.get("zpid", "")),
        "title": item.get("address", "").split(",")[0] if item.get("address") else "Unknown",
        "city": extract_city(item.get("address", "")),
        "price": item.get("price", 0),
        "bedrooms": item.get("bedrooms", 0),
        "bathrooms": item.get("bathrooms", 0),
        "image": item.get("imgSrc", None)
    }

def parse_property_detail(data):
    """Map Zillow single property detail to our frontend format."""
    return {
        "id": str(data.get("zpid", "")),
        "title": data.get("address", "").split(",")[0] if data.get("address") else "Unknown",
        "city": extract_city(data.get("address", "")),
        "price": data.get("price", 0),
        "bedrooms": data.get("bedrooms", 0),
        "bathrooms": data.get("bathrooms", 0),
        "image": (data.get("imgSrc") or 
                  (data.get("photos", [{}])[0].get("url") if data.get("photos") else None))
    }
# ------ FORECAST ------
@api.route("/forecast/favorites", methods=["GET"])
def forecast_favorited_homes():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    favorites = list(db["Favorite"].find({"userId": user_id}))
    if not favorites:
        return jsonify({"forecast": []})

    current_year = 2025
    base_year = list(model["forecast"].values())[0]
    forecasts = []

    for fav in favorites:
        base_price = fav.get("price")
        if base_price is None:
            # No price, skip this favorite
            continue

        forecast = []
        for i in range(1, 6):
            year = str(current_year + i)
            if year in model["forecast"]:
                scale = model["forecast"][year] / base_year
                min_scale = model["lower"][year] / base_year
                max_scale = model["upper"][year] / base_year

                forecast.append({
                    "date": year,
                    "price": round(base_price * scale, 2),
                    "min": round(base_price * min_scale, 2),
                    "max": round(base_price * max_scale, 2),
                })

        forecasts.append({
            "home": {
                "_id": str(fav.get("_id", "")),
                "title": fav.get("title", "Untitled"),
                "price": base_price
            },
            "forecast": forecast,
            "confidence": f"{model.get('confidence', 95)}%"
        })

    return jsonify({"forecast": forecasts})


@api.route("/forecast", methods=["POST"])
def forecast_home():
    data = request.get_json()
    area = data.get("area")
    bedrooms = data.get("bedrooms")
    bathrooms = data.get("bathrooms")
    price = data.get("price")

    if None in (area, bedrooms, bathrooms, price):
        return jsonify({"error": "Missing required home data"}), 400

    current_year = 2025
    base_year = list(model["forecast"].values())[0]
    forecast = []

    for i in range(1, 6):
        year = str(current_year + i)
        if year in model["forecast"]:
            scale = model["forecast"][year] / base_year
            min_scale = model["lower"][year] / base_year
            max_scale = model["upper"][year] / base_year

            forecast.append({
                "date": year,
                "price": round(price * scale, 2),
                "min": round(price * min_scale, 2),
                "max": round(price * max_scale, 2),
            })

    return jsonify({
        "forecast": forecast,
        "confidence": f"{model.get('confidence', 95)}%"
    })


@api.route("/homes", methods=["GET"])
def get_homes():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    homes_cursor = db["Home"].find({"listedById": user_id})
    homes = []
    for home in homes_cursor:
        home["_id"] = str(home["_id"])
        homes.append(home)

    return jsonify({"homes": homes})


# ------ Favorites ------
@api.route("/favorites", methods=["POST"])
def add_favorite():
    data = request.get_json()
    user_id = data.get("userId")
    zpid = data.get("zpid")

    if not user_id or not zpid:
        return jsonify({"error": "userId and zpid are required"}), 400

    # Prevent duplicates
    existing = db["Favorite"].find_one({"userId": user_id, "zpid": zpid})
    if existing:
        return jsonify({"message": "Already favorited"}), 200

    favorite_doc = {
        "userId": user_id,
        "zpid": zpid,
        "title": data.get("title"),
        "city": data.get("city"),
        "price": data.get("price"),
        "bedrooms": data.get("bedrooms"),
        "bathrooms": data.get("bathrooms"),
        "image": data.get("image")
    }
    db["Favorite"].insert_one(favorite_doc)
    return jsonify({"message": "Favorite added"}), 201


@api.route("/favorites", methods=["GET"])
def get_favorites():
    user_id = request.args.get("userId")
    if not user_id:
        return jsonify({"error": "userId required"}), 400

    cursor = db["Favorite"].find({"userId": user_id})
    results = []
    for fav in cursor:
        fav["_id"] = str(fav["_id"])
        results.append(fav)

    # Always return 200 with an empty array instead of 404
    return jsonify({"favorites": results})


@api.route("/favorites/<fav_id>", methods=["DELETE"])
def remove_favorite(fav_id):
    try:
        result = db["Favorite"].delete_one({"_id": ObjectId(fav_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Favorite not found"}), 404
        return jsonify({"message": "Favorite removed"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
