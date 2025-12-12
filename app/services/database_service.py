from app.database.mongodb import mongodb
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing database operations"""
    
    def __init__(self):
        self.db = mongodb.get_database()
    
    def create_collection(
        self,
        collection_name: str,
        validator: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Create a new collection with optional validation schema
        
        Args:
            collection_name: Name of the collection to create
            validator: Optional JSON schema validator
            
        Returns:
            True if created successfully, False otherwise
        """
        try:
            if collection_name in self.db.list_collection_names():
                logger.warning(f"Collection {collection_name} already exists")
                return False
            
            # Create collection with optional validation
            if validator:
                self.db.create_collection(
                    collection_name,
                    validator=validator
                )
            else:
                self.db.create_collection(collection_name)
            
            # Create basic indexes
            self._create_default_indexes(collection_name)
            
            logger.info(f"Collection {collection_name} created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating collection {collection_name}: {e}")
            return False
    
    def _create_default_indexes(self, collection_name: str):
        """
        Create default indexes for a collection
        
        Args:
            collection_name: Name of the collection
        """
        collection = self.db[collection_name]
        
        # Create index on created_at for sorting
        collection.create_index("created_at")
        
        # Create index on updated_at
        collection.create_index("updated_at")
        
        logger.info(f"Default indexes created for {collection_name}")
    
    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if exists, False otherwise
        """
        return collection_name in self.db.list_collection_names()
    
    def delete_collection(self, collection_name: str) -> bool:
        """
        Delete a collection
        
        Args:
            collection_name: Name of the collection to delete
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            if not self.collection_exists(collection_name):
                logger.warning(f"Collection {collection_name} does not exist")
                return False
            
            self.db.drop_collection(collection_name)
            logger.info(f"Collection {collection_name} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting collection {collection_name}: {e}")
            return False
    
    def copy_collection_data(
        self,
        source_collection: str,
        target_collection: str
    ) -> bool:
        """
        Copy all data from source collection to target collection
        
        Args:
            source_collection: Name of the source collection
            target_collection: Name of the target collection
            
        Returns:
            True if copied successfully, False otherwise
        """
        try:
            if not self.collection_exists(source_collection):
                logger.error(f"Source collection {source_collection} does not exist")
                return False
            
            source = self.db[source_collection]
            target = self.db[target_collection]
            
            # Get all documents from source
            documents = list(source.find())
            
            if documents:
                # Insert into target
                target.insert_many(documents)
                logger.info(
                    f"Copied {len(documents)} documents from {source_collection} "
                    f"to {target_collection}"
                )
            else:
                logger.info(f"No documents to copy from {source_collection}")
            
            return True
        except Exception as e:
            logger.error(f"Error copying collection data: {e}")
            return False
    
    def get_collection_stats(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics about a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with collection stats or None if error
        """
        try:
            if not self.collection_exists(collection_name):
                return None
            
            stats = self.db.command("collStats", collection_name)
            return {
                "name": collection_name,
                "count": stats.get("count", 0),
                "size": stats.get("size", 0),
                "avgObjSize": stats.get("avgObjSize", 0),
                "storageSize": stats.get("storageSize", 0),
                "indexes": stats.get("nindexes", 0)
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return None
