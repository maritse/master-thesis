from flask import Flask, request, jsonify
import sqlite3
import base64
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

DB_FILE = "./db.db"

def create_db_connection():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    cur = conn.cursor()
    return cur

app = Flask(__name__)

def compute_key_hash(pem_data: bytes) -> bytes:
    public_key = serialization.load_pem_public_key(pem_data, backend=default_backend())
    der_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return w3.keccak(der_bytes)  # zwraca 32 bajty

@app.route("/upload", methods=["POST"])
def upload_key():
    if "file" not in request.files:
        return jsonify({"error": "Brak pliku"}), 400
    

