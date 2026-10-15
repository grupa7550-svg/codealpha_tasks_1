import os
import re
import secrets
from datetime import datetime, timezone
from urllib.parse import urlparse

from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request
from pymongo import MongoClient
from pymongo.errors import PyMongoError

load_dotenv()

app = Flask(__name__)

MONGODB_URI = os.getenv("MONGODB_URI", "").strip()
DATABASE_NAME = os.getenv("DATABASE_NAME", "codealpha_url_shortener")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "urls")
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000").rstrip("/")
SHORT_CODE_LENGTH = int(os.getenv("SHORT_CODE_LENGTH", "7"))

mongo_client = None
urls_collection = None

if MONGODB_URI:
    try:
        mongo_client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=3000)
        mongo_client.admin.command("ping")
        urls_collection = mongo_client[DATABASE_NAME][COLLECTION_NAME]
        urls_collection.create_index("short_code", unique=True)
    except Exception as exc:
        print(f"[WARN] MongoDB is not connected: {exc}")
        urls_collection = None


def valid_http_url(value: str) -> bool:
    """Allow only complete HTTP/HTTPS URLs with a hostname."""
    try:
        parsed = urlparse(value)
        return (
            parsed.scheme in ("http", "https")
            and bool(parsed.netloc)
            and "." in parsed.hostname
            and not any(ch.isspace() for ch in value)
        )
    except (ValueError, AttributeError):
        return False


def generate_short_code() -> str:
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
    return "".join(secrets.choice(alphabet) for _ in range(SHORT_CODE_LENGTH))


@app.get("/")
def home():
    return render_template("index.html")


@app.get("/health")
def health():
    connected = urls_collection is not None
    return jsonify({
        "status": "ok" if connected else "degraded",
        "database": "connected" if connected else "not_connected",
    }), 200 if connected else 503


@app.post("/api/shorten")
def shorten_url():
    if urls_collection is None:
        return jsonify({
            "error": "Database is not connected. Check MONGODB_URI in your .env file."
        }), 503

    payload = request.get_json(silent=True) or request.form
    original_url = str(payload.get("url", "")).strip()

    if not original_url:
        return jsonify({"error": "Please provide a URL."}), 400
    if len(original_url) > 2048:
        return jsonify({"error": "URL must be 2048 characters or fewer."}), 400
    if not valid_http_url(original_url):
        return jsonify({
            "error": "Enter a valid URL starting with http:// or https://."
        }), 400

    # Reuse an existing short link for the same URL.
    existing = urls_collection.find_one({"original_url": original_url})
    if existing:
        code = existing["short_code"]
        return jsonify({
            "original_url": original_url,
            "short_code": code,
            "short_url": f"{BASE_URL}/{code}",
            "message": "This URL already has a short link.",
        }), 200

    for _ in range(5):
        code = generate_short_code()
        document = {
            "original_url": original_url,
            "short_code": code,
            "created_at": datetime.now(timezone.utc),
            "clicks": 0,
        }
        try:
            urls_collection.insert_one(document)
            return jsonify({
                "original_url": original_url,
                "short_code": code,
                "short_url": f"{BASE_URL}/{code}",
                "message": "Short URL created successfully.",
            }), 201
        except PyMongoError as exc:
            # Retry only if the generated code collided; report other DB errors.
            if urls_collection.find_one({"short_code": code}):
                continue
            app.logger.exception("Could not save URL")
            return jsonify({"error": "Could not save URL. Check the database connection."}), 500

    return jsonify({"error": "Could not generate a unique code. Please try again."}), 500


@app.get("/<short_code>")
def redirect_short_url(short_code):
    if not re.fullmatch(r"[A-Za-z0-9]{1,20}", short_code):
        return jsonify({"error": "Invalid short code."}), 400
    if urls_collection is None:
        return jsonify({"error": "Database is not connected."}), 503

    try:
        record = urls_collection.find_one_and_update(
            {"short_code": short_code},
            {"$inc": {"clicks": 1}},
            return_document=True,
        )
    except PyMongoError:
        app.logger.exception("Could not retrieve URL")
        return jsonify({"error": "Database error."}), 500

    if not record:
        return jsonify({"error": "Short URL not found."}), 404

    return redirect(record["original_url"], code=302)


if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "true").lower() == "true")
