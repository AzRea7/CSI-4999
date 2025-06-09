from flask import Flask
from api.property_api import property_api
from api.geo_api import geo_api
from api.mortgage import mortgage_api
from flask_cors import CORS

print("Starting Flask app")


app = Flask(__name__)
CORS(app, origins=["http://localhost:3000"])
app.register_blueprint(property_api)
app.register_blueprint(geo_api)
app.register_blueprint(mortgage_api)
# Route must be above the app.run block
@app.route('/')
def home():
    return "Flask backend is running!"

# This must be at the very bottom
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=5001)
