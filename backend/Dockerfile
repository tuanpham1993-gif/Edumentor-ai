# Backend EduMentor AI (FastAPI) — Tuấn · 13/11/2026.
# Build + chạy từ gốc dự án:   docker compose up -d --build postgres qdrant backend
#
# Cấu trúc trong container giữ giống trên máy (code tìm file theo đường dẫn tương đối):
#   /app/backend   ← code trong thư mục này (WORKDIR)
#   /app/datajson  ← dữ liệu seed của Hòa — KHÔNG chép vào image, docker-compose gắn ./datajson vào khi chạy
# Không chép .env vào image: biến môi trường do docker-compose truyền (env_file + environment).

FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    HF_HOME=/cache/huggingface

WORKDIR /app/backend

# 1) torch bản CPU trước (bản mặc định kéo theo CUDA, nặng vài GB) — tách lớp riêng để sửa code không phải cài lại
RUN pip install --index-url https://download.pytorch.org/whl/cpu torch

# 2) Thư viện còn lại — chỉ cài lại khi requirements.txt đổi
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

# 3) Code
COPY . /app/backend/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
