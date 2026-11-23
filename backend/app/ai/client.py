
import time
import logging

# Attempt to import Google Gemini SDK; fallback to dummy stub if unavailable
try:
    from google import genai
    from google.genai import errors
except Exception as import_err:  # pragma: no cover
    # Gemini SDK is not installed or cannot be imported.
    # Keep the module importable; raise a clear error only when generate_text is used.
    genai = None

    class _ServerError(Exception):
        pass

    class _APIError(Exception):
        pass

    errors = type("errors", (), {"ServerError": _ServerError, "APIError": _APIError})
    _GENAI_IMPORT_ERROR = import_err
else:
    _GENAI_IMPORT_ERROR = None

from app.core.config import settings


logger = logging.getLogger(__name__)

# Client mặc định sử dụng API KEY trong file .env
# If the real Gemini SDK is unavailable, use a dummy client that raises a clear error when called.
if genai is None:
    class _DummyClient:
        def __init__(self, *args, **kwargs):
            pass
        def models(self):
            raise RuntimeError("Gemini SDK not installed; cannot generate text.")
    client = _DummyClient()
else:
    client = genai.Client(api_key=settings.LLM_API_KEY)


def generate_text(prompt: str, api_key: str | None = None) -> str:
    """
    Gửi prompt đến Gemini và nhận nội dung phản hồi.

    Nếu có custom API key thì sử dụng key đó.
    Nếu không có thì sử dụng client mặc định từ settings.

    Tự động thử lại khi Gemini gặp lỗi ServerError hoặc RateLimit / tạm thời.
    """
    if genai is None:
        raise RuntimeError(
            f"Thư viện google-genai chưa được cài đặt hoặc import thất bại: {_GENAI_IMPORT_ERROR}. "
            f"Vui lòng cài đặt bằng `pip install google-genai`."
        )

    # 1. Chọn Gemini Client
    effective_key = (api_key or "").strip() or settings.LLM_API_KEY
    if not effective_key:
        raise RuntimeError("Chưa cấu hình API Key cho Gemini (LLM_API_KEY).")

    if api_key and api_key.strip():
        call_client = genai.Client(api_key=api_key.strip())
    else:
        call_client = client or genai.Client(api_key=settings.LLM_API_KEY)

    # 2. Cấu hình số lần thử lại
    max_retries = 3

    # 3. Gọi Gemini
    last_error = None
    for attempt in range(max_retries):
        try:
            response = call_client.models.generate_content(
                model=settings.LLM_MODEL,
                contents=prompt,
            )

            # 4. Kiểm tra nội dung phản hồi
            if not response or not response.text:
                raise RuntimeError("Gemini không trả về nội dung text.")

            return response.text

        except (errors.ServerError, errors.APIError, Exception) as e:
            last_error = e
            # Nếu là lỗi do SDK thiếu hoặc tham số cơ bản không hợp lệ thì không retry
            error_str = str(e).lower()
            is_transient = (
                "503" in error_str
                or "429" in error_str
                or "rate" in error_str
                or "overloaded" in error_str
                or "timeout" in error_str
                or isinstance(e, errors.ServerError)
            )

            if attempt == max_retries - 1 or not is_transient:
                logger.error(
                    "Lỗi gọi Gemini (lần thử %s/%s): %s",
                    attempt + 1,
                    max_retries,
                    e,
                )
                raise RuntimeError(f"Lỗi kết nối Gemini AI: {e}") from e

            wait_time = 2**attempt
            logger.warning(
                "Gemini gặp sự cố tạm thời (%s). Thử lại lần %s/%s sau %s giây.",
                e,
                attempt + 1,
                max_retries,
                wait_time,
            )
            time.sleep(wait_time)

    raise RuntimeError(f"Không thể kết nối đến Gemini AI sau {max_retries} lần thử: {last_error}")
