from fastapi import APIRouter
from app.api.endpoints import health, shares

api_router = APIRouter()

# Register sub-routers
api_router.include_router(health.router, prefix="/health", tags=["Health"])
api_router.include_router(shares.router, prefix="/shares", tags=["Shares"])
