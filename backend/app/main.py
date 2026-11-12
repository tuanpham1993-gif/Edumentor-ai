

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
from app.routers.v1.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    print("Close app")

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url=f"{settings.API_STR}/docs",
    redoc_url=f"{settings.API_STR}/redoc",
    openapi_url=f"{settings.API_STR}/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_STR)

# GĐ7 (Tuấn): phục vụ ảnh đại diện đã upload tại /uploads/... (thư mục không commit — .gitignore)
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
