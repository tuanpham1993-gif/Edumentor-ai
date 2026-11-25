
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.core.database import init_db
import httpx
import os

import logging
from app.routers.v1.api import api_router
from app.services.review_rag_service import warm_up_in_background
from app.services import review_due_service, review_generation_service, skill_search_service
from app.core.database import SessionLocal


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Khởi tạo database
    init_db()
    warm_up_in_background()  # Tuấn 12/11: nạp sẵn mô hình embedding (ôn tập) ở luồng nền
    review_due_service.start_background(SessionLocal)  # Tuấn 21/11: nhắc "Đến hạn ôn" (chuông + email), Q12
    review_generation_service.recover_on_startup(SessionLocal)  # Tuấn 25/11 (G3d): việc soạn đề dở → 'failed'
    skill_search_service.warm_up_in_background(SessionLocal)  # Tuấn 21/11 (G1): vector tên kỹ năng, thiếu thì tính
    app.state.llm_client = httpx.AsyncClient(
        base_url=settings.LLM_URL_ADAPTER,
        timeout=180.0
    )
    yield
    review_due_service.stop_background()
    await app.state.llm_client.aclose()
    print("Close app")


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

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
