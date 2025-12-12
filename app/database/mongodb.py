from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from app.config import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MongoDBConnection:
    _instance: Optional['MongoDBConnection'] = None
    _client: Optional[MongoClient] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self) -> MongoClient:
        if self._client is None:
            try:
                self._client = MongoClient(
                    settings.mongodb_url,
                    serverSelectionTimeoutMS=5000,
                    maxPoolSize=50,
                    minPoolSize=10
                )
                self._client.admin.command('ping')
                logger.info("Successfully connected to MongoDB")
            except ConnectionFailure as e:
                logger.error(f"Failed to connect to MongoDB: {e}")
                raise
        return self._client
    
    def get_database(self, db_name: Optional[str] = None):
        if self._client is None:
            self.connect()
        db_name = db_name or settings.database_name
        return self._client[db_name]
    
    def close(self):
        if self._client:
            self._client.close()
            self._client = None
            logger.info("MongoDB connection closed")
    
    def get_collection(self, collection_name: str, db_name: Optional[str] = None):
        db = self.get_database(db_name)
        return db[collection_name]


mongodb = MongoDBConnection()
