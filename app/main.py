from fastapi import FastAPI
from app.routes.organization import router as organization_router
from app.routes.auth import router as auth_router
from app.config import settings  # Import settings from config

app = FastAPI(
    title=settings.app_name,        # Use app name from settings
    version=settings.app_version,    # Use app version from settings
    debug=settings.debug             # Set debug flag based on environment variable
)

@app.get("/health")
def health_check():
    return {"status": "ok"}

# Include route modules
app.include_router(organization_router)
app.include_router(auth_router, prefix="/admin", tags=["Admin"])

