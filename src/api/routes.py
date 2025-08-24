from fastapi import APIRouter

from .endpoints.users import router as user_router
from .endpoints.auth import router as auth_router
from .endpoints.roles import router as role_router


router = APIRouter(prefix="/api")
router_list = [
    auth_router,
    user_router,
    role_router
]

for r in router_list:
    router.include_router(r)
