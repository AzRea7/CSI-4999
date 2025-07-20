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

