"""
Entity extractor module for Query Router.
Extracts Skill, Course, Instructor, Organization, Rating, Level entities using rules and LLM fallback.
"""

import re

from app.ai.client import generate_text
from app.ai.query_router.config import (
    ALLOWED_ENTITY_TYPES,
    COMMON_TECH_SKILLS,
    ENTITY_REQUIRED_INTENTS,
)
from app.ai.query_router.normalizer import (
    clean_entity_name,
    extract_json_object,
    finalize_entity,
    is_generic_entity,
    normalize_entity_name,
    normalize_text,
)


def detect_entity_type(text: str) -> str:
    """Detects whether user query refers to course, skill, or none."""
    normalized = normalize_text(text)

    course_keywords = [
        "khoa hoc",
        "course",
        "courses",
        "mon hoc",
    ]

    skill_keywords = [
        "skill",
        "skills",
        "ky nang",
        "kien thuc",
    ]

    if any(keyword in normalized for keyword in course_keywords):
        return "course"

    if any(keyword in normalized for keyword in skill_keywords):
        return "skill"

    # Check for known tech skills
    for skill in sorted(COMMON_TECH_SKILLS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(skill) + r"\b", normalized):
            return "skill"

    explanation_markers = [
        "la gi",
        "giai thich",
        "khai niem",
        "hoat dong nhu the nao",
        "hoat dong ra sao",
        "dung de lam gi",
        "cach dung",
        "cach viet",
    ]
    if any(marker in normalized for marker in explanation_markers):
        return "skill"

    return "none"


def extract_skill_search_entity(user_message: str) -> dict:
    """
    Trích xuất chủ đề Skill người dùng muốn tìm.
    Ví dụ:
    - Tìm skill về Python -> Python
    - Skill nào liên quan đến SQL? -> SQL
    """
    text = normalize_text(user_message)

    anaphoric_markers = [
        "skill do",
        "ky nang do",
        "khoa hoc do",
        "mon do",
        "chu de do",
        "skill nay",
        "ky nang nay",
        "khoa hoc nay",
        "mon nay",
        "chu de nay",
        "do thi sao",
        "cai do",
        "no thi sao",
        "ve no",
        "den no",
        "ve chung",
        "den chung",
        "nao nua",
        "nua khong",
        "con nua",
        "con khac",
        "gi nua",
        "gi khac",
    ]
    if any(re.search(r"\b" + re.escape(m) + r"\b", text) for m in anaphoric_markers):
        return {
            "entity_type": "skill",
            "entity_name": None,
        }

    popular_skill_markers = [
        "duoc hoc nhieu nhat",
        "hoc nhieu nhat",
        "nhieu nguoi hoc nhat",
        "pho bien nhat",
        "noi bat nhat",
        "noi bat",
        "hot nhat",
        "pho bien",
        "hang dau",
        "tieu bieu",
        "quan trong nhat",
        "hay nhat",
        "tot nhat",
    ]
    if any(re.search(r"\b" + re.escape(p) + r"\b", text) for p in popular_skill_markers):
        matched_skill = None
        for skill in sorted(COMMON_TECH_SKILLS, key=len, reverse=True):
            if re.search(r"\b" + re.escape(skill) + r"\b", text):
                matched_skill = skill
                break
        if matched_skill:
            return {
                "entity_type": "skill",
                "entity_name": normalize_entity_name(matched_skill),
            }
        return {
            "entity_type": "popular",
            "entity_name": "popular",
        }

    patterns = [
        (
            r"(?:skill|skills|ky nang|kien thuc)"
            r".*?"
            r"(?:lien quan den|lien quan toi|lien quan ve|ve)"
            r"\s+(.+?)"
            r"(?=\s+(?:can hoc|nen hoc|muon hoc|co the hoc|"
            r"phu hop|trong he thong|ngoai he thong)\b|[?.!]*$)"
        ),
        (
            r"(?:lien quan den|lien quan toi|lien quan ve)"
            r"\s+(.+?)"
            r"(?=\s+(?:can hoc|nen hoc|muon hoc|co the hoc|"
            r"phu hop|trong he thong|ngoai he thong)\b|[?.!]*$)"
        ),
        (
            r"(?:tim|search|find)"
            r"\s+(?:cho toi\s+|cho minh\s+)?"
            r"(?:cac\s+|nhung\s+)?"
            r"(?:skill|skills|ky nang)"
            r"\s+(?:ve|cua)?\s*(.+?)[?.!]*$"
        ),
        (
            r"(?:skill|skills|ky nang)"
            r"\s+(?:ve|cua)\s+(.+?)[?.!]*$"
        ),
        (
            r"(?:skill|skills|ky nang)"
            r"\s+(?:nao\s+)?"
            r"(?:lien quan\s+)?(?:den|toi|ve)"
            r"\s+(.+?)[?.!]*$"
        ),
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue

        raw_match = match.group(1)
        start, end = match.span(1)
        if len(user_message) == len(text):
            raw_match = user_message[start:end]

        entity_name = finalize_entity(raw_match)
        if entity_name:
            return {
                "entity_type": "skill",
                "entity_name": entity_name,
            }

    for skill in sorted(COMMON_TECH_SKILLS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            return {
                "entity_type": "skill",
                "entity_name": normalize_entity_name(skill),
            }

    return {
        "entity_type": "skill",
        "entity_name": None,
    }


def extract_course_review_entity(user_message: str) -> dict:
    text = normalize_text(user_message)
    patterns = [
        (r"(?:khoa hoc|khoa|course|courses)\s+(?:nay\s+)?(?:trong he thong\s+)?(?:khong|ha|nhi)?\s+(.+?)[?.!]*$"),
        (r"(?:khoa hoc|khoa|course|courses)\s+(?:ve\s+)?(.+?)[?.!]*$"),
        (r"(?:on tap|kiem tra|lam bai|quiz|review)\s+(?:khoa hoc|khoa|course)\s+(.+?)[?.!]*$"),
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            raw_entity = match.group(1).strip()
            # Loại bỏ các từ phụ như "nay", "trong he thong", "khong" nếu còn sót
            raw_entity = re.sub(r"^(?:nay\s+|do\s+|trong he thong\s+|khong\s+)+", "", raw_entity, flags=re.IGNORECASE)
            entity_name = finalize_entity(raw_entity)
            if entity_name and not is_generic_entity(entity_name):
                return {
                    "entity_type": "course",
                    "entity_name": entity_name,
                }
    return {
        "entity_type": "course",
        "entity_name": None,
    }


def extract_skill_review_entity(user_message: str) -> dict:
    text = normalize_text(user_message)

    # First check for known skills
    for skill in sorted(COMMON_TECH_SKILLS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            return {
                "entity_type": "skill",
                "entity_name": normalize_entity_name(skill),
            }

    patterns = [
        (r"(?:skill|skills|ky nang)\s+(?:ve\s+)?(.+?)[?.!]*$"),
        (
            r"(?:on tap|kiem tra|lam bai|quiz|review|cau hoi trac nghiem|cau hoi on tap|cau hoi luyen tap|cau hoi|trac nghiem|luyen tap)\s+(?:ve\s+)?(.+?)[?.!]*$"
        ),
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            raw = match.group(1).strip()
            raw = re.sub(r"^(?:on tap|luyen tap|kiem tra|ve)\s+", "", raw, flags=re.IGNORECASE)
            entity_name = finalize_entity(raw)
            if entity_name:
                return {
                    "entity_type": "skill",
                    "entity_name": entity_name,
                }

    return {
        "entity_type": "skill",
        "entity_name": None,
    }


def extract_learning_path_entity(user_message: str) -> dict:
    """Trích xuất chủ đề người dùng muốn học."""
    text = normalize_text(user_message)
    patterns = [
        (r"(?:lo trinh|learning path).*?(?:de\s+)?(?:tro thanh|lam)\s+(.+?)[?.!]*$"),
        (
            r"(?:goi y|tu van|de xuat|tao|xay dung|generate|create).*?(?:lo trinh|learning path)\s+(?:cac ky nang\s+)?(?:can hoc\s+)?(?:de\s+)?(?:tro thanh\s+)?(?:ve\s+|cho\s+)?(.+?)[?.!]*$"
        ),
        (
            r"(?:tao|generate|create)\s+(?:cho toi\s+|cho minh\s+)?(?:mot\s+)?(?:lo trinh hoc|learning path)\s+(?:ve\s+|cho\s+)?(.+?)[?.!]*$"
        ),
        (r"(?:lo trinh hoc|learning path|lo trinh)\s+(?:ve\s+|cho\s+|hoc\s+)?(.+?)[?.!]*$"),
        (r"(?:hoc|learn)\s+(.+?)\s+(?:theo\s+)?(?:mot\s+)?(?:lo trinh|learning path)[?.!]*$"),
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        raw_match = match.group(1).strip()
        raw_match = re.sub(r"^(?:hoc|cho|ve|cac ky nang|nhung ky nang|ky nang)\s+", "", raw_match, flags=re.IGNORECASE)
        entity_name = finalize_entity(raw_match)
        if entity_name:
            return {
                "entity_type": "skill",
                "entity_name": entity_name,
            }
    return {
        "entity_type": "none",
        "entity_name": None,
    }


def extract_course_search_entity(user_message: str) -> dict:
    """
    Tìm chủ đề Skill hoặc tiêu chí (tổ chức, giảng viên, rating, cấp độ)
    mà người dùng muốn tìm Course.
    """
    text = normalize_text(user_message)

    is_course_by_instructor = bool(
        re.search(r"\bkhoa hoc do\s+(?:day|giang day|huong dan)\b", text)
        or re.search(r"\bkhoa hoc do\s+[a-z\s]+?\s+(?:day|giang day)\b", text)
    )
    anaphoric_markers = [
        "khoa hoc do thi sao",
        "ve khoa hoc do",
        "mon hoc do",
        "mon do",
        "course do",
        "khoa hoc nay",
        "mon nay",
        "course nay",
        "skill do",
        "ky nang do",
        "chu de do",
        "cai do",
        "do thi sao",
        "no thi sao",
        "ve no",
        "den no",
        "nao nua",
        "nua khong",
        "con nua",
        "con khac",
        "gi nua",
        "gi khac",
    ]
    if not is_course_by_instructor:
        if any(re.search(r"\b" + re.escape(m) + r"\b", text) for m in anaphoric_markers) or re.search(
            r"\bkhoa hoc do\b(?:\s+(?:thi|co|la|nhu the nao|gom|chua|[?.!]))?", text
        ):
            return {
                "entity_type": "skill",
                "entity_name": None,
            }

    # Popular / Most Enrolled
    popular_course_markers = [
        "duoc hoc nhieu nhat",
        "hoc nhieu nhat",
        "nhieu nguoi hoc nhat",
        "pho bien nhat",
        "noi bat nhat",
        "hot nhat",
        "hang dau",
        "top khoa hoc",
        "khoa hoc noi bat",
        "khoa hoc pho bien",
        "khoa hoc hot",
        "noi bat",
        "pho bien",
    ]
    if any(re.search(r"\b" + re.escape(p) + r"\b", text) for p in popular_course_markers):
        matched_skill = None
        for skill in sorted(COMMON_TECH_SKILLS, key=len, reverse=True):
            if re.search(r"\b" + re.escape(skill) + r"\b", text):
                matched_skill = skill
                break
        if matched_skill:
            return {
                "entity_type": "skill",
                "entity_name": normalize_entity_name(matched_skill),
            }
        return {
            "entity_type": "popular",
            "entity_name": "popular",
        }

    # Rating
    if re.search(
        r"(?:5\s*sao|danh gia cao nhat|danh gia tot nhat|rating cao|top rating|diem cao nhat|rating 5)",
        text,
    ):
        return {
            "entity_type": "rating",
            "entity_name": "5",
        }

    m_rating = re.search(r"(?:khoa hoc|courses?).*?([3-5](?:\.[0-9])?)\s*sao", text)
    if m_rating:
        return {
            "entity_type": "rating",
            "entity_name": m_rating.group(1),
        }

    # Level
    matched_skill = None
    for skill in sorted(COMMON_TECH_SKILLS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            matched_skill = skill
            break

    level_patterns = [
        (r"(?:cap do|trinh do|level)\s+(?:la\s+)?(?:co ban|moi bat dau|so cap|beginner)", "beginner"),
        (r"(?:cho|danh cho)\s+(?:nguoi\s+)?(?:moi\s+bat\s+dau|moi\s+hoc|chua\s+biet\s+gi)", "beginner"),
        (r"\b(?:beginner|co ban|moi bat dau)\b.*?(?:khoa hoc|courses?)", "beginner"),
        (r"(?:khoa hoc|courses?).*?\b(?:beginner)\b", "beginner"),
        (r"(?:cap do|trinh do|level)\s+(?:la\s+)?(?:trung cap|trung binh|intermediate)", "intermediate"),
        (r"(?:khoa hoc|courses?).*?\b(?:intermediate|trung cap)\b", "intermediate"),
        (r"(?:cap do|trinh do|level)\s+(?:la\s+)?(?:nang cao|chuyen sau|advanced)", "advanced"),
        (r"(?:khoa hoc|courses?).*?\b(?:advanced|nang cao|chuyen sau)\b", "advanced"),
    ]
    for lp, lvl in level_patterns:
        if re.search(lp, text, flags=re.IGNORECASE):
            if matched_skill:
                return {
                    "entity_type": "skill",
                    "entity_name": normalize_entity_name(matched_skill),
                    "level": lvl,
                }
            return {
                "entity_type": "level",
                "entity_name": lvl,
            }

    # Instructor
    instructor_patterns = [
        r"(?:khoa hoc|courses?).*?(?:cua|do|boi)?\s*(?:giang vien|giao vien|thay|co giao|instructor)\s+(.+?)(?=\s+(?:day|giang day|trong he thong|tren he thong|cho toi|co khong)\b|[?.!]*$)",
        r"(?:giang vien|giao vien|thay|co giao|instructor)\s+(.+?)\s+(?:co\s+)?(?:nhung\s+|cac\s+)?(?:khoa hoc|courses?)",
        r"(?:khoa hoc|courses?).*?(?:do|boi)\s+(.+?)\s+(?:day|giang day)",
        r"(?:giang vien|giao vien|thay|co giao|instructor)\s+([a-zA-Z0-9\s.'-]+?)(?=\s+(?:day|giang day|trong he thong|tren he thong|cho toi|co khong)\b|[?.!]*$)",
    ]
    for ip in instructor_patterns:
        m = re.search(ip, text, flags=re.IGNORECASE)
        if m:
            s, e = m.span(1)
            raw_val = user_message[s:e] if len(user_message) == len(text) else m.group(1)
            clean_name = clean_entity_name(raw_val.strip())
            if clean_name and not is_generic_entity(clean_name):
                return {
                    "entity_type": "instructor",
                    "entity_name": clean_name,
                }

    # Organization
    org_patterns = [
        r"(?:khoa hoc|courses?).*?(?:cua|tu|thuoc)\s+(?:to chuc|truong dai hoc|truong|dai hoc|vien|doi tac)?\s*(.+?)(?=\s+(?:trong he thong|tren he thong|cho toi|co khong)\b|[?.!]*$)",
        r"(?:to chuc|truong dai hoc|truong|dai hoc|vien|doi tac)\s+(.+?)\s+(?:co\s+)?(?:nhung\s+|cac\s+)?(?:khoa hoc|courses?)",
        r"(?:to chuc|truong dai hoc|truong|dai hoc|vien|doi tac)\s+([a-zA-Z0-9\s.'-]+?)(?=\s+(?:to chuc|day|giang day|cung cap|trong he thong|tren he thong|cho toi|co khong)\b|[?.!]*$)",
        r"(?:do|boi|tu)\s+(?:to chuc\s+)?([a-zA-Z0-9\s.'-]+?)(?=\s+(?:to chuc|day|giang day|cung cap|trong he thong|tren he thong|cho toi|co khong)\b|[?.!]*$)",
    ]
    for op in org_patterns:
        m = re.search(op, text, flags=re.IGNORECASE)
        if m:
            s, e = m.span(1)
            raw_val = user_message[s:e] if len(user_message) == len(text) else m.group(1)
            clean_name = clean_entity_name(raw_val.strip())
            if clean_name and not is_generic_entity(clean_name):
                return {
                    "entity_type": "organization",
                    "entity_name": clean_name,
                }

    # Grammar patterns for Skill / Topic
    patterns = [
        (r"(?:khoa hoc|courses?)\s+(?:co\s+|chua\s+)?(?:ky nang|skill)\s+(.+?)[?.!]*$"),
        (
            r"(?:(?:edumentor|he thong|ban|web|o day|hien tai)\s+)?(?:co\s+)?(?:nhung\s+|cac\s+)?(?:khoa hoc|courses?)\s+(?:nao\s+)?(?:ve|cua|cho|day|giang day|chuyen ve|lien quan den|lien quan toi|lien quan ve|co|chua)\s+(.+?)(?:\s+khong|\s+ha|\s+nhi|[?.!])*$"
        ),
        (
            r"(?:tim|search|find)\s+(?:cho toi\s+|giup toi\s+|cho minh\s+)?(?:cac\s+|nhung\s+)?(?:khoa hoc|courses?)\s+(?:nao\s+)?(?:ve|cua|cho|day|giang day|chuyen ve|lien quan den|lien quan toi|lien quan ve|co|chua)?\s*(.+?)[?.!]*$"
        ),
        (
            r"(?:cho toi|cho minh|toi muon)\s+(?:xem\s+)?(?:nhung\s+|cac\s+)?(?:khoa hoc|courses?)\s*(?:nao\s+)?(?:cua|ve|cho|day|giang day|lien quan den|lien quan toi|lien quan ve|co|chua)?\s*(.+?)[?.!]*$"
        ),
        (
            r"(?:danh sach|liet ke)\s+(?:cac\s+|nhung\s+)?(?:khoa hoc|courses?)\s*(?:nao\s+)?(?:ve|cua|cho|day|lien quan den|lien quan toi|lien quan ve|co|chua)?\s*(.+?)[?.!]*$"
        ),
        (r"^(.+?)\s+co\s+(?:nhung\s+|cac\s+)?(?:khoa hoc|courses?)\s+nao\s*[?.!]*$"),
    ]

    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        raw_match = match.group(1)
        start, end = match.span(1)
        if len(user_message) == len(text):
            raw_match = user_message[start:end]
        entity_name = finalize_entity(raw_match)
        if entity_name:
            return {
                "entity_type": "skill",
                "entity_name": entity_name,
            }

    for skill in sorted(COMMON_TECH_SKILLS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(skill) + r"\b", text):
            return {
                "entity_type": "skill",
                "entity_name": normalize_entity_name(skill),
            }

    return {
        "entity_type": "skill",
        "entity_name": None,
    }


def extract_course_enrollment_entity(user_message: str) -> dict:
    """Trích xuất tên Course hoặc chủ đề Course cần tìm link."""
    text = normalize_text(user_message)
    patterns = [
        (r"(?:khoa hoc|course|courses).*?(?:lien quan den|lien quan toi|lien quan ve)\s+(.+?)[?.!]*$"),
        (r"(?:khoa hoc|course|courses)\s+(?:ve|cua|cho|day|co chu de)\s+(.+?)[?.!]*$"),
        (
            r"(?:link|duong dan|url).*?(?:tham gia|dang ky|ghi danh|enroll|join)\s+(?:vao\s+)?(?:khoa hoc|course|courses)\s+(.+?)[?.!]*$"
        ),
        (r"(?:tham gia|dang ky|ghi danh|enroll|join)\s+(?:vao\s+)?(?:khoa hoc|course|courses)\s+(.+?)[?.!]*$"),
        (r"(?:khoa hoc|course|courses)\s+(.+?)[?.!]*$"),
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if not match:
            continue
        entity_name = finalize_entity(match.group(1))
        if entity_name:
            return {
                "entity_type": "course",
                "entity_name": entity_name,
            }
    return {
        "entity_type": "course",
        "entity_name": None,
    }


def extract_entity_by_rules(user_message: str, intent: str) -> dict:
    """Main rule-based entity extraction dispatcher."""
    if intent == "learning_path_request":
        return extract_learning_path_entity(user_message)

    if intent == "course_enrollment_link":
        return extract_course_enrollment_entity(user_message)

    if intent not in ENTITY_REQUIRED_INTENTS:
        return {
            "entity_type": "none",
            "entity_name": None,
        }

    if intent == "skill_search":
        return extract_skill_search_entity(user_message)

    if intent == "course_search":
        return extract_course_search_entity(user_message)

    if intent == "skill_review":
        return extract_skill_review_entity(user_message)

    if intent == "course_review":
        return extract_course_review_entity(user_message)

    if intent == "course_question":
        return extract_course_review_entity(user_message)
    elif intent == "skill_question":
        entity_type = "skill"
        markers = ["ky nang", "kien thuc", "skill", "skills"]
    else:
        return {
            "entity_type": "none",
            "entity_name": None,
        }

    normalized = normalize_text(user_message)

    for marker in sorted(markers, key=len, reverse=True):
        pattern = re.escape(marker) + r"\s+(.+?)[?.!]*$"
        match = re.search(pattern, normalized, flags=re.IGNORECASE)
        if not match:
            continue
        entity_name = finalize_entity(match.group(1))
        if entity_name:
            return {
                "entity_type": entity_type,
                "entity_name": entity_name,
            }

    if intent == "skill_question":
        explanation_patterns = [
            r"giai thich (?:ve |giup |cho )?(.+?)(?: giup| cho| kem| nhe|[?.!]|$)",
            r"khai niem (?:ve )?(.+?)(?: la gi|[?.!]|$)",
            r"(.+?)\s+la gi[?.!]*$",
            r"(.+?)\s+hoat dong (?:nhu the nao|ra sao)[?.!]*$",
            r"cach (?:dung|su dung|viet) (.+?)(?: trong| cho|[?.!]|$)",
            r"so sanh (.+?) va (.+?)[?.!]*$",
            r"vi du (?:ve )?(.+?)(?: trong|[?.!]|$)",
        ]
        for pat in explanation_patterns:
            m = re.search(pat, normalized, flags=re.IGNORECASE)
            if m:
                extracted = finalize_entity(m.group(1))
                if extracted and not is_generic_entity(extracted):
                    return {
                        "entity_type": "skill",
                        "entity_name": extracted,
                    }

        for skill in sorted(COMMON_TECH_SKILLS, key=len, reverse=True):
            if re.search(r"\b" + re.escape(skill) + r"\b", normalized):
                return {
                    "entity_type": "skill",
                    "entity_name": skill,
                }

    return {
        "entity_type": entity_type,
        "entity_name": None,
    }


def extract_entity_by_llm(user_message: str, custom_api_key: str | None = None) -> dict:
    """Uses LLM to extract entity when rules cannot find one."""
    prompt = f"""
Bạn là Entity Extractor của hệ thống EduMentor AI.

Nhiệm vụ:
Xác định Skill hoặc Course mà người dùng thực sự nhắc đến.

Chỉ trả về JSON:

{{
    "entity_type": "skill",
    "entity_name": "Python"
}}

Quy tắc:
1. entity_type chỉ gồm skill, course hoặc none.
2. entity_name phải là tên được người dùng cung cấp.
3. Không tự nghĩ ra tên Skill hoặc Course.
4. Không lấy từ nghi vấn như nào, gì, không, vậy.
5. Không lấy từ chung chung như khóa học, kỹ năng.
6. Không lấy cụm chỉ sở hữu (của tôi, của riêng mình, cho bản thân).
7. Không lấy cụm chỉ mục đích (liên quan đến, trong hệ thống).
8. Giữ nguyên tên Course nhiều từ.
9. Nếu không có Entity cụ thể, trả về none và null.
10. Chỉ trả về JSON hợp lệ, không giải thích.

Câu hỏi:
{user_message}
"""
    ai_text = generate_text(prompt, api_key=custom_api_key)
    result = extract_json_object(ai_text)

    entity_type = result.get("entity_type")
    entity_name = result.get("entity_name")

    if entity_type not in ALLOWED_ENTITY_TYPES:
        entity_type = "none"

    entity_name = finalize_entity(entity_name)
    if not entity_name:
        return {
            "entity_type": "none",
            "entity_name": None,
        }

    if entity_type == "none":
        entity_name = None
    else:
        entity_name = normalize_entity_name(entity_name)

    return {
        "entity_type": entity_type,
        "entity_name": entity_name,
    }
