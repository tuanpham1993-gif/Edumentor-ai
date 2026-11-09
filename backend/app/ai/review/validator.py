"""Kiểm tra câu hỏi ôn tập — dùng CHUNG cho ngân hàng soạn tay (scripts/seed_review.py)
và câu do AI sinh (services/review_service.py) (module 09 · Tuấn · GĐ2, 09/11/2026).

Một câu hỏi là dict cùng định dạng file data/review/*.json:
    {"type": "mcq", "level": "recognize", "content": "...", "options": [4 chuỗi], "correct_index": 0..3}
    {"type": "essay", "level": "easy", "content": "...", "rubric": [{"text", "max_points",
     "main_keywords", "sub_keywords"}, ...]}
Câu bốc từ ngân hàng có thêm "question_id".
"""

from app.models.review_question import ESSAY_LEVELS, MCQ_LEVELS

RUBRIC_SIZE = {"easy": (2, 3), "advanced": (4, 5)}  # số ý barem theo loại câu (chốt 09/11)
RUBRIC_TOTAL = 10
TYPE_OF_LEVEL = {**dict.fromkeys(MCQ_LEVELS, "mcq"), **dict.fromkeys(ESSAY_LEVELS, "essay")}


def _is_text(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _mcq_errors(q: dict, where: str) -> list[str]:
    errors = []
    if q.get("level") not in MCQ_LEVELS:
        errors.append(f"{where}: level của trắc nghiệm phải là {MCQ_LEVELS}")
    options = q.get("options")
    if not (isinstance(options, list) and len(options) == 4 and all(_is_text(o) for o in options)):
        errors.append(f"{where}: trắc nghiệm phải có đúng 4 lựa chọn (chuỗi khác rỗng)")
    elif len({o.strip().lower() for o in options}) != 4:
        errors.append(f"{where}: 4 lựa chọn bị trùng nhau")
    index = q.get("correct_index")
    if not (isinstance(index, int) and not isinstance(index, bool) and 0 <= index <= 3):
        errors.append(f"{where}: correct_index phải là số 0..3")
    if q.get("rubric") is not None:
        errors.append(f"{where}: trắc nghiệm không được có rubric")
    return errors


def _essay_errors(q: dict, where: str) -> list[str]:
    level = q.get("level")
    if level not in ESSAY_LEVELS:
        return [f"{where}: level của tự luận phải là {ESSAY_LEVELS}"]
    errors = []
    if q.get("options") is not None or q.get("correct_index") is not None:
        errors.append(f"{where}: tự luận không được có options / correct_index")
    rubric = q.get("rubric")
    if not isinstance(rubric, list):
        return errors + [f"{where}: tự luận phải có rubric (danh sách ý)"]
    low, high = RUBRIC_SIZE[level]
    if not low <= len(rubric) <= high:
        errors.append(f"{where}: câu {level} phải có {low}–{high} ý, đang có {len(rubric)}")
    total = 0
    for i, item in enumerate(rubric, start=1):
        if not isinstance(item, dict):
            errors.append(f"{where} ý {i}: phải là object")
            continue
        if not _is_text(item.get("text")):
            errors.append(f"{where} ý {i}: thiếu text")
        points = item.get("max_points")
        if isinstance(points, (int, float)) and not isinstance(points, bool) and points > 0:
            total += points
        else:
            errors.append(f"{where} ý {i}: max_points phải > 0")
        main = item.get("main_keywords")
        if not (isinstance(main, list) and main and all(_is_text(k) for k in main)):
            errors.append(f"{where} ý {i}: main_keywords phải có ít nhất 1 từ khóa")
        sub = item.get("sub_keywords", [])
        if not (isinstance(sub, list) and all(_is_text(k) for k in sub)):
            errors.append(f"{where} ý {i}: sub_keywords phải là danh sách chuỗi")
    if total != RUBRIC_TOTAL:
        errors.append(f"{where}: tổng max_points phải = {RUBRIC_TOTAL}, đang = {total}")
    return errors


def question_errors(q, where: str = "Câu") -> list[str]:
    """Lỗi của MỘT câu hỏi (nội dung, loại, mức độ, lựa chọn / barem). Rỗng = hợp lệ."""
    if not isinstance(q, dict):
        return [f"{where}: phải là object"]
    errors = [] if _is_text(q.get("content")) else [f"{where}: thiếu content"]
    if q.get("type") == "mcq":
        return errors + _mcq_errors(q, where)
    if q.get("type") == "essay":
        return errors + _essay_errors(q, where)
    return errors + [f"{where}: type phải là 'mcq' hoặc 'essay'"]


def generated_errors(questions, need: dict[str, int]) -> list[str]:
    """Kiểm kết quả AI trả về cho MỘT kỹ năng: từng câu hợp lệ, đủ đúng số câu mỗi mức độ, không trùng.

    need: số câu cần theo mức độ, vd {"recognize": 2, "understand": 1, "easy": 1}.
    """
    if not isinstance(questions, list):
        return ["Kết quả AI phải là danh sách câu hỏi"]
    errors = []
    for i, q in enumerate(questions, start=1):
        errors += question_errors(q, f"Câu {i}")
    if errors:
        return errors

    got: dict[str, int] = {}
    for q in questions:
        got[q["level"]] = got.get(q["level"], 0) + 1
    wanted = {level: n for level, n in need.items() if n > 0}
    if got != wanted:
        errors.append(f"Sai số câu theo mức độ: cần {wanted}, nhận {got}")

    ids = [q["question_id"] for q in questions if q.get("question_id") is not None]
    contents = [q["content"].strip().lower() for q in questions]
    if len(set(ids)) != len(ids) or len(set(contents)) != len(contents):
        errors.append("Có câu hỏi bị trùng")
    return errors


GRADE_RESULTS = {"full": 1.0, "partial": 0.5, "none": 0.0}  # phần điểm của ý (A10: đạt / ½ / 0)


def grading_errors(results, rubric: list[dict]) -> list[str]:
    """Kiểm kết quả chấm MỘT câu tự luận: đủ một kết quả cho mỗi ý, điểm khớp quy tắc đạt / ½ / 0."""
    if not isinstance(results, list) or len(results) != len(rubric):
        return [f"Kết quả chấm phải có đúng {len(rubric)} ý"]
    errors = []
    for i, (result, item) in enumerate(zip(results, rubric, strict=True), start=1):
        if not isinstance(result, dict) or result.get("result") not in GRADE_RESULTS:
            errors.append(f"Ý {i}: result phải là full / partial / none")
            continue
        expected = GRADE_RESULTS[result["result"]] * float(item["max_points"])
        points = result.get("points")
        if not isinstance(points, (int, float)) or abs(points - expected) > 1e-9:
            errors.append(f"Ý {i}: điểm phải = {expected}")
        evidence = result.get("evidence")
        if evidence is not None and not isinstance(evidence, str):
            errors.append(f"Ý {i}: evidence phải là chuỗi hoặc null")
    return errors
