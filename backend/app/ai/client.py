
import time
import logging

from google import genai
from google.genai import errors

from app.core.config import settings


logger = logging.getLogger(__name__)

# Client mặc định sử dụng API KEY trong file .env
client = genai.Client(api_key=settings.LLM_API_KEY)


def generate_text(prompt: str, api_key: str | None = None) -> str:
    """
    Gửi prompt đến Gemini và nhận nội dung phản hồi.

    Nếu có custom API key thì sử dụng key đó.
    Nếu không có thì sử dụng client mặc định.

    Tự động thử lại khi Gemini gặp lỗi ServerError.
    """

    # 1. Chọn Gemini Client
    if api_key and api_key.strip():
        call_client = genai.Client(api_key=api_key.strip())
    else:
        call_client = client

    # 2. Cấu hình số lần thử lại
    max_retries = 3

    # 3. Gọi Gemini
    for attempt in range(max_retries):

        try:
            response = call_client.models.generate_content(
                model=settings.LLM_MODEL,
                contents=prompt,
            )

            # 4. Kiểm tra nội dung phản hồi
            if not response.text:
                raise RuntimeError(
                    "Gemini không trả về nội dung."
                )

            return response.text

        except errors.ServerError as e:

            # Đã hết số lần thử
            if attempt == max_retries - 1:
                logger.error(
                    "Gemini ServerError sau %s lần thử: %s",
                    max_retries,
                    e,
                )
                raise

            # Thời gian chờ: 1s, 2s
            wait_time = 2 ** attempt

            logger.warning(
                "Gemini đang gặp lỗi ServerError. "
                "Thử lại lần %s/%s sau %s giây.",
                attempt + 1,
                max_retries,
                wait_time,
            )

            time.sleep(wait_time)
