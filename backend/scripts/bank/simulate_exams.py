"""Giả lập học viên làm lại nhiều lượt ôn theo kỹ năng — KHÔNG qua server, KHÔNG ghi DB, KHÔNG gọi AI.

    python -m scripts.bank.simulate_exams 494                     (mọi kỹ năng, 5 lượt, 200 học viên giả)
    python -m scripts.bank.simulate_exams 494 --skills IOT MSG --attempts 6

Ráp đề bằng đúng mock_ai.pick_from_bank với cơ chế G3e (tránh câu của REVIEW_AVOID_LAST_ATTEMPTS lượt gần nhất; lượt
gần nhất phạt N, cũ nhất phạt 1 — như review_repository.recent_submitted_question_ids) và nhóm loại trừ (7.5b).
Báo cho từng kỹ năng:
  - ngân hàng có đủ mục tiêu D25 (SKILL_TARGET) không → thiếu thì lượt làm lại sẽ gọi AI soạn bổ sung (topup);
  - số đề có câu tự luận cùng nhóm với một câu khác trong đề (lộ đáp án, ràng buộc mềm phải lùi) — mong 0;
  - lượt 2 có lặp câu của lượt 1 không — mong 0; từ lượt 3 lặp một phần là đúng thiết kế.
Chỉ tính câu soạn tay trong file đề (không có câu AI soạn).
"""

import argparse
import random
from collections import Counter

from scripts.bank.common import bank_path, load_bank, quiet


def simulate(bank: dict, skill: str, attempts: int, students: int, avoid_last: int) -> dict:
    from app.ai.review.mock_ai import pick_from_bank
    from app.services.question_gen_service import FULL_EXAM, SKILL_TARGET

    cands = [
        {"question_id": i, "level": q["level"], "type": q["type"], "exclusion_group": q.get("exclusion_group"),
         "code": q["code"]}
        for i, q in enumerate(bank["questions"])
        if q["skill"] == skill
    ]  # fmt: skip
    have = Counter(c["level"] for c in cands)
    short = {lv: n - have[lv] for lv, n in SKILL_TARGET.items() if have[lv] < n}
    clashes, repeat_2nd, repeats_later, incomplete = 0, 0, 0, 0
    for s in range(students):
        rng = random.Random(s)
        history: list[set[int]] = []
        for k in range(attempts):
            recent = history[-avoid_last:]
            penalty: dict[int, int] = {}
            for rank, ids in enumerate(recent, start=avoid_last - len(recent) + 1):  # cũ nhất phạt thấp nhất
                for qid in ids:
                    penalty[qid] = max(penalty.get(qid, 0), rank)
            picked = pick_from_bank(cands, dict(FULL_EXAM), rng, avoid_question_ids=penalty)
            ids = {q["question_id"] for q in picked}
            if len(picked) != sum(FULL_EXAM.values()):
                incomplete += 1
            essay_groups = Counter(
                q["exclusion_group"] for q in picked if q["type"] == "essay" and q["exclusion_group"]
            )
            all_groups = Counter(q["exclusion_group"] for q in picked if q["exclusion_group"])
            clashes += any(all_groups[g] > 1 for g in essay_groups)  # câu tự luận đã chọn ↔ câu cùng nhóm (lộ đáp án)
            if k == 1:
                repeat_2nd += len(ids & history[0])
            elif k > 1:
                repeats_later += len(ids & set().union(*history[-avoid_last:]))
            history.append(ids)
    return {"bank": dict(have), "short_of_target": short, "clashes": clashes, "repeat_2nd": repeat_2nd,
            "repeats_later_avg": round(repeats_later / max(1, students * max(0, attempts - 2)), 2),
            "incomplete": incomplete, "exams": students * attempts}  # fmt: skip


def main() -> int:
    parser = argparse.ArgumentParser(description="Giả lập làm lại nhiều lượt ôn theo kỹ năng (không DB, không AI)")
    parser.add_argument("course_id", type=int)
    parser.add_argument("--skills", nargs="+")
    parser.add_argument("--attempts", type=int, default=5)
    parser.add_argument("--students", type=int, default=200)
    args = parser.parse_args()
    quiet()
    from app.core.config import settings

    bank = load_bank(bank_path(args.course_id))
    bad = 0
    for skill in args.skills or list(bank["skills"]):
        r = simulate(bank, skill, args.attempts, args.students, settings.REVIEW_AVOID_LAST_ATTEMPTS)
        ok = not r["short_of_target"] and r["clashes"] == 0 and r["repeat_2nd"] == 0 and r["incomplete"] == 0
        bad += not ok
        print(
            f"{'OK ' if ok else 'XEM'} {skill:5} ngân hàng {r['bank']} | thiếu mục tiêu D25 {r['short_of_target'] or '-'}"
            f" | đề trùng nhóm {r['clashes']}/{r['exams']} | lượt 2 lặp {r['repeat_2nd']} câu"
            f" | từ lượt 3 lặp TB {r['repeats_later_avg']} câu/đề | đề thiếu câu {r['incomplete']}"
        )
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
