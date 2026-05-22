import json
import os
import hashlib

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.json')

def load_db():
    try:
        with open(DB_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {'users': {}}

def save_db(db):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def hash_pass(password):
    return hashlib.sha256(password.encode()).hexdigest()
