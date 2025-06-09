import os
from dotenv import load_dotenv

load_dotenv()

API_KEYS = {
    "mapbox": os.getenv("MAPBOX_KEY"),
    "geocoding": os.getenv("GEOCODING_KEY"),
    "zillow_key": os.getenv("ZILLOW_API_KEY"),
    "zillow_host": os.getenv("ZILLOW_API_HOST"),
}
