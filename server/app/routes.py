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
@api.route("/forecast", methods=["POST"])
def forecast_price():
    data = request.get_json()
    print("Received forecast request with data:", data)

    current_year = 2025
    print("Model contains forecast up to year:", max(model.keys()))

    forecast = []
    for i in range(1, 6):  # Predict next 5 years
        future_year = str(current_year + i)
        price = model.get(future_year)

        if price is not None:
            forecast.append({
                "date": future_year,
                "price": round(price, 2)
            })
        else:
            print(f"No forecast found for year {future_year} in model")

    if not forecast:
        print("Forecast array is EMPTY. Double-check model contents.")

    return jsonify({
        "forecast": forecast,
        "confidence": 75
    })





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
    
    try:
        # Search for homes by title, city, or address (case-insensitive)
        homes = db["Home"].find({
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"city": {"$regex": query, "$options": "i"}},
                {"address": {"$regex": query, "$options": "i"}}
            ]
        })
        
        results = []
        for home in homes:
            # Convert ObjectId to string for JSON serialization
            home["_id"] = str(home["_id"])
            home["listedById"] = str(home["listedById"])
            
            # Map the fields to match what the frontend expects
            result = {
                "id": home["_id"],
                "title": home["title"],
                "city": home.get("city", home.get("address", "Unknown")),
                "price": home["price"],
                "bedrooms": home.get("bedrooms", 0),
                "bathrooms": home.get("bathrooms", 0),
                "image": home.get("image")
            }
            results.append(result)
        
        return jsonify({"results": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------ ADD SAMPLE HOMES (for testing) ------
@api.route("/homes/sample", methods=["POST"])
def add_sample_homes():
    try:
        # First, check if we have any users to assign homes to
        users = list(db["User"].find())
        if not users:
            return jsonify({"error": "No users found. Create a user first."}), 400
        
        user_id = users[0]["_id"]  # Use the first user
        
        sample_homes = [
            {
                "title": "Modern Condo in Miami",
                "address": "123 Ocean Drive, Miami, FL",
                "city": "Miami",
                "price": 1800,
                "bedrooms": 2,
                "bathrooms": 2,
                "image": "https://via.placeholder.com/400x300",
                "description": "Beautiful modern condo with ocean view",
                "listedById": user_id
            },
            {
                "title": "Cozy Apartment in Chicago",
                "address": "456 Michigan Ave, Chicago, IL",
                "city": "Chicago", 
                "price": 1400,
                "bedrooms": 1,
                "bathrooms": 1,
                "image": "https://via.placeholder.com/400x300",
                "description": "Cozy downtown apartment",
                "listedById": user_id
            },
            {
                "title": "House in LA",
                "address": "789 Sunset Blvd, Los Angeles, CA",
                "city": "Los Angeles",
                "price": 2200,
                "bedrooms": 3,
                "bathrooms": 2,
                "image": "https://via.placeholder.com/400x300", 
                "description": "Spacious house in LA",
                "listedById": user_id
            },
            {
                "title": "Downtown Loft in New York",
                "address": "101 Broadway, New York, NY",
                "city": "New York",
                "price": 3500,
                "bedrooms": 2,
                "bathrooms": 1,
                "image": "https://via.placeholder.com/400x300",
                "description": "Modern loft in Manhattan",
                "listedById": user_id
            },
            {
                "title": "Beach House in San Diego",
                "address": "555 Coastal Blvd, San Diego, CA",
                "city": "San Diego",
                "price": 2800,
                "bedrooms": 4,
                "bathrooms": 3,
                "image": "https://via.placeholder.com/400x300",
                "description": "Beautiful beachfront property",
                "listedById": user_id
            }
        ]
        
        # Insert sample homes
        result = db["Home"].insert_many(sample_homes)
        return jsonify({
            "message": f"Added {len(result.inserted_ids)} sample homes",
            "ids": [str(id) for id in result.inserted_ids]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------ GET ALL HOMES ------
@api.route("/homes", methods=["GET"])
def get_all_homes():
    try:
        homes = db["Home"].find()
        results = []
        
        for home in homes:
            # Convert ObjectId to string for JSON serialization
            home["_id"] = str(home["_id"])
            home["listedById"] = str(home["listedById"])
            
            # Map the fields to match what the frontend expects
            result = {
                "id": home["_id"],
                "title": home["title"],
                "city": home.get("city", home.get("address", "Unknown")),
                "price": home["price"],
                "bedrooms": home.get("bedrooms", 0),
                "bathrooms": home.get("bathrooms", 0),
                "image": home.get("image")
            }
            results.append(result)
        
        return jsonify({"results": results})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@api.route("/listings/<listing_id>", methods=["DELETE"])
def delete_listing(listing_id):
    try:
        result = db["listings"].delete_one({"_id": ObjectId(listing_id)})
        if result.deleted_count == 0:
            return jsonify({"error": "Listing not found"}), 404

        # Cascade delete related data
        db["favorites"].delete_many({"listingId": listing_id})
        db["Task"].delete_many({"userId": listing_id})  # adjust if tasks are linked differently

        return jsonify({"message": "Listing and related favorites and tasks deleted"}), 200
    except Exception as e:
        return jsonify({"error": f"Invalid listing ID or delete failed: {str(e)}"}), 400
