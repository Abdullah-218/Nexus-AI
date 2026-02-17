"""
db.py — MongoDB Atlas connection singleton for FastAPI backend.

Works with MongoDB Atlas (cloud) via the MONGO_URI env variable.
URI format from Atlas: mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/
"""
import os
from datetime import datetime
from typing import Optional

try:
    from pymongo import MongoClient, DESCENDING
    from pymongo.server_api import ServerApi
    _MONGO_AVAILABLE = True
except ImportError:
    _MONGO_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _get_mongo_config():
    uri     = os.getenv("MONGO_URI", "").strip()
    db_name = os.getenv("MONGO_DB",  "nexus_ai")
    coll    = os.getenv("MONGO_COLL", "users")
    if not uri:
        raise RuntimeError(
            "MONGO_URI is not set.\n"
            "Copy backend/.env.example -> backend/.env and fill in your Atlas connection string."
        )
    return uri, db_name, coll


class Database:
    """
    Singleton MongoDB Atlas connection.
    Uses ServerApi(version='1') as required by Atlas.
    All CRUD helpers are safe-fail — they log errors but never crash the API.
    """
    _instance: Optional["Database"] = None
    _collection = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._init_connection()
        return cls._instance

    def _init_connection(self):
        if not _MONGO_AVAILABLE:
            print("[DB] pymongo not installed. Run:  pip install 'pymongo[srv]'")
            return
        try:
            uri, db_name, coll_name = _get_mongo_config()
            client = MongoClient(
                uri,
                server_api=ServerApi("1"),          # Atlas Stable API v1
                serverSelectionTimeoutMS=15000,     # 15 s for Atlas cold-start
                connectTimeoutMS=15000,
                socketTimeoutMS=30000,
                tls=True,                           # Atlas always TLS
                retryWrites=True,
            )
            client.admin.command("ping")            # verify reachable
            db = client[db_name]
            self._collection = db[coll_name]
            # Indexes — idempotent, safe to re-run
            self._collection.create_index("user_id", unique=True)
            self._collection.create_index([("last_updated", DESCENDING)])
            self._collection.create_index("profile.email")
            self._collection.create_index("profile.target_role")
            print(f"[DB] Connected to MongoDB Atlas -> {db_name}.{coll_name}")
        except RuntimeError as e:
            print(f"[DB] Config error: {e}")
            self._collection = None
        except Exception as e:
            print(f"[DB] Atlas connection failed: {e}")
            print("[DB] Check MONGO_URI in .env and Atlas Network Access (whitelist your IP or 0.0.0.0/0).")
            self._collection = None

    @property
    def available(self) -> bool:
        return self._collection is not None

    def get_collection(self):
        return self._collection

    # ── CRUD helpers ──────────────────────────────────────────────

    def upsert_user(self, user_id: str, data: dict) -> bool:
        if not self.available:
            return False
        try:
            doc = {k: v for k, v in data.items() if k != "_id"}
            doc["user_id"]     = user_id
            doc["last_updated"] = datetime.utcnow().isoformat()
            self._collection.update_one(
                {"user_id": user_id},
                {"$set": doc},
                upsert=True,
            )
            return True
        except Exception as e:
            print(f"[DB] upsert error: {e}")
            return False

    def get_user(self, user_id: str) -> Optional[dict]:
        if not self.available:
            return None
        try:
            doc = self._collection.find_one({"user_id": user_id})
            if doc:
                doc.pop("_id", None)
            return doc
        except Exception as e:
            print(f"[DB] get_user error: {e}")
            return None

    def find_by_email(self, email: str) -> Optional[dict]:
        if not self.available:
            return None
        try:
            if not email:
                return None
            doc = self._collection.find_one({"profile.email": email})
            if doc:
                doc.pop("_id", None)
            return doc
        except Exception as e:
            print(f"[DB] find_by_email error: {e}")
            return None

    def patch_user(self, user_id: str, patch: dict) -> bool:
        """Partial update — only updates specified keys using $set."""
        if not self.available:
            return False
        try:
            patch["last_updated"] = datetime.utcnow().isoformat()
            self._collection.update_one(
                {"user_id": user_id},
                {"$set": patch}
            )
            return True
        except Exception as e:
            print(f"[DB] patch error: {e}")
            return False


# Module-level singleton — imported everywhere as `from db import db`
db = Database()
