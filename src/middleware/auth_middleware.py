from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

from services.auth import AuthService


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        token = request.headers.get("Authorization")
        user = None
        if token:
            if token.startswith("Bearer "):
                token = token[7:]
            db = request.state.db
            user = await AuthService().get_user_from_token(token, db)
        request.state.user = user
        response = await call_next(request)
        return response
