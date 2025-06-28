import os
from pymongo import MongoClient
from dotenv import load_dotenv
import certifi

load_dotenv()  # Load environment variables from .env

client = MongoClient(
    os.getenv("DATABASE_URL"),
    tls=True,
    tlsCAFile=certifi.where()
)
db = client.get_database()  
