import logging

from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

logger = logging.getLogger(__name__)


def create_mongo_client(uri: str, timeout_ms: int) -> MongoClient:
    """
    Creates a new MongoClient.
    Used by the Flask app and (later) by every grading process, because a
    MongoClient must not be shared between processes.
    """
    return MongoClient(
        uri,
        serverSelectionTimeoutMS=timeout_ms,
        tz_aware=True,
        uuidRepresentation="standard",
    )


class Mongo:
    """Holds the MongoDB connection (DB2) for the Flask application."""

    def __init__(self) -> None:
        self._client: MongoClient | None = None
        self._db: Database | None = None

    def init_app(self, app) -> None:
        self._client = create_mongo_client(app.config["MONGO_URI"], app.config["MONGO_TIMEOUT_MS"])
        self._db = self._client[app.config["MONGO_DB_NAME"]]
        app.extensions["mongo"] = self
        logger.info("MongoDB configured: database '%s'", app.config["MONGO_DB_NAME"])

    @property
    def db(self) -> Database:
        if self._db is None:
            raise RuntimeError("Mongo is not initialized. Call mongo.init_app(app) first.")
        return self._db

    def collection(self, name: str) -> Collection:
        return self.db[name]

    def ping(self) -> bool:
        """Returns True if MongoDB is reachable."""
        try:
            self.db.client.admin.command("ping")
            return True
        except PyMongoError as exc:
            logger.warning("MongoDB ping failed: %s", exc)
            return False

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._db = None


mongo = Mongo()
