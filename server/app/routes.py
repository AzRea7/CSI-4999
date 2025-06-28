from flask import Blueprint, jsonify, request
import os
from openai import OpenAI, RateLimitError
from pymongo import MongoClient
from bson.objectid import ObjectId
from app.db import db
# Test at http://localhost:5000/api/tasks/generate

api = Blueprint("api", __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
        f"User has a credit score of {credit_score}. {refinancing_info}. "
        + house_details +
        "Generate a personalized list of next-step tasks this user should do in their home buying or refinancing process."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            n=1
        )
        reply = response.choices[0].message.content.strip()
    except RateLimitError:
        return jsonify({"error": "OpenAI quota exceeded. Please check your API limits."}), 429
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

    task_lines = [line for line in reply.split("\n") if line.strip()]
    tasks = []
    for line in task_lines:
        title = line.lstrip("0123456789.-) " u"\u2022").strip()
        if title:
            tasks.append(title)

    db["Task"].delete_many({"userId": user_id})
    new_tasks = []
    for title in tasks:
        result = db["Task"].insert_one({
            "title": title,
            "completed": False,
            "userId": user_id
        })
        new_tasks.append({
            "id": str(result.inserted_id),
            "title": title,
            "completed": False
        })

    return jsonify({"tasks": new_tasks}), 201


@api.route("/tasks", methods=["GET"])
def get_tasks():
    user_id = request.args.get("user_id")
    query = {"userId": user_id} if user_id else {}

    cursor = db["Task"].find(query)
    tasks = [{
        "id": str(t["_id"]),
        "title": t["title"],
        "completed": t.get("completed", False)
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
