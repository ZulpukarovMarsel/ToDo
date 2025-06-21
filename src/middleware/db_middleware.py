from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


class DBSessionMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, session_factory):
        super().__init__(app)
        self.session_factory = session_factory

    async def dispatch(self, request: Request, call_next):
        async with self.session_factory() as session:
            request.state.db = session
            response = await call_next(request)
            return response
