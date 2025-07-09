from fastapi import APIRouter

from app.api.routes import invoices, defaults

api_router = APIRouter()

# Include route modules
api_router.include_router(invoices.router, prefix="/invoices", tags=["invoices"])
api_router.include_router(defaults.router, prefix="/defaults", tags=["defaults"])