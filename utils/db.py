import json
import os
import bcrypt
from sqlitedict import SqliteDict

DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'aryax.db')
OLD_DB_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db.json')

class TrackedDict(dict):
    def __init__(self, *args, parent=None, key=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__['parent'] = parent
        self.__dict__['key'] = key

    def __setitem__(self, k, v):
        super().__setitem__(k, v)
        if self.parent is not None:
            # Trigger write to SQLite
            self.parent[self.key] = dict(self)

    def setdefault(self, k, default=None):
        if k not in self:
            self[k] = default
        return self[k]
        
    def pop(self, k, default=None):
        res = super().pop(k, default)
        if self.parent is not None:
            self.parent[self.key] = dict(self)
        return res

class UsersProxy:
    def __init__(self):
        self.db = SqliteDict(DB_FILE, tablename='users', autocommit=True)

    def __getitem__(self, key):
        data = self.db[key]
        # Return a tracked dict so nested updates trigger DB write
        return TrackedDict(data, parent=self.db, key=key)

    def __setitem__(self, key, value):
        self.db[key] = dict(value)

    def __contains__(self, key):
        return key in self.db

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return self.db.keys()

    def items(self):
        for k, v in self.db.items():
            yield k, TrackedDict(v, parent=self.db, key=k)

class DBWrapper(dict):
    def __init__(self):
        self.users = UsersProxy()
    
    def __getitem__(self, key):
        if key == 'users':
            return self.users
        return super().__getitem__(key)

# Auto-migrate from db.json to SQLite
if os.path.exists(OLD_DB_FILE):
    try:
        with open(OLD_DB_FILE, 'r', encoding='utf-8') as f:
            old_data = json.load(f)
        users_db = SqliteDict(DB_FILE, tablename='users', autocommit=True)
        for username, data in old_data.get('users', {}).items():
            if username not in users_db:
                users_db[username] = data
        users_db.close()
        os.rename(OLD_DB_FILE, OLD_DB_FILE + '.migrated')
        print("✅ Successfully migrated db.json to SQLite aryax.db")
    except Exception as e:
        print("Migration error:", e)

def load_db():
    return DBWrapper()

def save_db(db):
    # SqliteDict autocommits on assignment, so we do nothing here.
    pass

def hash_pass(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_pass(password, hashed):
    if not hashed:
        return False
    try:
        # Check if it's an old sha256 hash (length 64 without '$')
        if len(hashed) == 64 and '$' not in hashed:
            import hashlib
            return hashlib.sha256(password.encode()).hexdigest() == hashed
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False
