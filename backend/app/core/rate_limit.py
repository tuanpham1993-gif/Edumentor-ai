"""Giới hạn tần suất cho đăng nhập / đăng ký / quên & đặt lại mật khẩu (module 01 · Tuấn · 19/11/2026).

Lỗ hổng tìm thấy khi rà 16/11: không giới hạn số lần thử → dò mật khẩu, spam email đặt lại, tạo tài khoản hàng loạt.

Cách làm: cửa sổ trượt (sliding window) đếm số lần trong `window` giây, lưu TRONG BỘ NHỚ của tiến trình.
    - Đủ cho đồ án (backend chạy 1 tiến trình uvicorn, cả khi chạy Docker).
    - Nhiều tiến trình / nhiều máy → mỗi nơi đếm riêng; khi đó chuyển sang Redis (ghi ở "Hướng phát triển").
    - Khởi động lại server → bộ đếm về 0 (chấp nhận được).

Hai lớp cho đăng nhập:
    - THEO EMAIL (lớp chính, không giả mạo được): sai mật khẩu LOGIN_MAX_FAILURES lần trong cửa sổ → tạm khóa
      đăng nhập email đó tới khi lần sai cũ nhất ra khỏi cửa sổ. Đăng nhập đúng → xóa bộ đếm.
    - THEO IP (lớp phụ, ngưỡng rộng): chặn một máy thử nhiều tài khoản. IP lấy từ X-Real-IP do nginx đặt
      (frontend/nginx.conf); không có thì lấy địa chỉ kết nối.
"""

import math
import threading
import time
from collections import deque
from collections.abc import Callable

from fastapi import HTTPException, Request, status

from app.core.config import settings


class RateLimiter:
    """Đếm số sự kiện của mỗi khóa trong `window` giây gần nhất (cửa sổ trượt)."""

    def __init__(self, limit: int, window: float, clock: Callable[[], float] = time.monotonic):
        self.limit = limit
        self.window = window
        self.clock = clock
        self._events: dict[str, deque[float]] = {}
        self._lock = threading.Lock()

    def _trim(self, key: str, now: float) -> deque[float]:
        events = self._events.get(key)
        if events is None:
            return deque()
        while events and events[0] <= now - self.window:
            events.popleft()
        if not events:
            self._events.pop(key, None)
        return events

    def retry_after(self, key: str) -> float:
        """0 nếu còn được phép; ngược lại số giây phải chờ tới khi lần cũ nhất ra khỏi cửa sổ."""
        with self._lock:
            now = self.clock()
            events = self._trim(key, now)
            if len(events) < self.limit:
                return 0.0
            return max(0.0, events[0] + self.window - now)

    def hit(self, key: str) -> None:
        with self._lock:
            now = self.clock()
            self._trim(key, now)
            self._events.setdefault(key, deque()).append(now)

    def reset(self, key: str) -> None:
        with self._lock:
            self._events.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._events.clear()


MINUTE = 60.0

# Ngưỡng (chốt 19/11): đủ rộng cho người dùng thật gõ nhầm, đủ chặt để dò mật khẩu / spam email không hiệu quả.
login_failures_by_email = RateLimiter(limit=5, window=15 * MINUTE)  # sai 5 lần / 15 phút → khóa tạm email đó
login_by_ip = RateLimiter(limit=30, window=15 * MINUTE)  # mọi lần thử đăng nhập từ một IP
register_by_ip = RateLimiter(limit=5, window=60 * MINUTE)
forgot_by_email = RateLimiter(limit=3, window=15 * MINUTE)  # chống spam email đặt lại cho một người
forgot_by_ip = RateLimiter(limit=10, window=60 * MINUTE)
reset_by_ip = RateLimiter(limit=10, window=15 * MINUTE)
# 19/11 (module 09): ôn tập KHÔNG giới hạn số lần; chỉ bắt 2 lần nộp của một người cách nhau ≥ REVIEW_SUBMIT_COOLDOWN
# giây — chặn công cụ nộp tự động làm cạn lượt Gemini (mỗi lần nộp chấm 3 câu tự luận). Người thật làm 15 câu mất
# vài phút nên không chạm tới.
review_submit_by_user = RateLimiter(limit=1, window=settings.REVIEW_SUBMIT_COOLDOWN)

ALL_LIMITERS = (
    login_failures_by_email,
    login_by_ip,
    register_by_ip,
    forgot_by_email,
    forgot_by_ip,
    reset_by_ip,
    review_submit_by_user,
)


def client_ip(request: Request) -> str:
    real_ip = request.headers.get("x-real-ip", "").strip()
    if real_ip:
        return real_ip
    return request.client.host if request.client else "unknown"


def email_key(email: str) -> str:
    return email.strip().lower()


def too_many(seconds: float) -> HTTPException:
    minutes = max(1, math.ceil(seconds / MINUTE))
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=f"Bạn đã thử quá nhiều lần. Vui lòng thử lại sau {minutes} phút.",
        headers={"Retry-After": str(math.ceil(seconds))},
    )


def enforce(limiter: RateLimiter, key: str, *, count: bool = True) -> None:
    """Vượt ngưỡng → 429 (kèm Retry-After). count=True: tính lần này vào bộ đếm."""
    if not settings.RATE_LIMIT_ENABLED:
        return
    wait = limiter.retry_after(key)
    if wait > 0:
        raise too_many(wait)
    if count:
        limiter.hit(key)


def _mm_ss(seconds: float) -> str:
    total = max(1, math.ceil(seconds))
    minutes, secs = divmod(total, 60)
    if minutes and secs:
        return f"{minutes} phút {secs} giây"
    return f"{minutes} phút" if minutes else f"{secs} giây"


def check_review_submit(user_id: int) -> None:
    """Vừa nộp bài chưa đủ REVIEW_SUBMIT_COOLDOWN giây → 429 "Bạn vừa nộp bài, vui lòng chờ…". Không đếm lần này."""
    if not settings.RATE_LIMIT_ENABLED or settings.REVIEW_SUBMIT_COOLDOWN <= 0:
        return
    review_submit_by_user.window = settings.REVIEW_SUBMIT_COOLDOWN  # đọc lại cấu hình (test đổi được)
    wait = review_submit_by_user.retry_after(str(user_id))
    if wait > 0:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Bạn vừa nộp bài, vui lòng chờ. Còn {_mm_ss(wait)} để nộp lần sau.",
            headers={"Retry-After": str(math.ceil(wait))},
        )


def record_review_submit(user_id: int) -> None:
    """Gọi SAU khi nộp thành công (đã chấm / đang chấm) — nộp lỗi không tính."""
    if settings.RATE_LIMIT_ENABLED and settings.REVIEW_SUBMIT_COOLDOWN > 0:
        review_submit_by_user.hit(str(user_id))
