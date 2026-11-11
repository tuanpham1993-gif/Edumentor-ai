

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers.v1.api import api_router
from app.core.config import settings
from app.core.database import init_db
import httpx
import os

import logging

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    app.state.llm_client = httpx.AsyncClient(
        base_url=settings.LLM_URL_ADAPTER,
        timeout=180.0
    )

    app.state.llm_client_base = httpx.AsyncClient(
        base_url=settings.LLM_URL_BASE,
        timeout=180.0
    )
    yield
    await app.state.llm_client_base.aclose()
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