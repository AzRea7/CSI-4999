import os
from pymongo import ASCENDING, TEXT, MongoClient
from dotenv import load_dotenv
import certifi

load_dotenv()  # Load environment variables from .env

client = MongoClient(
    os.getenv("DATABASE_URL"),
    tls=True,
    tlsCAFile=certifi.where()
)
db = client.get_database()  

# ---- Create performance indexes ----
# Listings collection
db.listings.create_index([("location", ASCENDING)])
db.listings.create_index([("price", ASCENDING)])
db.listings.create_index([("propertyType", ASCENDING)])
db.listings.create_index([("title", TEXT), ("description", TEXT)])  # for full-text search

# Users collection
db.users.create_index([("email", ASCENDING)], unique=True)

# Favorites collection
db.favorites.create_index([("userId", ASCENDING)])

# ---- Schema validation rules ----
# User collection
db.command("collMod", "User", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["email", "password"],
        "properties": {
            "email": {"bsonType": "string", "description": "must be a string and is required"},
            "password": {"bsonType": "string", "description": "must be a string and is required"},
            "name": {"bsonType": "string", "description": "optional but must be a string if present"}
        }
    }
}, validationAction="error")

# Listings collection
db.command("collMod", "listings", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "price", "location", "listedById"],
        "properties": {
            "title": {"bsonType": "string"},
            "price": {"bsonType": "number"},
            "location": {"bsonType": "string"},
            "propertyType": {"bsonType": "string"},
            "listedById": {"bsonType": "string"}
        }
    }
}, validationAction="error")

# Favorites collection
db.command("collMod", "favorites", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["userId", "listingId"],
        "properties": {
            "userId": {"bsonType": "string"},
            "listingId": {"bsonType": "string"}
        }
    }
}, validationAction="error")

# Task collection
db.command("collMod", "Task", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "category", "due_date", "priority", "userId"],
        "properties": {
            "title": {"bsonType": "string"},
            "category": {"bsonType": "string"},
            "due_date": {"bsonType": "string"},
            "priority": {"bsonType": "string"},
            "userId": {"bsonType": "string"}
        }
    }
}, validationAction="error")
