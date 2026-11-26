"""Phần dùng chung của scripts/bank: nạp dữ liệu khóa, đường dẫn, thư mục kết quả chạy (KHÔNG commit)."""

import importlib
import json
import logging
from datetime import datetime
from pathlib import Path
from types import ModuleType

BACKEND = Path(__file__).resolve().parents[2]
BANK_DIR = BACKEND / "data" / "review"
# Kết quả chạy (sao lưu, kết quả đo Gemini, ảnh chụp điểm) — có thể chứa bài làm của học viên → .gitignore
RUNS_DIR = BACKEND / "data" / "bank_runs"
# Danh sách user ID tài khoản thử — file CỤC BỘ, .gitignore (mẫu: test_users.example.json)
TEST_USERS_FILE = Path(__file__).resolve().parent / "test_users.local.json"


def quiet() -> None:
    """Tắt log SQLAlchemy / app khi chạy công cụ (log echo của DB rất dài)."""
    logging.disable(logging.CRITICAL)


def load_course(course_id: int) -> ModuleType:
    return importlib.import_module(f"scripts.bank.courses.course_{course_id}")


def bank_path(course_id: int) -> Path:
    return BANK_DIR / f"course_{course_id}_en.json"


def load_bank(path: Path | str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def run_file(prefix: str, suffix: str = ".json") -> Path:
    """File kết quả mới trong data/bank_runs/: <prefix>_<YYYYmmdd-HHMMSS><suffix>."""
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    return RUNS_DIR / f"{prefix}_{datetime.now():%Y%m%d-%H%M%S}{suffix}"


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")
