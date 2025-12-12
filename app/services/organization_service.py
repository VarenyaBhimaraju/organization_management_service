from app.database.mongodb import mongodb
from app.models.organization import (
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationInDB
)
from app.models.admin import AdminCreate
from app.services.auth_service import AuthService
from app.services.database_service import DatabaseService
from datetime import datetime
from typing import Optional, Dict, Any
from bson import ObjectId
import logging


logger = logging.getLogger(__name__)

class OrganizationService:
    """Service for organization management operations"""
    
    def __init__(self):
        self.db = mongodb.get_database()
        self.organizations_collection = self.db["organizations"]
        self.auth_service = AuthService()
        self.database_service = DatabaseService()
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure required indexes exist"""
        # Create unique index on organization_name
        self.organizations_collection.create_index("organization_name", unique=True)
        # Create index on collection_name
        self.organizations_collection.create_index("collection_name", unique=True)
    
    def _generate_collection_name(self, organization_name: str) -> str:
        """
        Generate collection name for organization
        
        Args:
            organization_name: Name of the organization
            
        Returns:
            Collection name in format: org_<organization_name>
        """
        return f"org_{organization_name}"
    
    def create_organization(self, org_data: OrganizationCreate) -> Optional[Dict[str, Any]]:
        try:
            logger.info(f"Creating organization with data: {org_data.dict()}")
            
            # Check if organization already exists
            existing_org = self.organizations_collection.find_one({"organization_name": org_data.organization_name})
            if existing_org:
                logger.warning(f"Organization {org_data.organization_name} already exists")
                return None

            # Generate collection name
            collection_name = self._generate_collection_name(org_data.organization_name)

            # Create organization document
            org_doc = {
                "organization_name": org_data.organization_name,
                "collection_name": collection_name,
                "created_at": datetime.utcnow(),
                "admin_id": None
            }
            
            logger.info(f"Inserting organization document: {org_doc}")
            org_result = self.organizations_collection.insert_one(org_doc)
            org_id = str(org_result.inserted_id)
            logger.info(f"Inserted organization with ID: {org_id}")
            
            # Create admin user
            admin_data = AdminCreate(
                email=org_data.email,
                password=org_data.password,
                organization_id=org_id
            )
            
            admin_id = self.auth_service.create_admin(admin_data)
            if not admin_id:
                self.organizations_collection.delete_one({"_id": org_result.inserted_id})
                logger.error("Failed to create admin user, rolling back organization")
                return None
            
            # Update organization with admin_id
            self.organizations_collection.update_one(
                {"_id": org_result.inserted_id},
                {"$set": {"admin_id": admin_id}}
            )
            
            # Create dynamic collection for organization
            collection_created = self.database_service.create_collection(collection_name)
            if not collection_created:
                logger.warning(f"Collection {collection_name} may already exist or failed to create")
            
            # Fetch and return created organization
            created_org = self.organizations_collection.find_one({"_id": org_result.inserted_id})
            admin = self.auth_service.get_admin_by_id(admin_id)
            created_org["admin_email"] = admin["email"] if admin else org_data.email
            
            logger.info(f"Organization {org_data.organization_name} created successfully")
            return created_org
        except Exception as e:
            logger.error(f"Error creating organization: {e}")
            return None

    
    def get_organization_by_name(
        self,
        organization_name: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get organization by name
        
        Args:
            organization_name: Name of the organization
            
        Returns:
            Organization document if found, None otherwise
        """
        try:
            org = self.organizations_collection.find_one(
                {"organization_name": organization_name}
            )
            
            if org:
                # Get admin email
                admin = self.auth_service.get_admin_by_id(org["admin_id"])
                org["admin_email"] = admin["email"] if admin else "N/A"
            
            return org
        except Exception as e:
            logger.error(f"Error getting organization: {e}")
            return None
    
    def get_organization_by_id(self, org_id: str) -> Optional[Dict[str, Any]]:
        """
        Get organization by ID
        
        Args:
            org_id: Organization ID
            
        Returns:
            Organization document if found, None otherwise
        """
        try:
            org = self.organizations_collection.find_one({"_id": ObjectId(org_id)})
            
            if org:
                # Get admin email
                admin = self.auth_service.get_admin_by_id(org["admin_id"])
                org["admin_email"] = admin["email"] if admin else "N/A"
            
            return org
        except Exception as e:
            logger.error(f"Error getting organization by ID: {e}")
            return None
    
    def update_organization(
        self,
        old_org_name: str,
        update_data: OrganizationUpdate,
        admin_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update organization and migrate data to new collection
        
        Args:
            old_org_name: Current organization name
            update_data: Updated organization data
            admin_id: Admin ID performing the update
            
        Returns:
            Updated organization document if successful, None otherwise
        """
        try:
            # Get existing organization
            existing_org = self.get_organization_by_name(old_org_name)
            
            if not existing_org:
                logger.error(f"Organization {old_org_name} not found")
                return None
            
            # Verify admin owns this organization
            if existing_org["admin_id"] != admin_id:
                logger.error("Admin does not have permission to update this organization")
                return None
            
            # Check if new name is different and already exists
            if update_data.organization_name != old_org_name:
                new_org_exists = self.organizations_collection.find_one(
                    {"organization_name": update_data.organization_name}
                )
                
                if new_org_exists:
                    logger.error(
                        f"Organization {update_data.organization_name} already exists"
                    )
                    return None
                
                # Generate new collection name
                new_collection_name = self._generate_collection_name(
                    update_data.organization_name
                )
                old_collection_name = existing_org["collection_name"]
                
                # Create new collection
                self.database_service.create_collection(new_collection_name)
                
                # Copy data from old collection to new
                if self.database_service.collection_exists(old_collection_name):
                    self.database_service.copy_collection_data(
                        old_collection_name,
                        new_collection_name
                    )
                    
                    # Delete old collection
                    self.database_service.delete_collection(old_collection_name)
                
                # Update organization document
                update_doc = {
                    "organization_name": update_data.organization_name,
                    "collection_name": new_collection_name,
                    "updated_at": datetime.utcnow()
                }
            else:
                # Only update admin credentials if name hasn't changed
                update_doc = {
                    "updated_at": datetime.utcnow()
                }
            
            # Update organization
            self.organizations_collection.update_one(
                {"_id": existing_org["_id"]},
                {"$set": update_doc}
            )
            
            # Update admin password if provided
            if update_data.password:
                self.auth_service.update_admin_password(
                    admin_id,
                    update_data.password
                )
            
            # Return updated organization
            updated_org = self.get_organization_by_name(
                update_data.organization_name
            )
            
            logger.info(f"Organization {old_org_name} updated successfully")
            return updated_org
            
        except Exception as e:
            logger.error(f"Error updating organization: {e}")
            return None
    
    def delete_organization(
        self,
        organization_name: str,
        admin_id: str
    ) -> bool:
        """
        Delete organization and its associated data
        
        Args:
            organization_name: Name of the organization
            admin_id: Admin ID performing the deletion
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            # Get organization
            org = self.get_organization_by_name(organization_name)
            
            if not org:
                logger.error(f"Organization {organization_name} not found")
                return False
            
            # Verify admin owns this organization
            if org["admin_id"] != admin_id:
                logger.error("Admin does not have permission to delete this organization")
                return False
            
            # Delete organization collection
            self.database_service.delete_collection(org["collection_name"])
            
            # Delete admin user
            self.auth_service.delete_admin(org["admin_id"])
            
            # Delete organization document
            result = self.organizations_collection.delete_one(
                {"_id": org["_id"]}
            )
            
            logger.info(f"Organization {organization_name} deleted successfully")
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting organization: {e}")
            return False
        
