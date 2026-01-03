from fastapi import APIRouter
from .views import router


admin_router = APIRouter()
admin_router.include_router(router)

__all__ = (
    "admin_router",
)