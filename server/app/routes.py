from flask import Blueprint, jsonify

api = Blueprint("api", __name__)

@api.route("/users", methods=["GET"])
def get_users():
    return jsonify({"users": ["test1", "test2", "test3"]})
