import logging
import smtplib
from email.message import EmailMessage

from app.core.config import settings

logger = logging.getLogger(__name__)


def _smtp_configured() -> bool:
    return bool(settings.SMTP_HOST) and "example.com" not in settings.SMTP_HOST


def send_email(to: str, subject: str, body: str) -> None:
    """Gửi email. Chưa cấu hình SMTP → in ra terminal (chế độ dev)."""
    if not _smtp_configured():
        print("=" * 60)
        print(f"[DEV EMAIL] Tới: {to}")
        print(f"[DEV EMAIL] Tiêu đề: {subject}")
        print(body)
        print("=" * 60)
        return

    message = EmailMessage()
    message["From"] = settings.SMTP_USER
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(message)
    except (smtplib.SMTPException, OSError):
        # Gửi lỗi KHÔNG được làm hỏng request; chỉ ghi log (không ghi nội dung chứa token)
        logger.exception("Gửi email tới %s thất bại", to)


def send_password_reset_email(to: str, token: str) -> None:
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    minutes = settings.RESET_TOKEN_EXPIRE_MINUTES
    body = (
        "Xin chào,\n\n"
        "Bạn vừa yêu cầu đặt lại mật khẩu cho tài khoản EduMentor AI.\n"
        f"Nhấn vào liên kết sau để đặt mật khẩu mới:\n{link}\n\n"
        f"Liên kết có hiệu lực trong {minutes} phút, chỉ dùng một lần.\n"
        "Nếu bạn không yêu cầu, hãy bỏ qua email này."
    )
    send_email(to, "EduMentor AI — Đặt lại mật khẩu", body)


def send_review_result_email(
    to: str,
    full_name: str,
    course_title: str,
    score: float,
    passed: bool,
    completed_course: bool,
    attempt_id: int,
) -> None:
    """Email kết quả ôn tập (module 09 · GĐ3). Router gửi SAU khi kết quả đã lưu; lỗi gửi chỉ ghi log."""
    link = f"{settings.FRONTEND_URL}/review/{attempt_id}/result"
    verdict = "ĐẠT" if passed else "CHƯA ĐẠT"
    lines = [
        f"Xin chào {full_name},\n",
        f"Bạn vừa nộp bài ôn tập khóa học \"{course_title}\".",
        f"Điểm: {score:g}/10 — {verdict} (ngưỡng đạt {settings.REVIEW_PASS_SCORE:g}/10).",
    ]
    if completed_course:
        lines.append("Chúc mừng! Khóa học đã chuyển sang Hoàn thành và các kỹ năng của khóa đã thành \"Đã biết\".")
    elif not passed:
        lines.append("Bạn có thể ôn lại bất cứ lúc nào — mỗi lần là một đề mới.")
    lines.append(f"\nXem chi tiết từng câu: {link}")
    send_email(to, f"EduMentor AI — Kết quả ôn tập: {verdict} ({score:g}/10)", "\n".join(lines))
