"""AI thật cho module 09 — Google Gemini (giai đoạn 2, AI_MODE=real) (Tuấn · 12/11/2026).

Cùng khuôn ReviewAI với MockAI → review_service không cần biết đang dùng AI nào.
  - grade_essay        : Gemini chấm TỪNG ý barem theo NGHĨA (không dò từ khóa) → full / none + câu trích (15/11: bỏ mức ½).
                         Điểm của ý do CODE tính từ kết quả (đủ / ½ / 0) — không để AI tự cộng điểm.
  - generate_questions : ngân hàng của kỹ năng đã đủ REVIEW_BANK_TARGET_PER_SKILL câu → bốc từ ngân hàng như mock
                         (không tốn lượt gọi, không làm loãng câu đã duyệt — ngân hàng bước 3, chốt 09/11);
                         chưa đủ → Gemini soạn câu mới theo đúng prompt RAG đã dựng (validator kiểm lại ở service).
Lỗi mạng / hết lượt / quá thời gian / trả sai định dạng → AIUnavailableError → service tự dùng dự phòng
(ngân hàng câu hỏi khi sinh đề; chấm theo từ khóa khi chấm bài).

B7 (15/11): chấm có cấu trúc — prompt theo ngôn ngữ (ai/prompts/review_grading.py: grade-en-v1 / grade-vi-v1),
`responseSchema` + kiểm lại bằng Pydantic (ai/review/grading_schema.py); thêm reason từng ý + feedback;
kết quả sai khung (AIOutputError) → thử lại 1 lần (lỗi mạng / quá giờ thì KHÔNG thử lại — người học đang chờ).

Gọi REST bằng httpx (đã có sẵn) — không thêm thư viện. Biến .env (12/11 — Tuấn và Tâm mỗi người một model):
    REVIEW_LLM_MODEL    model của Ôn tập (gemini-3.5-flash-lite) — để trống thì dùng LLM_MODEL của chatbot
    REVIEW_LLM_API_KEY  khóa riêng cho Ôn tập (không bắt buộc) — để trống thì dùng LLM_API_KEY chung
Dữ liệu gửi đi CHỈ gồm: đề, barem, bài làm (chấm) / đoạn tri thức (sinh đề). KHÔNG gửi tên, email, CCCD.
"""

import json
import random
import time

import httpx

from app.ai.prompts.review_grading import grading_prompt
from app.ai.review.base import (
    AIUnavailableError,
    EssayGrade,
    GenerationRequest,
    ReviewAI,
)
from app.ai.review.grading_schema import (
    GEMINI_RESPONSE_SCHEMA,
    AIOutputError,
    parse_grading,
)
from app.ai.review.mock_ai import pick_from_bank
from app.ai.review.validator import GRADE_RESULTS
from app.core.config import settings

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
RESULT_POINTS = GRADE_RESULTS  # full = đủ điểm ý, none = 0

GRADE_RETRIES = 1  # kết quả sai khung → gọi lại tối đa 1 lần (docs/Review-AI-Grading.md B7)
# 17/11: Gemini quá tải (503) một lần là rơi về chấm từ khóa — chạy thật gặp ngay ở lượt 63.
# Lỗi TẠM THỜI phía Google (5xx) / rớt kết nối → gọi lại sau 1 s rồi 2 s. KHÔNG gọi lại 429 (hết hạn mức,
# gọi nữa chỉ phí lượt) và quá thời gian chờ (đã tiêu hết ngân sách chờ chấm).
TRANSIENT_STATUS = {500, 502, 503, 504}
TRANSIENT_DELAYS = (1.0, 2.0)
_sleep = time.sleep  # test thay bằng hàm không chờ


def review_llm() -> tuple[str, str]:
    """(khóa, model) Ôn tập dùng: REVIEW_LLM_* nếu đặt, không thì LLM_* chung với chatbot."""
    key = settings.REVIEW_LLM_API_KEY.strip() or settings.LLM_API_KEY.strip()
    model = settings.REVIEW_LLM_MODEL.strip() or settings.LLM_MODEL.strip()
    return key, model


def _settings_ok() -> tuple[str, str]:
    key, model = review_llm()
    if not key or not model:
        raise AIUnavailableError("Chưa cấu hình LLM_API_KEY / LLM_MODEL (hoặc REVIEW_LLM_*) trong .env")
    return key, model


def _extract_json(text: str):
    """Gemini đôi khi bọc JSON trong ```json … ``` — bóc ra rồi parse."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        text = text.rsplit("```", 1)[0]
    return json.loads(text)


class RealAI(ReviewAI):
    name = "gemini"

    def __init__(self, *, timeout: float | None = None, transport: httpx.BaseTransport | None = None):
        # Sinh đề: người học đang chờ ở nút "Bắt đầu" → chờ ngắn (REVIEW_GRADING_TIMEOUT), lỗi thì dùng ngân hàng.
        # Chấm bài: chạy song song, quá 20 giây bài chuyển "Đang chấm" và chấm tiếp ở nền (T1) → cho Gemini chờ
        # tới REVIEW_GRADING_MAX_WAIT để vẫn chấm theo nghĩa; quá nữa mới rơi về chấm từ khóa.
        self.timeout = timeout if timeout is not None else float(settings.REVIEW_GRADING_TIMEOUT)
        self.grading_timeout = timeout if timeout is not None else float(settings.REVIEW_GRADING_MAX_WAIT)
        self._transport = transport  # test truyền transport giả → không gọi mạng thật

    # ─────────────── gọi Gemini ───────────────

    def _post(self, url: str, key: str, body: dict, timeout: float) -> httpx.Response:
        """Gửi 1 request; lỗi tạm thời (5xx, rớt kết nối) → gọi lại theo TRANSIENT_DELAYS."""
        for delay in (*TRANSIENT_DELAYS, None):
            try:
                with httpx.Client(timeout=timeout, transport=self._transport) as client:
                    response = client.post(url, headers={"x-goog-api-key": key}, json=body)
            except httpx.TimeoutException as err:  # chậm quá → không gọi lại
                raise AIUnavailableError(f"Gọi Gemini lỗi: {type(err).__name__}") from None
            except httpx.HTTPError as err:  # mất mạng / rớt kết nối
                if delay is None:
                    raise AIUnavailableError(f"Gọi Gemini lỗi: {type(err).__name__}") from None
            else:
                if response.status_code not in TRANSIENT_STATUS or delay is None:
                    return response
            _sleep(delay)
        raise AssertionError("unreachable")  # pragma: no cover

    def _call(
        self,
        system_prompt: str,
        user_prompt: str,
        *,
        temperature: float,
        timeout: float | None = None,
        schema: dict | None = None,
    ):
        key, model = _settings_ok()
        config = {"responseMimeType": "application/json", "temperature": temperature}
        if schema is not None:
            config["responseSchema"] = schema  # structured output: Gemini buộc trả đúng khung
        body = {
            "systemInstruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": config,
        }
        response = self._post(API_URL.format(model=model), key, body, timeout or self.timeout)
        if response.status_code != 200:
            try:
                status = response.json().get("error", {}).get("status", "")
            except ValueError:
                status = ""
            raise AIUnavailableError(f"Gemini trả HTTP {response.status_code} {status}".strip())
        try:
            text = response.json()["candidates"][0]["content"]["parts"][0]["text"]
            return _extract_json(text)
        except (KeyError, IndexError, ValueError, TypeError):
            raise AIOutputError("Gemini trả về không phải JSON hợp lệ") from None

    # ─────────────── phân loại phạm vi kỹ năng (G3.0, 24/11) ───────────────

    def classify_skills(self, items: list[dict], *, timeout: float = 120.0):
        """Một lô kỹ năng → JSON thô {"results": [...]} (skill_scope_service kiểm lại bằng parse_scope).
        temperature 0 (cùng đầu vào → cùng nhãn); lô 100 kỹ năng trả chậm hơn chấm bài → timeout riêng."""
        from app.ai.prompts.review_scope import SCOPE_SYSTEM_PROMPT, build_scope_prompt
        from app.ai.review.scope_schema import GEMINI_SCOPE_SCHEMA

        return self._call(
            SCOPE_SYSTEM_PROMPT, build_scope_prompt(items), temperature=0.0, timeout=timeout, schema=GEMINI_SCOPE_SCHEMA
        )

    # ─────────────── viết đoạn tri thức (G3a, 24/11) ───────────────

    def write_knowledge(
        self, skill: str, courses: list[dict], n: int, existing_titles: list[str], feedback: list[str], *, timeout=120.0
    ):
        """→ JSON thô {"passages": [...]} (knowledge_service kiểm lại bằng check_passages). temperature 0,3: viết tự nhiên
        nhưng ít bịa; feedback = lỗi lần trước (viết lại có phản hồi — phase 02 của thầy)."""
        from app.ai.prompts.review_knowledge import KNOWLEDGE_SYSTEM_PROMPT, build_knowledge_prompt
        from app.ai.review.knowledge_schema import GEMINI_KNOWLEDGE_SCHEMA

        prompt = build_knowledge_prompt(skill, courses, n, existing_titles)
        if feedback:
            prompt += "\n\nYOUR PREVIOUS ATTEMPT WAS REJECTED BECAUSE:\n- " + "\n- ".join(feedback)
        return self._call(
            KNOWLEDGE_SYSTEM_PROMPT, prompt, temperature=0.3, timeout=timeout, schema=GEMINI_KNOWLEDGE_SCHEMA
        )

    # ─────────────── soạn câu ôn theo kỹ năng (G3b, 25/11) ───────────────

    def write_questions(
        self,
        skill: str,
        passages: list[dict],
        kind: str,
        need: dict[str, int],
        existing: list[str],
        feedback: list[str],
        *,
        used: list[str] = (),
        timeout: float = 120.0,
    ):
        """→ JSON thô {"questions": [...]} (question_gen_service kiểm lại bằng check_questions). kind: "mcq" | "essay".
        temperature 0,5: câu đa dạng nhưng bám tài liệu; feedback = lỗi lần trước (soạn lại có phản hồi — phase 02)."""
        from app.ai.prompts.review_generate import GEN_SYSTEM_PROMPT, build_question_prompt
        from app.ai.review.question_schema import GEMINI_QUESTION_SCHEMAS

        prompt = build_question_prompt(skill, passages, need, existing, feedback, used)  # used: Bước A (gen-en-v5)
        return self._call(
            GEN_SYSTEM_PROMPT, prompt, temperature=0.5, timeout=timeout, schema=GEMINI_QUESTION_SCHEMAS[kind]
        )

    def solve_mcqs(self, skill: str, items: list[dict], *, timeout: float = 120.0):
        """Cổng G3c — giải mù: → JSON thô {"answers": [{"id", "index"}]} (question_gate kiểm lại). temperature 0."""
        from app.ai.prompts.review_solve import GEMINI_SOLVE_SCHEMA, SOLVE_SYSTEM_PROMPT, build_solve_prompt

        return self._call(
            SOLVE_SYSTEM_PROMPT, build_solve_prompt(skill, items), temperature=0.0, timeout=timeout,
            schema=GEMINI_SOLVE_SCHEMA,
        )  # fmt: skip

    # ─────────────── chấm tự luận ───────────────

    def grade_essay(self, question: dict, answer: str | None) -> list[dict]:
        return self.grade_essay_detailed(question, answer).items

    def grade_essay_detailed(self, question: dict, answer: str | None) -> EssayGrade:
        rubric = question["rubric"]
        if not (answer and answer.strip()):
            return EssayGrade(items=[{"result": "none", "points": 0.0, "evidence": None} for _ in rubric])
        system_prompt, user_prompt, version = grading_prompt(question, answer)
        attempts = 0
        while True:
            attempts += 1
            try:
                data = self._call(
                    system_prompt,
                    user_prompt,
                    temperature=0,
                    timeout=self.grading_timeout,
                    schema=GEMINI_RESPONSE_SCHEMA,
                )
                out = parse_grading(data, len(rubric))
                break
            except AIOutputError as err:  # sai khung → thử lại; lỗi mạng / HTTP (AIUnavailableError) đi thẳng ra
                if attempts > GRADE_RETRIES:
                    raise AIOutputError(f"{err} (sau {attempts} lần gọi)", attempts=attempts) from None
        results = []
        for graded, item in zip(out.items, rubric, strict=True):
            # Câu trích giữ nguyên — khối 5 Verifier (pipeline/essay.py) kiểm có thật trong bài hay không (B8)
            evidence = graded.evidence.strip() if isinstance(graded.evidence, str) and graded.evidence.strip() else None
            results.append(
                {
                    "result": graded.result,
                    "points": RESULT_POINTS[graded.result] * float(item["max_points"]),
                    "evidence": evidence,
                    "reason": graded.reason or None,
                }
            )
        return EssayGrade(items=results, feedback=out.feedback, prompt_version=version, attempts=attempts)

    # ─────────────── sinh câu hỏi ───────────────

    def generate_questions(self, request: GenerationRequest, rng: random.Random) -> list[dict]:
        if len(request.candidates) + request.pending_count >= settings.REVIEW_BANK_TARGET_PER_SKILL:
            # Ngân hàng đủ → không gọi AI (bước 3: chỉ sinh khi kỹ năng còn thiếu câu). Câu đang chờ duyệt cũng
            # tính (7.5c) — nếu không, mỗi lượt làm bài lại bắt AI soạn thêm câu chờ duyệt trùng nhau.
            return pick_from_bank(
                request.candidates,
                request.need,
                rng,
                prefer_chunk_ids={c.chunk_id for c in request.chunks},
                avoid_question_ids=request.avoid_question_ids,
            )
        return self.generate_new(request)

    def generate_new(self, request: GenerationRequest) -> list[dict]:
        """Gemini soạn câu MỚI theo prompt RAG (request.system_prompt + request.prompt). Chưa kiểm — service kiểm."""
        data = self._call(request.system_prompt, request.prompt, temperature=0.7)
        if not isinstance(data, list):
            raise AIUnavailableError("Gemini không trả về mảng câu hỏi")
        chunk_id = request.chunks[0].chunk_id if request.chunks else None
        return [{**q, "chunk_id": q.get("chunk_id") or chunk_id} for q in data if isinstance(q, dict)]
