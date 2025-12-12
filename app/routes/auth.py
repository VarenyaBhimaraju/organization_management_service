from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import AuthService
from app.utils.security import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin Authentication"])


@router.post("/login")
async def admin_login(payload: dict, service: AuthService = Depends()):
    token = await service.login(payload)
    return token


@router.get("/me")
async def get_current_admin_info(admin=Depends(get_current_admin)):
    return admin
