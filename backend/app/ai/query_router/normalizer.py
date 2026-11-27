"""
Normalizer module for Query Router.
Handles string normalization, diacritics removal, JSON extraction, and entity cleaning.
"""

import json
import re
import unicodedata

from app.ai.query_router.config import GENERIC_ENTITIES


def remove_accents(text: str) -> str:
    """Loại bỏ dấu tiếng Việt để so sánh từ khóa."""
    if not isinstance(text, str):
        return ""
    normalized = unicodedata.normalize("NFD", text)
    result = "".join(char for char in normalized if unicodedata.category(char) != "Mn")
    return result.replace("đ", "d").replace("Đ", "D")


def normalize_text(text: str) -> str:
    """
    Chuẩn hóa văn bản phục vụ so sánh và nhận diện pattern.
    Lưu ý: Không dùng để lưu tên Entity cuối cùng.
    """
    if not isinstance(text, str):
        return ""
    # Tách khoảng cách nếu dấu câu/ngoặc bị viết liền với từ (ví dụ: (a11y)trong -> (a11y) trong)
    text = re.sub(r"([)\]}>,;!?])([a-zA-Z0-9_À-ỹ])", r"\1 \2", text)
    text = re.sub(r"([a-zA-Z0-9_À-ỹ])([(<\[{])", r"\1 \2", text)
    # Tách từ nếu bị dính liền với từ khóa khóa học (ví dụ: khoahocBusiness -> khoa hoc Business)
    text = re.sub(r"(khoa\s*hoc)([A-Za-zÀ-ỹ])", r"\1 \2", text, flags=re.IGNORECASE)
    text = re.sub(r"(course|courses)([A-Za-zÀ-ỹ])", r"\1 \2", text, flags=re.IGNORECASE)
    text = re.sub(r"(mon\s*hoc)([A-Za-zÀ-ỹ])", r"\1 \2", text, flags=re.IGNORECASE)
    text = text.lower().strip()
    text = remove_accents(text)
    text = re.sub(r"\s+", " ", text)
    return text


def extract_json_object(text: str) -> dict:
    """Extracts JSON object from text or Markdown fence."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Raw text for JSON extraction is empty.")

    cleaned = text.strip()

    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines and lines[0].strip().startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()

    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    match = re.search(r"\{[\s\S]*\}", cleaned)
    if not match:
        raise ValueError("Could not find valid JSON object in text.")

    data = json.loads(match.group(0))
    if not isinstance(data, dict):
        raise ValueError("Extracted JSON must be a dictionary.")

    return data


def clean_entity_name(entity_name: str) -> str:
    """
    Làm sạch tên Entity:
    1. Loại bỏ khoảng trắng và dấu câu ở hai đầu.
    2. Loại bỏ các cụm từ đệm, từ để hỏi hoặc trợ từ đuôi/đầu.
    """
    if not isinstance(entity_name, str):
        return ""

    name = entity_name.strip(" \t\n.,!?;:\"'`")

    trailing_particles = [
        r"\s+trong\s+he\s+thong\s+cua\s+ban\s+cho\s+toi\s+xem\s+di$",
        r"\s+trong\s+he\s+thong\s+cua\s+ban$",
        r"\s+trong\s+he\s+thong$",
        r"\s+tren\s+he\s+thong$",
        r"\s+cua\s+he\s+thong$",
        r"\s+cua\s+ban$",
        r"\s+cho\s+toi\s+xem\s+di$",
        r"\s+cho\s+minh\s+xem\s+di$",
        r"\s+cho\s+toi\s+xem$",
        r"\s+cho\s+minh\s+xem$",
        r"\s+cho\s+toi\s+biet$",
        r"\s+cho\s+minh\s+biet$",
        r"\s+cho\s+toi$",
        r"\s+cho\s+minh$",
        r"\s+de\s+toi\s+tham\s+khao$",
        r"\s+de\s+tham\s+khao$",
        r"\s+de\s+toi\s+hoc$",
        r"\s+de\s+hoc$",
        r"\s+co\s+gi\s+hay\s+khong$",
        r"\s+hay\s+khong$",
        r"\s+co\s+gi\s+hay$",
        r"\s+duoc\s+khong$",
        r"\s+duoc\s+ko$",
        r"\s+nao\s+khong$",
        r"\s+co\s+khong$",
        r"\s+khong\s+a$",
        r"\s+khong\s+vay$",
        r"\s+khong\s+nhi$",
        r"\s+nhung\s+gi$",
        r"\s+the\s+nao$",
        r"\s+ra\s+sao$",
        r"\s+lien\s+quan\s+nua$",
        r"\s+lien\s+quan\s+khac$",
        r"\s+lien\s+quan$",
        r"\s+nao\s+nua$",
        r"\s+nao\s+khac$",
        r"\s+nua$",
        r"\s+khac$",
        r"\s+them$",
        r"\s+nao$",
        r"\s+khong$",
        r"\s+vay$",
        r"\s+a$",
        r"\s+ha$",
        r"\s+nhi$",
        r"\s+chua$",
        r"\s+the$",
        r"\s+gi$",
        r"\s+di$",
        r"\s+nhe$",
        r"\s+nha$",
        r"\s+voi$",
    ]

    leading_particles = [
        r"^(?:con\s+|co\s+)?(?:ky\s+nang|skill|skills)\s+",
        r"^(?:con\s+|co\s+)?(?:khoa\s+hoc|course|courses)\s+",
        r"^(?:co\s+trong|co\s+o|trong|o|tai)\s+",
        r"^(?:thong\s+tin\s+chi\s+tiet|chi\s+tiet)\s+(?:ve\s+)?(?:khoa\s+hoc|khoa|course)?\s*",
        r"^(?:cac\s+|nhung\s+)?(?:modules?|moudules?|moudles?|moduls?)\s+(?:co\s+trong|trong|cua)\s*",
        r"^(?:cac\s+|nhung\s+)?(?:modules?|moudules?|moudles?|moduls?)\s+",
        r"^hoc\s*",
        r"^(?:co\s+|con\s+|chua\s+|day\s+|giang\s+day\s+|chuyen\s+ve\s+|ve\s+|cho\s+|lien\s+quan\s+(?:den|toi|ve)\s+|lien\s+quan\s+)",
        r"^(?:related\s+to\s+|related\s+|about\s+|on\s+|for\s+)",
        r"^(?:skills?\s+(?:related\s+to|about|on)\s+)",
        r"^(?:cac\s+|nhung\s+|mot\s+so\s+)",
        r"^nao\s+",
        r"^con\s+",
    ]

    changed = True
    while changed:
        changed = False
        norm = remove_accents(name)
        for p in trailing_particles:
            m = re.search(p, norm, flags=re.IGNORECASE)
            if m:
                cut_len = len(norm) - m.start()
                name = name[:-cut_len].strip(" \t\n.,!?;:\"'`")
                changed = True
                break
        norm = remove_accents(name)
        for p in leading_particles:
            m = re.search(p, norm, flags=re.IGNORECASE)
            if m:
                cut_len = m.end()
                name = name[cut_len:].strip(" \t\n.,!?;:\"'`")
                changed = True
                break

    standalone_noise = {
        "nao",
        "nua",
        "khac",
        "lien quan",
        "lien quan nua",
        "lien quan khac",
        "nao nua",
        "nao khac",
        "con lai",
        "them",
        "gi",
        "sao",
        "the nao",
        "ra sao",
        "nhung",
        "cac",
        "co",
        "la",
        "di",
        "do",
        "nay",
        "kia",
        "nhe",
        "nha",
        "voi",
        "a",
        "ha",
        "nhi",
        "chua",
        "the",
        "vay",
        "hoc",
        "so",
        "thu",
        "chi tiet",
        "thong tin",
    }
    if remove_accents(name).strip() in standalone_noise:
        return ""

    return name


def is_generic_entity(entity_name: str) -> bool:
    """Kiểm tra Entity có phải cụm chung chung không."""
    if not isinstance(entity_name, str) or not entity_name.strip():
        return True
    normalized = normalize_text(entity_name)
    if normalized in GENERIC_ENTITIES:
        return True
    if re.search(r"^(?:so|thu)?\s*[0-9]+$", normalized):
        return True
    if normalized in ("hoc", "so", "thu", "may", "bao nhieu", "khoa", "khoa hoc"):
        return True
    generic_patterns = [
        "phu hop",
        "nguoi moi",
        "moi hoc",
        "chua biet gi",
        "cho nguoi",
        "thich hop",
        "can thiet",
        "co ban nhat",
        "suitable for",
        "newbie",
        "me exercises",
    ]
    return any(p in normalized for p in generic_patterns)


def normalize_entity_name(entity_name: str) -> str:
    """Chuẩn hóa cách viết một số tên công nghệ phổ biến."""
    if not isinstance(entity_name, str) or not entity_name.strip():
        return ""

    known_names = {
        "python": "Python",
        "sql": "SQL",
        "mysql": "MySQL",
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "javascript": "JavaScript",
        "typescript": "TypeScript",
        "react": "React",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "php": "PHP",
        "laravel": "Laravel",
        "java": "Java",
        "c#": "C#",
        "c++": "C++",
        "html": "HTML",
        "css": "CSS",
        "mongodb": "MongoDB",
        "flutter": "Flutter",
        "fastapi": "FastAPI",
        "django": "Django",
        "flask": "Flask",
        "docker": "Docker",
        "kubernetes": "Kubernetes",
        "git": "Git",
        "github": "GitHub",
        "machine learning": "Machine Learning",
        "deep learning": "Deep Learning",
        "artificial intelligence": "Artificial Intelligence",
        "ai": "AI",
        "data": "Data",
        "web accessibility": "Web Accessibility",
        "web accessibility (a11y)": "Web Accessibility",
        "a11y": "Web Accessibility",
        "accessibility": "Accessibility",
    }

    entity_name = clean_entity_name(entity_name)
    normalized = normalize_text(entity_name)
    return known_names.get(normalized, entity_name)


def finalize_entity(entity_name: str | None) -> str | None:
    """Chuẩn hóa Entity sau khi trích xuất. Trả về None nếu rỗng hoặc generic."""
    if not entity_name:
        return None
    entity_name = clean_entity_name(entity_name)
    if not entity_name or is_generic_entity(entity_name):
        return None
    return normalize_entity_name(entity_name)


def detect_operation_type(user_message: str) -> str:
    """Phân biệt yêu cầu lấy link và hướng dẫn thao tác."""
    text = normalize_text(user_message)

    step_by_step_keywords = [
        "huong dan",
        "cach",
        "lam sao",
        "how to",
        "how can i",
        "buoc tiep theo",
        "can nhap",
        "can dien",
        "thuc hien nhu the nao",
        "toi vao roi",
        "toi truy cap roi",
        "da truy cap",
        "da vao",
        "dang o trang",
        "da mo trang",
        "sau khi",
        "tiep theo lam gi",
    ]

    if any(keyword in text for keyword in step_by_step_keywords):
        return "step_by_step"

    direct_link_keywords = [
        "link",
        "duong dan",
        "url",
        "dia chi trang",
        "truy cap trang nao",
        "vao trang nao",
        "mo trang nao",
    ]

    if any(keyword in text for keyword in direct_link_keywords):
        return "direct_link"

    return "general_operation"
