from fastapi import APIRouter, Depends, HTTPException
from app.services.organization_service import OrganizationService
from app.models.organization import OrganizationCreate, OrganizationUpdate
from app.utils.security import get_current_admin

router = APIRouter(prefix="/org", tags=["Organization"])


@router.post("/create", status_code=201)
async def create_organization(
    payload: OrganizationCreate,
    service: OrganizationService = Depends(),
):
    org = service.create_organization(payload)
    if not org:
        raise HTTPException(status_code=400, detail="Organization already exists")
    return org


@router.get("/get")
async def get_organization(
    organization_name: str,
    service: OrganizationService = Depends(),
):
    org = service.get_organization_by_name(organization_name)
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    return org


@router.put("/update")
async def update_organization(
    old_org_name: str,
    payload: OrganizationUpdate,
    admin=Depends(get_current_admin),
    service: OrganizationService = Depends(),
):
    updated = service.update_organization(old_org_name, payload, admin["id"])
    if not updated:
        raise HTTPException(status_code=400, detail="Update failed")
    return updated


@router.delete("/delete")
async def delete_organization(
    organization_name: str,
    admin=Depends(get_current_admin),
    service: OrganizationService = Depends(),
):
    deleted = service.delete_organization(organization_name, admin["id"])
    if not deleted:
        raise HTTPException(status_code=400, detail="Delete failed")
    return {"success": True}
