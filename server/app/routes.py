from flask import Blueprint, jsonify, request
import os
import json
from openai import OpenAI, RateLimitError
from pymongo import MongoClient
from bson.objectid import ObjectId
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from bson.objectid import ObjectId

# Test at http://localhost:5000/api/tasks/generate

api = Blueprint("api", __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@api.route("/tasks/generate", methods=["POST"])
def generate_tasks():
    import traceback  # ensure it's imported for error logs

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
