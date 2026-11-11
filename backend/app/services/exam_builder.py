"""Khung đề ôn tập (A1, A2, A13 — chốt 09/11) (module 09 · Tuấn · GĐ2, 09/11/2026).

Hàm thuần (không DB) → test kỹ được:
    plan_exam(...)    quyết định MỖI KỸ NĂNG cần bao nhiêu câu ở MỖI MỨC ĐỘ
    order_exam(...)   xếp thứ tự câu trên đề + xáo thứ tự 4 lựa chọn

Khung 15 câu: 6 TN Nhận biết + 6 TN Thông hiểu + 2 TL dễ + 1 TL nâng cao.
  - Mọi kỹ năng của khóa phải có câu TN trong ngân hàng, thiếu → "Chưa có đề ôn tập" (sửa 11/11).
  - Mỗi kỹ năng ≥ 1 câu TN (khóa > 12 kỹ năng → chọn 12, ưu tiên kỹ năng lượt trước CHƯA hỏi).
  - TN chia đều giữa các kỹ năng; 3 câu TL ưu tiên 3 kỹ năng khác nhau.
  - Ngẫu nhiên trong từng lựa chọn (rng truyền vào → test lặp lại được).
"""

import random
from collections import defaultdict

STRUCTURE = {"recognize": 6, "understand": 6, "easy": 2, "advanced": 1}
MCQ_LEVELS = ("recognize", "understand")
TOTAL_QUESTIONS = sum(STRUCTURE.values())  # 15
MAX_POINTS = {"recognize": 0.5, "understand": 0.5, "easy": 1.0, "advanced": 2.0}  # thang 10 (A11)


class NotEnoughQuestionsError(Exception):
    """Ngân hàng không đủ câu để ráp đúng khung → "Chưa có đề ôn tập"."""


Plan = dict[int, dict[str, int]]  # {skill_id: {level: số câu}}


def plan_exam(
    skill_ids: list[int],
    available: dict[tuple[int, str], int],
    rng: random.Random,
    *,
    previous_skill_ids: set[int] | None = None,
    fresh: dict[tuple[int, str], int] | None = None,
) -> Plan:
    """available[(skill_id, level)] = số câu đang có trong ngân hàng. Không đủ → NotEnoughQuestionsError.

    fresh[(skill_id, level)] = số câu CHƯA dùng ở lượt trước (mặc định = available). Khi phải chọn giữa
    các kỹ năng, ưu tiên chỗ còn câu mới → lượt sau ít lặp câu (A1). Không đủ câu mới thì vẫn lặp.
    """
    cap = defaultdict(int, available)
    unused = defaultdict(int, available if fresh is None else fresh)

    # 0) A1: MỌI kỹ năng của khóa phải có câu trắc nghiệm trong ngân hàng. Thiếu một kỹ năng → chưa có đề
    #    (nếu không, khóa nhiều kỹ năng ra đề toàn câu của 1–2 kỹ năng, đạt là Hoàn thành + "Đã biết" cả
    #    những kỹ năng chưa hề hỏi — phát hiện 11/11 khi ngân hàng 312 lên 100 câu: 197 khóa bị ảnh hưởng).
    missing = [s for s in skill_ids if not any(cap[(s, lv)] > 0 for lv in MCQ_LEVELS)]
    if missing:
        raise NotEnoughQuestionsError(f"Kỹ năng chưa có câu trắc nghiệm: {missing}")
    plan: Plan = defaultdict(lambda: defaultdict(int))

    def take(skill_id: int, level: str) -> None:
        plan[skill_id][level] += 1
        cap[(skill_id, level)] -= 1
        unused[(skill_id, level)] -= 1

    def stale(skill_id: int, level: str) -> bool:
        return unused[(skill_id, level)] <= 0

    def mcq_count(skill_id: int) -> int:
        return sum(plan[skill_id][lv] for lv in MCQ_LEVELS)

    # 1) Kỹ năng được hỏi trắc nghiệm (tối đa 12 — số câu TN)
    mcq_total = STRUCTURE["recognize"] + STRUCTURE["understand"]
    mcq_skills = [s for s in skill_ids if any(cap[(s, lv)] > 0 for lv in MCQ_LEVELS)]
    rng.shuffle(mcq_skills)
    if len(mcq_skills) > mcq_total:
        prev = previous_skill_ids or set()
        mcq_skills.sort(key=lambda s: s in prev)  # lượt trước chưa hỏi → lên trước (sort giữ thứ tự ngẫu nhiên)
        mcq_skills = mcq_skills[:mcq_total]

    # 2) Mỗi kỹ năng ≥ 1 câu TN — chọn mức độ đang còn thiếu nhiều hơn
    remaining = {lv: STRUCTURE[lv] for lv in MCQ_LEVELS}
    for s in mcq_skills:
        levels = [lv for lv in MCQ_LEVELS if remaining[lv] > 0 and cap[(s, lv)] > 0]
        if levels:
            level = max(levels, key=lambda lv, s=s: (remaining[lv], not stale(s, lv), rng.random()))
            take(s, level)
            remaining[level] -= 1

    # 3) Phần TN còn lại — chia đều: kỹ năng đang ít câu nhất được ưu tiên
    for level in MCQ_LEVELS:
        while remaining[level] > 0:
            choices = [s for s in mcq_skills if cap[(s, level)] > 0]
            if not choices:
                raise NotEnoughQuestionsError(f"Thiếu câu trắc nghiệm mức {level}")
            # chia đều trước, rồi ưu tiên chỗ còn câu mới
            s = min(choices, key=lambda s, lv=level: (mcq_count(s), stale(s, lv), rng.random()))
            take(s, level)
            remaining[level] -= 1

    # 4) Tự luận: 1 nâng cao trước (ít câu hơn), rồi 2 dễ — ưu tiên kỹ năng chưa có câu tự luận
    essay_skills: set[int] = set()
    for level in ("advanced", "easy"):
        for _ in range(STRUCTURE[level]):
            choices = [s for s in skill_ids if cap[(s, level)] > 0]
            if not choices:
                raise NotEnoughQuestionsError(f"Thiếu câu tự luận mức {level}")
            # ưu tiên: kỹ năng chưa có câu TL (3 kỹ năng khác nhau) → còn câu mới → còn lại
            rng.shuffle(choices)
            s = min(choices, key=lambda s, lv=level: (s in essay_skills, stale(s, lv)))
            take(s, level)
            essay_skills.add(s)

    return {s: {lv: n for lv, n in levels.items() if n} for s, levels in plan.items()}


def order_exam(questions: list[dict], rng: random.Random) -> list[dict]:
    """Thứ tự trên đề: 12 TN (xáo ngẫu nhiên) → 2 TL dễ → 1 TL nâng cao.

    Trả về bản sao từng câu kèm "position" (1..15), "max_points" và — với TN — "option_order":
    hoán vị 4 lựa chọn, vd [2, 0, 3, 1] = vị trí hiển thị i là lựa chọn gốc option_order[i].
    """
    mcq = [q for q in questions if q["type"] == "mcq"]
    rng.shuffle(mcq)
    easy = [q for q in questions if q["level"] == "easy"]
    advanced = [q for q in questions if q["level"] == "advanced"]
    ordered = []
    for position, q in enumerate(mcq + easy + advanced, start=1):
        item = {**q, "position": position, "max_points": MAX_POINTS[q["level"]]}
        if q["type"] == "mcq":
            item["option_order"] = rng.sample(range(4), 4)
        ordered.append(item)
    return ordered
