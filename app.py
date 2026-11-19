from flask import Flask, jsonify
from dotenv import load_dotenv

import db

load_dotenv()  # read keys from .env

# Files in ./static are served at the site root (e.g. /index.html)
app = Flask(__name__, static_folder="static", static_url_path="")


@app.get("/")
def home():
    # Show the website's main page
    return app.send_static_file("index.html")


@app.get("/api/health")
def health():
    # Simple check that the server is up
    return jsonify({"ok": True})


@app.get("/api/patients")
def patients():
    # List all patients
    return jsonify(db.list_patients())


db.init_db()  # create tables on startup

if __name__ == "__main__":
    app.run(debug=True, port=5000)
