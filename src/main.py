import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from middleware.db_middleware import DBSessionMiddleware
from core.config import settings
from core.db import db_instance

@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_instance.create_database()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version="0.0.1",
    lifespan=lifespan,
)

if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.add_middleware(DBSessionMiddleware, session_factory=db_instance._async_session_maker)


@app.get("/")
async def root():
    return {"message": "Hello worlds!"}


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True,
                workers=1, limit_concurrency=100, limit_max_requests=1000)
