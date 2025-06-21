from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import datetime
from pymongo.uri_parser import parse_uri

app = Flask(__name__)
CORS(app)
load_dotenv()

# 👇 Parse connection manually to avoid +srv DNS errors and TLS issues
uri = os.getenv("MONGO_URI")
parsed = parse_uri(uri)
host = parsed['nodelist'][0][0]
username = parsed['username']
password = parsed['password']

client = MongoClient(
    f"mongodb://{username}:{password}@{host}/?ssl=true&retryWrites=true&w=majority&tlsAllowInvalidCertificates=true",
    tls=True,
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=10000
)

db = client["never_game"]
collection = db["confessions"]

@app.route('/')
def home():
    return "🔥 Flask backend is running!"

@app.route('/submit', methods=['POST'])
def submit():
    try:
        data = request.get_json()
        print("🔥 Incoming data:", data)

        entry = {
            "nickname": data.get("nickname", "Anonymous"),
            "age": data.get("age", "Unknown"),
            "score": data.get("score", 0),
            "total": data.get("total", 0),
            "percent": data.get("percent", 0),
            "answers": data.get("answers", []),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        collection.insert_one(entry)
        return jsonify({"message": "Data saved successfully!"}), 200

    except Exception as e:
        import traceback
        print("❌ Error during /submit:")
        traceback.print_exc()
        return jsonify({"message": "Error saving data"}), 500

@app.route('/confessions', methods=['GET'])
def get_confessions():
    try:
        data = list(collection.find({}, {"_id": 0}))  # hide _id
        return jsonify(data), 200
    except Exception as e:
        print("❌ Error during /confessions:", e)
        return jsonify({"message": "Error fetching data"}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
