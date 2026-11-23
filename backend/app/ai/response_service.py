"""
Response Service module for EduMentor AI Chatbot.
Normalizes, validates, and packages assistant responses to strictly preserve
the frontend contract: {"answer": str, "suggestions": [{"label": str, "prompt": str}]}.
"""

import re
from typing import Any

from app.ai.validators import parse_ai_response

# Chỉ cho phép duy nhất 3 URL chuẩn này xuất hiện trong câu trả lời
ALLOWED_URLS = {
    "http://localhost:5173/login",
    "http://localhost:5173/register",
    "http://localhost:5173/ai-learning-path",
    "https://localhost:5173/login",
    "https://localhost:5173/register",
    "https://localhost:5173/ai-learning-path",
}


def sanitize_links(text: str) -> str:
    """
    Quét và loại bỏ tất cả các link URL nội bộ tự chế / sai lệch (như /assessment/..., /courses/...).
    Nếu là link ngoài 3 link cho phép, thay thế bằng lời xin lỗi và hướng dẫn bấm Navbar.
    """
    def _replace_url(match: re.Match) -> str:
        url = match.group(0).rstrip(".,;:!?)`\"'")
        # Cho phép các link bên ngoài hợp lệ (ví dụ link tài liệu python.org, coursera... nếu có)
        # Nhưng cấm tuyệt đối mọi link localhost hoặc link giả mạo hệ thống EduMentor ngoài 3 link chuẩn
        if "localhost" in url or "127.0.0.1" in url or "edumentor" in url:
            if url in ALLOWED_URLS:
                return url
            return (
                "*(Đường dẫn trực tiếp hiện chưa khả dụng. "
                "Bạn vui lòng truy cập tính năng này qua thanh điều hướng Navbar phía trên màn hình nhé)*"
            )
        return url

    # Regex nhận diện URL bắt đầu bằng http:// hoặc https://
    url_pattern = re.compile(r"https?://[^\s<>`\"'()\]]+")
    cleaned_text = url_pattern.sub(_replace_url, text)
    return cleaned_text



class ResponseService:
    """
    Standardizes output format from any handler into the required frontend response contract.
    Handles single query formatting and multi-query aggregation.
    """

    @staticmethod
    def format_response(
        raw_output: str | dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Parses raw text or dictionary, validates structure, and applies sanitization.
        """
        if isinstance(raw_output, dict):
            answer = raw_output.get("answer")
            suggestions = raw_output.get("suggestions", [])
            if not isinstance(answer, str) or not answer.strip():
                answer = "Xin lỗi, tôi không thể xử lý câu trả lời lúc này."
            else:
                answer = sanitize_links(answer)
            if not isinstance(suggestions, list):
                suggestions = []

            cleaned_suggestions = []
            for item in suggestions[:3]:
                if isinstance(item, dict):
                    label = str(item.get("label", "")).strip()[:40]
                    prompt = str(item.get("prompt", "")).strip()
                    if label and prompt:
                        cleaned_suggestions.append(
                            {
                                "label": label,
                                "prompt": prompt,
                            }
                        )

            result = {
                "answer": answer,
                "suggestions": cleaned_suggestions,
            }
        elif isinstance(raw_output, str):
            try:
                result = parse_ai_response(raw_output)
                if "answer" in result and isinstance(result["answer"], str):
                    result["answer"] = sanitize_links(result["answer"])
            except Exception:  # noqa: BLE001
                result = {
                    "answer": sanitize_links(raw_output.strip() or "Đã tạo phản hồi thành công."),
                    "suggestions": [],
                }
        else:
            result = {
                "answer": "Đã xảy ra lỗi khi tạo phản hồi.",
                "suggestions": [],
            }

        if metadata:
            result["metadata"] = metadata

        return result

    @staticmethod
    def combine_responses(
        sub_responses: list[dict[str, Any]],
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Synthesizes multiple sub-query responses into a single cohesive frontend response.
        Preserves all successful sub-answers and aggregates top suggestions.
        """
        if not sub_responses:
            return {
                "answer": "Xin lỗi, không có phản hồi nào được tạo.",
                "suggestions": [],
            }

        if len(sub_responses) == 1:
            res = sub_responses[0]
            if metadata:
                res["metadata"] = metadata
            return res

        answer_parts: list[str] = []
        combined_suggestions: list[dict[str, str]] = []
        seen_prompts: set[str] = set()

        for sub in sub_responses:
            ans = str(sub.get("answer", "")).strip()
            if ans:
                answer_parts.append(ans)

            for s in sub.get("suggestions", []):
                if isinstance(s, dict):
                    prompt = str(s.get("prompt", "")).strip()
                    label = str(s.get("label", "")).strip()[:40]
                    if prompt and label and prompt not in seen_prompts:
                        seen_prompts.add(prompt)
                        combined_suggestions.append({"label": label, "prompt": prompt})

        unified_answer = (
            "\n\n---\n\n".join(answer_parts) if answer_parts else "Đã hoàn thành các yêu cầu của bạn."
        )

        result: dict[str, Any] = {
            "answer": unified_answer,
            "suggestions": combined_suggestions[:3],
        }
        if metadata:
            result["metadata"] = metadata

        return result


response_service = ResponseService()
