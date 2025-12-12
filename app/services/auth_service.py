from app.database.mongodb import mongodb
from app.models.admin import AdminCreate, AdminLogin, TokenResponse, AdminInDB
from app.utils.security import security_manager
from app.config import settings
from datetime import datetime, timedelta
from typing import Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        self.db = mongodb.get_database()
        self.admins_collection = self.db["admins"]
        self._ensure_indexes()
    
    def _ensure_indexes(self):
        """Ensure required indexes exist"""
        # Create unique index on email
        self.admins_collection.create_index("email", unique=True)
        # Create index on organization_id
        self.admins_collection.create_index("organization_id")
    
    def create_admin(self, admin_data: AdminCreate) -> Optional[str]:
        """
        Create a new admin user
        
        Args:
            admin_data: Admin creation data
            
        Returns:
            Admin ID if created successfully, None otherwise
        """
        try:
            # Check if admin with email already exists
            logger.info(f"Checking if admin with email {admin_data.email} already exists...")
            existing_admin = self.admins_collection.find_one({"email": admin_data.email})
            
            if existing_admin:
                logger.warning(f"Admin with email {admin_data.email} already exists. ID: {existing_admin['_id']}")
                return None

            # Hash password
            logger.info(f"Hashing password for admin with email: {admin_data.email}")
            hashed_password = security_manager.hash_password(admin_data.password)
            logger.info(f"Password hashed successfully for {admin_data.email}")

            # Create admin document
            admin_doc = {
                "email": admin_data.email,
                "hashed_password": hashed_password,
                "organization_id": admin_data.organization_id,
                "created_at": datetime.utcnow(),
                "is_active": True
            }

            # Insert admin into the database
            logger.info(f"Inserting admin document into database: {admin_doc}")
            result = self.admins_collection.insert_one(admin_doc)
            
            # Verify that the admin was inserted
            if not result.acknowledged:
                logger.error(f"Failed to insert admin with email {admin_data.email}")
                return None
            
            logger.info(f"Admin created successfully with ID: {result.inserted_id}")
            return str(result.inserted_id)
        
        except Exception as e:
            logger.error(f"Error creating admin: {e}")
            return None

    
    def authenticate_admin(self, login_data: AdminLogin) -> Optional[dict]:
        """
        Authenticate an admin user
        
        Args:
            login_data: Login credentials
            
        Returns:
            Admin document if authenticated, None otherwise
        """
        try:
            # Find admin by email
            admin = self.admins_collection.find_one({"email": login_data.email})
            
            if not admin:
                logger.warning(f"Admin not found: {login_data.email}")
                return None
            
            # Verify password
            if not security_manager.verify_password(
                login_data.password,
                admin["hashed_password"]
            ):
                logger.warning(f"Invalid password for admin: {login_data.email}")
                return None
            
            # Check if admin is active
            if not admin.get("is_active", True):
                logger.warning(f"Inactive admin attempted login: {login_data.email}")
                return None
            
            return admin
        except Exception as e:
            logger.error(f"Error authenticating admin: {e}")
            return None
    
    def generate_token(self, admin: dict) -> TokenResponse:
        """
        Generate JWT token for authenticated admin
        
        Args:
            admin: Admin document from database
            
        Returns:
            TokenResponse with access token
        """
        token_data = {
            "admin_id": str(admin["_id"]),
            "email": admin["email"],
            "organization_id": admin["organization_id"]
        }
        
        expires_delta = timedelta(minutes=settings.jwt_expiration_minutes)
        access_token = security_manager.create_access_token(
            data=token_data,
            expires_delta=expires_delta
        )
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.jwt_expiration_minutes * 60  # in seconds
        )
    
    def get_admin_by_id(self, admin_id: str) -> Optional[dict]:
        """
        Get admin by ID
        
        Args:
            admin_id: Admin ID
            
        Returns:
            Admin document if found, None otherwise
        """
        try:
            admin = self.admins_collection.find_one({"_id": ObjectId(admin_id)})
            return admin
        except Exception as e:
            logger.error(f"Error getting admin by ID: {e}")
            return None
    
    def get_admin_by_email(self, email: str) -> Optional[dict]:
        """
        Get admin by email
        
        Args:
            email: Admin email
            
        Returns:
            Admin document if found, None otherwise
        """
        try:
            admin = self.admins_collection.find_one({"email": email})
            return admin
        except Exception as e:
            logger.error(f"Error getting admin by email: {e}")
            return None
    
    def update_admin_password(
        self,
        admin_id: str,
        new_password: str
    ) -> bool:
        """
        Update admin password
        
        Args:
            admin_id: Admin ID
            new_password: New password
            
        Returns:
            True if updated successfully, False otherwise
        """
        try:
            hashed_password = security_manager.hash_password(new_password)
            
            result = self.admins_collection.update_one(
                {"_id": ObjectId(admin_id)},
                {"$set": {"hashed_password": hashed_password}}
            )
            
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating admin password: {e}")
            return False
    
    def delete_admin(self, admin_id: str) -> bool:
        """
        Delete an admin user
        
        Args:
            admin_id: Admin ID
            
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            result = self.admins_collection.delete_one({"_id": ObjectId(admin_id)})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting admin: {e}")
            return False
