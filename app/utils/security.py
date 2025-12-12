from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from app.config import settings
from app.models.admin import TokenData
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityManager:
    
    @staticmethod
    def hash_password(password: str) -> str:
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.jwt_expiration_minutes
            )
        
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.jwt_secret_key,
            algorithm=settings.jwt_algorithm
        )
        
        return encoded_jwt
    
    @staticmethod
    def decode_access_token(token: str) -> Optional[TokenData]:
        try:
            payload = jwt.decode(
                token,
                settings.jwt_secret_key,
                algorithms=[settings.jwt_algorithm]
            )
            
            admin_id: str = payload.get("admin_id")
            email: str = payload.get("email")
            organization_id: str = payload.get("organization_id")
            
            if admin_id is None or email is None or organization_id is None:
                return None
            
            return TokenData(
                admin_id=admin_id,
                email=email,
                organization_id=organization_id,
                exp=datetime.fromtimestamp(payload.get("exp"))
            )
        except JWTError:
            return None
        
        
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="admin/login")

def get_current_admin(token: str = Depends(oauth2_scheme)):
    token_data = security_manager.decode_access_token(token)
    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token_data


security_manager = SecurityManager()
