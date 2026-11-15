
import json
import re
import unicodedata

from app.ai.client import generate_text


# ==========================================
# 1. CONFIGURATION
# ==========================================

ALLOWED_INTENTS = {
    "skill_question",
    "skill_review",
    "skill_search",
    "course_question",
    "course_review",
    "course_search",
    "course_enrollment_link",
    "system_operation",
    "code_help",
    "learning_path_request",
    "general_question",
}

ALLOWED_ENTITY_TYPES = {
    "skill",
    "course",
    "none",
}

ENTITY_REQUIRED_INTENTS = {
    "skill_question",
    "skill_review",
    "skill_search",
    "course_question",
    "course_review",
    "course_search",
    "course_enrollment_link",
}

RETRIEVAL_MAP = {
    "skill_question": ["sql", "no_rag"],
    "skill_review": ["sql", "rag"],
    "skill_search": ["sql", "no_rag"],
    "course_question": ["sql", "no_rag"],
    "course_review": ["sql", "rag"],
    "course_search": ["sql"],
    "course_enrollment_link": ["sql"],
    "system_operation": ["rag"],
    "code_help": ["no_rag"],
    "learning_path_request": ["rag"],
    "general_question": ["no_rag"],
}

GENERIC_ENTITIES = {
    "cua rieng minh",
    "rieng minh",
    "cua toi",
    "cua ban than",
    "cho ban than",
    "ca nhan",
    "ban than",
    "minh",
    "toi",
    "chinh minh",
    "cua minh",
    "cho minh",
    "cho toi",
    "lien quan den",
    "lien quan toi",
    "khoa hoc",
    "cac khoa hoc",
    "nhung khoa hoc",
    "ky nang",
    "cac ky nang",
    "nhung ky nang",
    "none",
    "null",
}


# ==========================================
# 2. TEXT NORMALIZATION
# ==========================================

def remove_accents(text: str) -> str:
    """Loại bỏ dấu tiếng Việt."""

    if not isinstance(text, str):
        return ""

    normalized = unicodedata.normalize("NFD", text)

    result = "".join(
        char
        for char in normalized
        if unicodedata.category(char) != "Mn"
    )

    return result.replace("đ", "d").replace("Đ", "D")


def normalize_text(text: str) -> str:
    """Chuẩn hóa văn bản để so sánh từ khóa."""

    if not isinstance(text, str):
        return ""

    return re.sub(
        r"\s+",
        " ",
        remove_accents(text).casefold(),
    ).strip()


def extract_json_object(text: str) -> dict:
    """Đọc JSON Gemini trả về."""

    if not isinstance(text, str) or not text.strip():
        raise ValueError("AI không trả về nội dung.")

    text = text.strip()

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(r"\s*```$", "", text)

    try:
        result = json.loads(text)

        if isinstance(result, dict):
            return result

    except json.JSONDecodeError:
        pass

    match = re.search(r"\{[\s\S]*\}", text)

    if not match:
        raise ValueError("Không tìm thấy JSON object.")

    try:
        result = json.loads(match.group(0))

    except json.JSONDecodeError as error:
        raise ValueError(f"JSON AI không hợp lệ: {error}")

    if not isinstance(result, dict):
        raise ValueError("Kết quả AI phải là JSON object.")

    return result


# ==========================================
# 3. OPERATION TYPE
# ==========================================

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


# ==========================================
# 4. ENTITY CLEANING
# ==========================================

def clean_entity_name(entity_name: str) -> str:
    """
    Làm sạch tên Skill/Course.

    Ví dụ:
    - liên quan đến Python được không -> Python
    - khóa học Python nhé -> Python
    - SQL bạn có thể gợi ý skill -> SQL
    - của riêng mình -> rỗng
    """

    if not isinstance(entity_name, str):
        return ""

    name = normalize_text(entity_name)

    name = name.strip(" \t\n.,!?;:\"'`")

    # Các cụm thừa ở đầu tên.
    leading_phrases = [
        "danh sach cac ",
        "danh sach nhung ",
        "mot so ",
        "cac ",
        "nhung ",
        "lien quan den ",
        "lien quan toi ",
        "co chu de ",
        "theo chu de ",
        "chu de ",
        "ve ",
        "cua ",
        "cho ",
    ]

    # Các cụm mở đầu một yêu cầu khác.
    # Nếu xuất hiện ở giữa Entity thì cắt phần phía sau.
    stop_phrases = [
        " ban co the goi y",
        " ban hay goi y",
        " hay goi y",
        " goi y them",
        " ngoai ra",
        " ben canh do",
        " dong thoi",
        " va co khoa hoc nao",
        " va co nhung khoa hoc nao",
        " va khoa hoc nao",
        " co khoa hoc nao",
        " neu chua co",
        " neu khong co",
        " trong he thong",
        " ngoai he thong",
    ]

    # Các cụm thừa ở cuối tên.
    trailing_phrases = [
        " co duoc khong",
        " duoc khong",
        " co khong",
        " hay khong",
        " duoc chu",
        " giup toi",
        " giup minh",
        " cho toi",
        " cho minh",
        " cua rieng minh",
        " cua rieng toi",
        " cua ban than",
        " cua toi",
        " cua minh",
        " cho ban than",
        " nhe",
        " nha",
        " nhi",
        " vay",
        " the",
        " a",
        " oi",
        " di",
        " khong",
        " chua",
        " nao",
    ]

    changed = True

    while changed:
        previous = name

        name = name.strip(" \t\n.,!?;:\"'`")

        # Cắt phần yêu cầu khác phía sau Entity.
        for phrase in stop_phrases:
            index = name.find(phrase)

            if index > 0:
                name = name[:index].strip()

        # Xóa cụm thừa ở đầu.
        for phrase in leading_phrases:
            if name.startswith(phrase):
                name = name[len(phrase):].strip()

        # Xóa cụm thừa ở cuối.
        for phrase in trailing_phrases:
            if name.endswith(phrase):
                name = name[:-len(phrase)].strip()

        changed = name != previous

    if name in GENERIC_ENTITIES:
        return ""

    return name.strip(" \t\n.,!?;:\"'`")


def is_generic_entity(entity_name: str) -> bool:
    """Kiểm tra Entity có phải cụm chung chung không."""

    if not entity_name:
        return True

    normalized = normalize_text(entity_name)

    return normalized in GENERIC_ENTITIES


def normalize_entity_name(entity_name: str) -> str:
    """Chuẩn hóa tên công nghệ phổ biến."""

    if not entity_name:
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
    }

    normalized = normalize_text(entity_name)

    return known_names.get(normalized, entity_name.strip())


# ==========================================
# 5. ENTITY TYPE DETECTION
# ==========================================

def detect_entity_type(text: str) -> str:

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

    return "none"


# ==========================================
# 6. SKILL SEARCH ENTITY EXTRACTION
# ==========================================

def extract_skill_search_entity(user_message: str) -> dict:

    text = normalize_text(user_message)

    patterns = [
        r"(?:lien quan den|lien quan toi)\s+(.+?)[?.!]*$",

        r"(?:tim|search|find)\s+"
        r"(?:cho toi\s+|cho minh\s+)?"
        r"(?:cac\s+|nhung\s+)?"
        r"(?:skill|skills|ky nang)"
        r"\s+(?:ve|cua)?\s*(.+?)[?.!]*$",

        r"(?:skill|skills|ky nang)"
        r"\s+(?:ve|cua)\s+(.+?)[?.!]*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            entity_name = clean_entity_name(match.group(1))

            if entity_name:
                return {
                    "entity_type": "skill",
                    "entity_name": normalize_entity_name(entity_name),
                }

    return {
        "entity_type": "skill",
        "entity_name": None,
    }


# ==========================================
# 7. COURSE REVIEW ENTITY EXTRACTION
# ==========================================

def extract_course_review_entity(user_message: str) -> dict:

    text = normalize_text(user_message)

    patterns = [
        r"(?:khoa hoc|course|courses)"
        r"\s+(?:ve\s+)?(.+?)[?.!]*$",

        r"(?:on tap|kiem tra|lam bai|quiz|review)"
        r"\s+(?:khoa hoc|course)\s+(.+?)[?.!]*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            entity_name = clean_entity_name(match.group(1))

            if entity_name:
                return {
                    "entity_type": "course",
                    "entity_name": entity_name,
                }

    return {
        "entity_type": "course",
        "entity_name": None,
    }


# ==========================================
# 8. SKILL REVIEW ENTITY EXTRACTION
# ==========================================

def extract_skill_review_entity(user_message: str) -> dict:

    text = normalize_text(user_message)

    patterns = [
        r"(?:skill|skills|ky nang)"
        r"\s+(?:ve\s+)?(.+?)[?.!]*$",

        r"(?:on tap|kiem tra|lam bai|quiz|review)"
        r"\s+(?:ve\s+)?(.+?)[?.!]*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            entity_name = clean_entity_name(match.group(1))

            if entity_name:
                return {
                    "entity_type": "skill",
                    "entity_name": normalize_entity_name(entity_name),
                }

    return {
        "entity_type": "skill",
        "entity_name": None,
    }


# ==========================================
# 9. LEARNING PATH ENTITY EXTRACTION
# ==========================================

def extract_learning_path_entity(user_message: str) -> dict:
    """Trích xuất chủ đề người dùng muốn học."""

    text = normalize_text(user_message)

    patterns = [
        r"(?:tao|generate|create)\s+"
        r"(?:cho toi\s+|cho minh\s+)?"
        r"(?:mot\s+)?"
        r"(?:lo trinh hoc|learning path)"
        r"\s+(?:ve\s+|cho\s+)?(.+?)[?.!]*$",

        r"(?:lo trinh hoc|learning path)"
        r"\s+(?:ve\s+|cho\s+)(.+?)[?.!]*$",

        r"(?:hoc|learn)\s+"
        r"(.+?)\s+"
        r"(?:theo\s+)?(?:mot\s+)?"
        r"(?:lo trinh|learning path)[?.!]*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        entity_name = clean_entity_name(match.group(1))

        if entity_name:
            return {
                "entity_type": "skill",
                "entity_name": normalize_entity_name(entity_name),
            }

    return {
        "entity_type": "none",
        "entity_name": None,
    }


# ==========================================
# 10. COURSE SEARCH ENTITY EXTRACTION
# ==========================================

def extract_course_search_entity(user_message: str) -> dict:
    """
    Tìm chủ đề Skill mà người dùng muốn tìm Course.

    Ví dụ:
    - Python có những khóa học nào? -> Python
    - Tìm khóa học về SQL -> SQL
    - Cho tôi khóa học liên quan đến React -> React
    """

    text = normalize_text(user_message)

    patterns = [
        # Python có những khóa học nào?
        r"^(.+?)\s+co\s+"
        r"(?:nhung\s+|cac\s+)?"
        r"(?:khoa hoc|courses?)\s+nao",

        # Khóa học liên quan đến Python
        r"(?:khoa hoc|courses?)"
        r"\s+(?:ve|cua|cho|day|lien quan den|lien quan toi)"
        r"\s+(.+?)[?.!]*$",

        # Tìm các khóa học về Python
        r"(?:tim|search|find)\s+"
        r"(?:cho toi\s+|giup toi\s+)?"
        r"(?:cac\s+|nhung\s+)?"
        r"(?:khoa hoc|courses?)"
        r"\s+(?:ve|cua|cho|day|lien quan den)?\s*"
        r"(.+?)[?.!]*$",

        # Cho tôi khóa học của Python
        r"(?:cho toi|cho minh|toi muon)\s+"
        r"(?:nhung\s+|cac\s+)?"
        r"(?:khoa hoc|courses?)"
        r"\s+(?:cua|ve|cho|day|lien quan den)\s+"
        r"(.+?)[?.!]*$",

        # Danh sách khóa học Python
        r"(?:danh sach|liet ke)\s+"
        r"(?:cac\s+|nhung\s+)?"
        r"(?:khoa hoc|courses?)"
        r"\s+(?:ve|cua|cho|lien quan den)\s+"
        r"(.+?)[?.!]*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        entity_name = clean_entity_name(match.group(1))

        if entity_name:
            return {
                "entity_type": "skill",
                "entity_name": normalize_entity_name(entity_name),
            }

    return {
        "entity_type": "skill",
        "entity_name": None,
    }


# ==========================================
# 11. COURSE ENROLLMENT ENTITY EXTRACTION
# ==========================================

def extract_course_enrollment_entity(user_message: str) -> dict:
    """
    Trích xuất tên Course hoặc chủ đề Course cần tìm link.
    """

    text = normalize_text(user_message)

    patterns = [
        # Khóa học liên quan đến Python
        r"(?:lien quan den|lien quan toi)"
        r"\s+(.+?)[?.!]*$",

        # Khóa học về Python
        r"(?:khoa hoc|course|courses)"
        r"\s+(?:ve|cua|cho|day|co chu de)\s+"
        r"(.+?)[?.!]*$",

        # Link tham gia khóa học Python
        r"(?:link|duong dan|url).*?"
        r"(?:tham gia|dang ky|ghi danh|enroll|join)"
        r"\s+(?:vao\s+)?"
        r"(?:khoa hoc|course|courses)"
        r"\s+(.+?)[?.!]*$",

        # Tham gia khóa học Python
        r"(?:tham gia|dang ky|ghi danh|enroll|join)"
        r"\s+(?:vao\s+)?"
        r"(?:khoa hoc|course|courses)"
        r"\s+(.+?)[?.!]*$",

        # Khóa học Python
        r"(?:khoa hoc|course|courses)"
        r"\s+(.+?)[?.!]*$",
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        entity_name = clean_entity_name(match.group(1))

        if entity_name:
            return {
                "entity_type": "course",
                "entity_name": normalize_entity_name(entity_name),
            }

    return {
        "entity_type": "course",
        "entity_name": None,
    }


# ==========================================
# 12. GENERAL ENTITY EXTRACTION
# ==========================================

def extract_entity_by_rules(
    user_message: str,
    intent: str,
) -> dict:

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
        entity_type = "course"
        markers = [
            "khoa hoc",
            "course",
            "courses",
            "mon hoc",
        ]

    elif intent == "skill_question":
        entity_type = "skill"
        markers = [
            "ky nang",
            "kien thuc",
            "skill",
            "skills",
        ]

    else:
        return {
            "entity_type": "none",
            "entity_name": None,
        }

    normalized = normalize_text(user_message)

    for marker in sorted(markers, key=len, reverse=True):

        pattern = (
            re.escape(marker)
            + r"\s+(.+?)[?.!]*$"
        )

        match = re.search(
            pattern,
            normalized,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        entity_name = clean_entity_name(match.group(1))

        if entity_name:
            return {
                "entity_type": entity_type,
                "entity_name": normalize_entity_name(entity_name),
            }

    return {
        "entity_type": entity_type,
        "entity_name": None,
    }


# ==========================================
# 13. GEMINI ENTITY EXTRACTION
# ==========================================

def extract_entity_by_llm(user_message: str) -> dict:

    prompt = f"""
Bạn là Entity Extractor của EduMentor AI.

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
6. Không lấy cụm chỉ sở hữu:
   - của tôi
   - của riêng mình
   - cho bản thân
7. Không lấy cụm chỉ mục đích:
   - liên quan đến
   - trong hệ thống
   - ngoài hệ thống
8. Nếu câu có dạng "khóa học liên quan đến Python",
   Entity cần lấy là Python.
9. Nếu không có Entity cụ thể, trả về none và null.
10. Không xác nhận Entity tồn tại trong database.
11. Không giải thích.
12. Không Markdown.

Câu hỏi:
{user_message}
"""

    ai_text = generate_text(prompt)

    result = extract_json_object(ai_text)

    entity_type = result.get("entity_type")
    entity_name = result.get("entity_name")

    if entity_type not in ALLOWED_ENTITY_TYPES:
        entity_type = "none"

    entity_name = clean_entity_name(entity_name)

    if not entity_name or is_generic_entity(entity_name):
        return {
            "entity_type": "none",
            "entity_name": None,
        }

    entity_name = normalize_entity_name(entity_name)

    if entity_type == "none":
        entity_name = None

    return {
        "entity_type": entity_type,
        "entity_name": entity_name,
    }


# ==========================================
# 14. RULE-BASED INTENT CLASSIFICATION
# ==========================================

def classify_by_rules(user_message: str) -> dict | None:
    """Phân loại Intent bằng luật. Không gọi Gemini."""

    text = normalize_text(user_message)

    entity_type = detect_entity_type(user_message)

    # --------------------------------------
    # 1. CODE HELP
    # --------------------------------------

    code_keywords = [
        "doan code",
        "doan ma",
        "sua loi",
        "debug",
        "traceback",
        "exception",
        "giai thich code",
        "toi uu code",
        "loi code",
        "error trong code",
        "explain this code",
        "fix this code",
        "debug this",
    ]

    if (
        "```" in user_message
        or any(keyword in text for keyword in code_keywords)
    ):
        return {
            "intent": "code_help",
            "entity_type": "none",
            "entity_name": None,
        }

    # --------------------------------------
    # 2. COURSE ENROLLMENT LINK
    # --------------------------------------

    has_link_keyword = any(
        keyword in text
        for keyword in ["link", "duong dan", "url"]
    )

    has_course_keyword = any(
        keyword in text
        for keyword in ["khoa hoc", "course", "courses"]
    )

    if has_link_keyword and has_course_keyword:

        entity = extract_course_enrollment_entity(user_message)

        return {
            "intent": "course_enrollment_link",
            "entity_type": "course",
            "entity_name": entity["entity_name"],
        }

    # --------------------------------------
    # 3. LEARNING PATH CREATION
    # --------------------------------------

    learning_path_creation_keywords = [
        "tao lo trinh",
        "tao learning path",
        "generate learning path",
        "create learning path",
        "tao lo trinh hoc",
    ]

    has_learning_path = any(
        keyword in text
        for keyword in ["lo trinh", "learning path"]
    )

    has_creation_keyword = any(
        keyword in text
        for keyword in ["tao", "generate", "create"]
    )

    if (
        any(keyword in text for keyword in learning_path_creation_keywords)
        or (has_learning_path and has_creation_keyword)
    ):
        entity = extract_learning_path_entity(user_message)

        return {
            "intent": "learning_path_request",
            "entity_type": entity["entity_type"],
            "entity_name": entity["entity_name"],
        }

    # --------------------------------------
    # 4. REVIEW
    # --------------------------------------

    review_keywords = [
        "on tap",
        "kiem tra",
        "lam bai",
        "bai quiz",
        "trac nghiem",
        "quiz",
        "review",
        "practice test",
    ]

    if any(keyword in text for keyword in review_keywords):

        if entity_type == "course":
            entity = extract_course_review_entity(user_message)

            return {
                "intent": "course_review",
                "entity_type": "course",
                "entity_name": entity["entity_name"],
            }

        if entity_type == "skill" or any(
            keyword in text
            for keyword in ["skill", "skills", "ky nang", "kien thuc"]
        ):
            entity = extract_skill_review_entity(user_message)

            return {
                "intent": "skill_review",
                "entity_type": "skill",
                "entity_name": entity["entity_name"],
            }

        return None

    # --------------------------------------
    # 5. SKILL SEARCH
    # --------------------------------------

    skill_search_patterns = [
        r"(?:cho toi|cho minh|toi muon|liet ke|danh sach)"
        r".*(?:skill|skills|ky nang)"
        r".*(?:lien quan|ve|related)",

        r"(?:tim|search|find)"
        r".*(?:skill|skills|ky nang)",

        r"(?:nhung|cac)?\s*"
        r"(?:skill|skills|ky nang)"
        r".*(?:lien quan|ve)",

        r"(?:skill|skills|ky nang)"
        r".*(?:nao|danh sach|liet ke)",
    ]

    if any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in skill_search_patterns
    ):
        entity = extract_skill_search_entity(user_message)

        return {
            "intent": "skill_search",
            "entity_type": "skill",
            "entity_name": entity["entity_name"],
        }

    # --------------------------------------
    # 6. COURSE SEARCH
    # --------------------------------------

    course_search_patterns = [
        r".+\s+co\s+(?:nhung\s+|cac\s+)?"
        r"(?:khoa hoc|courses?)\s+nao",

        r"(?:cho toi|cho minh|toi muon)\s+"
        r"(?:nhung\s+|cac\s+)?"
        r"(?:khoa hoc|courses?)\s+"
        r"(?:cua|ve|cho|day|lien quan den)",

        r"(?:tim|search|find)\s+.*"
        r"(?:khoa hoc|courses?)",

        r"(?:danh sach|liet ke)\s+.*"
        r"(?:khoa hoc|courses?)",

        r"(?:khoa hoc|courses?)\s+"
        r"(?:ve|cua|cho|day|lien quan den)\s+.+",
    ]

    if any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in course_search_patterns
    ):
        entity = extract_course_search_entity(user_message)

        return {
            "intent": "course_search",
            "entity_type": "skill",
            "entity_name": entity["entity_name"],
        }

    # --------------------------------------
    # 7. SYSTEM OPERATION
    # --------------------------------------

    operation_keywords = [
        "cach su dung",
        "lam sao de",
        "lam sao",
        "huong dan",
        "cach tao",
        "cach luu",
        "cach xem",
        "cach quan ly",
        "cach dang nhap",
        "cach dang ky",
        "how to",
        "how can i",
    ]

    link_keywords = [
        "link",
        "duong dan",
        "url",
        "trang",
        "vao trang",
        "mo trang",
        "truy cap",
        "di toi",
        "open page",
        "go to",
    ]

    system_features = [
        "edumentor",
        "ai review",
        "learning path",
        "lo trinh",
        "tien do",
        "luu tien do",
        "dashboard",
        "tai khoan",
        "dang nhap",
        "dang ky",
        "login",
        "register",
        "bookmark",
        "danh dau",
        "luu khoa hoc",
        "my courses",
        "profile",
        "ho so",
        "quiz",
        "on tap",
        "skill",
    ]

    has_operation_request = any(
        keyword in text
        for keyword in operation_keywords
    )

    has_link_request = any(
        keyword in text
        for keyword in link_keywords
    )

    has_system_feature = any(
        keyword in text
        for keyword in system_features
    )

    auth_keywords = [
        "dang nhap",
        "dang ky",
        "login",
        "register",
    ]

    if (
        (has_operation_request or has_link_request)
        and has_system_feature
    ) or any(keyword in text for keyword in auth_keywords):

        return {
            "intent": "system_operation",
            "entity_type": "none",
            "entity_name": None,
        }

    # --------------------------------------
    # 8. COURSE QUESTION
    # --------------------------------------

    if entity_type == "course":
        return {
            "intent": "course_question",
            "entity_type": "course",
            "entity_name": None,
        }

    # --------------------------------------
    # 9. SKILL QUESTION
    # --------------------------------------

    if entity_type == "skill":
        return {
            "intent": "skill_question",
            "entity_type": "skill",
            "entity_name": None,
        }

    return None


# ==========================================
# 15. GEMINI INTENT CLASSIFICATION
# ==========================================

def build_classifier_prompt(user_message: str) -> str:

    return f"""
Bạn là Query Classifier của hệ thống EduMentor AI.

Nhiệm vụ:
Phân loại ý định người dùng và xác định Entity.

INTENT HỢP LỆ:

1. skill_question:
   Hỏi kiến thức về một Skill.

2. skill_review:
   Muốn ôn tập hoặc kiểm tra một Skill.

3. skill_search:
   Tìm danh sách Skill theo chủ đề.

4. course_question:
   Hỏi thông tin về một Course cụ thể.

5. course_review:
   Muốn ôn tập một Course.

6. course_search:
   Tìm các Course theo chủ đề hoặc tên Skill.

7. course_enrollment_link:
   Muốn lấy link tham gia hoặc đăng ký Course.

8. system_operation:
   Hỏi cách sử dụng hoặc thao tác trên EduMentor.

9. code_help:
   Giải thích, sửa lỗi hoặc tối ưu code.

10. learning_path_request:
    Muốn tạo lộ trình học bằng AI.

11. general_question:
    Câu hỏi kiến thức chung hoặc trường hợp khác.

ENTITY TYPE:
- skill
- course
- none

QUY TẮC PHÂN LOẠI:

- "Cho tôi những skill liên quan đến SQL"
  => skill_search, skill, SQL.

- "Tìm các kỹ năng về Python"
  => skill_search, skill, Python.

- "Python có những khóa học nào?"
  => course_search, skill, Python.

- "Cho tôi những khóa học của Python"
  => course_search, skill, Python.

- "Cho tôi khóa học liên quan đến Python"
  => course_search, skill, Python.

- "Cho tôi link để tham gia khóa học Analytical Solutions to Common Healthcare Problems"
  => course_enrollment_link, course,
     Analytical Solutions to Common Healthcare Problems.

- "Cho tôi link đăng ký khóa học Python"
  => course_enrollment_link, course, Python.

- "Cho tôi các link tham gia khóa học liên quan đến Python được không"
  => course_enrollment_link, course, Python.

- "Cho tôi link vào trang đăng nhập"
  => system_operation, none, null.

- "Làm sao lưu khóa học trên EduMentor?"
  => system_operation, none, null.

- "Hướng dẫn tôi tạo lộ trình của riêng mình"
  => learning_path_request, none, null.

- "Tạo lộ trình học Python"
  => learning_path_request, skill, Python.

- "Sau khi AI tạo lộ trình, tôi lưu thế nào?"
  => system_operation, none, null.

QUY TẮC QUAN TRỌNG:

1. Tạo lộ trình học là learning_path_request.
2. Lưu, xem, chỉnh sửa, quản lý lộ trình là system_operation.
3. Hỏi cách thao tác trên EduMentor là system_operation.
4. Hỏi kiến thức Skill là skill_question.
5. Hỏi thông tin Course là course_question.
6. Hỏi tìm khóa học theo Skill là course_search.
7. Hỏi link tham gia khóa học là course_enrollment_link.
8. Không lấy "của riêng mình", "của tôi",
   "cho bản thân" làm Entity.
9. Không lấy "liên quan đến" làm Entity.
10. Không lấy "được không", "nhé", "ạ" làm Entity.
11. Không tự nghĩ ra tên Skill hoặc Course.
12. Không tự xác nhận Entity tồn tại trong database.
13. Không tự tạo ID.
14. Nếu không có tên cụ thể, entity_name là null.
15. Không nhầm tên Course với Skill.
16. Nếu không chắc chắn, chọn general_question.
17. Chỉ phân loại yêu cầu trong câu được cung cấp.
18. Không tự thêm yêu cầu khác.

CHỈ TRẢ VỀ JSON HỢP LỆ:

{{
    "intent": "skill_search",
    "entity_type": "skill",
    "entity_name": "SQL"
}}

Câu hỏi:
{user_message}
"""


def classify_by_llm(user_message: str) -> dict:

    prompt = build_classifier_prompt(user_message)

    ai_text = generate_text(prompt)

    result = extract_json_object(ai_text)

    intent = result.get("intent")
    entity_type = result.get("entity_type")
    entity_name = result.get("entity_name")

    if intent not in ALLOWED_INTENTS:
        raise ValueError("Intent không hợp lệ.")

    if entity_type not in ALLOWED_ENTITY_TYPES:
        entity_type = "none"

    entity_name = clean_entity_name(entity_name)

    if not entity_name or is_generic_entity(entity_name):
        entity_name = None

    elif entity_type != "none":
        entity_name = normalize_entity_name(entity_name)

    return {
        "intent": intent,
        "entity_type": entity_type,
        "entity_name": entity_name,
    }


# ==========================================
# 16. SINGLE QUERY ROUTER
# ==========================================

def _route_single_query(user_message: str) -> dict:
    """
    Xử lý một yêu cầu đơn lẻ.

    Pipeline:
    1. Rule-based intent classification.
    2. Gemini classification nếu Rule không nhận diện được.
    3. Rule-based entity extraction.
    4. Gemini entity extraction nếu cần.
    5. Enforce entity type.
    6. Quyết định retrieval modes.
    7. Xác định operation type.
    """

    result = classify_by_rules(user_message)

    if result is not None:
        source = "rule"

    else:
        try:
            result = classify_by_llm(user_message)
            source = "llm"

        except Exception as error:

            print(
                "[QUERY ROUTER] LLM classification failed:",
                str(error),
            )

            result = {
                "intent": "general_question",
                "entity_type": "none",
                "entity_name": None,
            }

            source = "fallback"

    intent = result["intent"]

    # --------------------------------------
    # STEP 1. RULE-BASED ENTITY EXTRACTION
    # --------------------------------------

    entity = extract_entity_by_rules(
        user_message=user_message,
        intent=intent,
    )

    entity_type = result.get("entity_type", "none")
    entity_name = result.get("entity_name")

    if entity.get("entity_name"):
        entity_name = entity["entity_name"]
        entity_type = entity["entity_type"]

    # --------------------------------------
    # STEP 2. OPTIONAL LLM ENTITY EXTRACTION
    # --------------------------------------

    if (
        source == "llm"
        and intent in ENTITY_REQUIRED_INTENTS
        and entity_name is None
    ):

        try:
            llm_entity = extract_entity_by_llm(user_message)

            if llm_entity.get("entity_name"):
                entity_name = llm_entity["entity_name"]
                entity_type = llm_entity["entity_type"]
                source = "hybrid"

        except Exception as error:

            print(
                "[QUERY ROUTER] Entity extraction failed:",
                str(error),
            )

    # --------------------------------------
    # STEP 3. ENFORCE ENTITY TYPE
    # --------------------------------------

    if intent in {
        "skill_question",
        "skill_review",
        "skill_search",
    }:
        entity_type = "skill"

    elif intent == "course_search":
        entity_type = "skill"

    elif intent in {
        "course_question",
        "course_review",
        "course_enrollment_link",
    }:
        entity_type = "course"

    elif intent == "learning_path_request":

        if entity_name:
            entity_type = "skill"
        else:
            entity_type = "none"

    else:
        entity_type = "none"
        entity_name = None

    if is_generic_entity(entity_name):
        entity_name = None

        if intent == "learning_path_request":
            entity_type = "none"

    # --------------------------------------
    # STEP 4. RETRIEVAL DECISION
    # --------------------------------------

    retrieval_modes = RETRIEVAL_MAP[intent].copy()

    if intent == "learning_path_request" and entity_name:
        retrieval_modes = ["sql", "rag"]

    # --------------------------------------
    # STEP 5. OPERATION TYPE
    # --------------------------------------

    operation_type = None

    if intent == "system_operation":
        operation_type = detect_operation_type(user_message)

    # --------------------------------------
    # STEP 6. RETURN
    # --------------------------------------

    return {
        "intent": intent,
        "operation_type": operation_type,
        "retrieval_modes": retrieval_modes,
        "entity_type": entity_type,
        "entity_name": entity_name,
        "source": source,
        "query": user_message,
    }


# ==========================================
# 17. MULTI-QUERY DETECTION
# ==========================================

def may_contain_multiple_requests(user_message: str) -> bool:
    """
    Kiểm tra sơ bộ xem tin nhắn có khả năng chứa
    nhiều yêu cầu độc lập hay không.

    Đây chỉ là bước phát hiện sơ bộ.
    Gemini mới quyết định có thực sự cần tách hay không.
    """

    text = normalize_text(user_message)

    connectors = [
        " ngoai ra ",
        " ben canh do ",
        " dong thoi ",
        " them nua ",
        " them cho toi ",
        " con ",
        " va ",
        " neu ",
        " sau do ",
        " tiep theo ",
        " khong nhung ",
        " ma con ",
        " cung nhu ",
        ";",
        "\n",
        "? ",
    ]

    return any(connector in text for connector in connectors)


# ==========================================
# 18. GEMINI MULTI-QUERY DECOMPOSITION
# ==========================================

def decompose_query_by_llm(user_message: str) -> list:
    """
    Dùng Gemini tách một tin nhắn thành các yêu cầu độc lập.

    Chú ý:
    Hàm này chỉ tách yêu cầu.
    Không phân loại intent ở bước này.
    """

    prompt = f"""
Bạn là Query Decomposer của EduMentor AI.

NHIỆM VỤ:
Phân tích tin nhắn người dùng và tách thành các yêu cầu
độc lập có thể cần xử lý riêng.

QUY TẮC:

1. Một tin nhắn có thể có một hoặc nhiều yêu cầu.
2. Không giới hạn số lượng yêu cầu.
3. Không phụ thuộc vào dấu chấm, dấu phẩy hoặc dấu hỏi.
4. Phải hiểu các từ nối tiếng Việt như:
   - ngoài ra
   - bên cạnh đó
   - thêm nữa
   - và
   - còn
   - đồng thời
   - nếu có thể
   - nếu chưa có
   - sau đó
   - tiếp theo
5. Chỉ tách khi người dùng thực sự đưa ra một yêu cầu
   có thể xử lý độc lập.
6. Không tách một yêu cầu thành nhiều câu nhỏ chỉ vì
   người dùng yêu cầu giải thích nhiều khía cạnh.
7. Giữ nguyên ngữ cảnh và chủ đề chung.
8. Không tự thêm yêu cầu người dùng không nói.
9. Không bỏ sót yêu cầu nào.
10. Giữ nguyên tên công nghệ, Skill, Course.
11. Nếu chỉ có một yêu cầu, trả về một phần tử.
12. Không phân loại intent ở bước này.
13. Không trả lời câu hỏi.
14. Không giải thích.
15. Không tự chuyển yêu cầu gợi ý bên ngoài hệ thống
    thành yêu cầu tìm kiếm trong database.

VÍ DỤ 1:

Đầu vào:
SQL là gì bạn giải thích giúp tôi với ngoài ra trong hệ thống
có những skill nào liên quan đến SQL và có khóa học nào không

Đầu ra:
{{
    "queries": [
        "SQL là gì? Giải thích cho tôi.",
        "Trong hệ thống có những Skill nào liên quan đến SQL?",
        "Có khóa học nào liên quan đến SQL không?"
    ]
}}

VÍ DỤ 2:

Đầu vào:
Tìm skill liên quan đến Python và gợi ý thêm những skill
ngoài hệ thống.

Đầu ra:
{{
    "queries": [
        "Tìm các Skill liên quan đến Python trong hệ thống.",
        "Gợi ý thêm các Skill liên quan đến Python ngoài hệ thống."
    ]
}}

VÍ DỤ 3:

Đầu vào:
Giải thích SQL và cho ví dụ về JOIN.

Đầu ra:
{{
    "queries": [
        "Giải thích SQL và cho ví dụ về JOIN."
    ]
}}

Lý do:
Đây là một yêu cầu giải thích kiến thức có kèm ví dụ,
không phải hai yêu cầu độc lập.

VÍ DỤ 4:

Đầu vào:
Tôi muốn học Python, tìm khóa học phù hợp,
tạo lộ trình học và hướng dẫn cách lưu tiến độ.

Đầu ra:
{{
    "queries": [
        "Tôi muốn học Python.",
        "Tìm khóa học phù hợp với Python.",
        "Tạo lộ trình học Python.",
        "Hướng dẫn cách lưu tiến độ học."
    ]
}}

ĐỊNH DẠNG ĐẦU RA:

Chỉ trả về JSON hợp lệ theo cấu trúc:

{{
    "queries": [
        "Yêu cầu thứ nhất",
        "Yêu cầu thứ hai"
    ]
}}

TIN NHẮN NGƯỜI DÙNG:
{user_message}
"""

    ai_text = generate_text(prompt)

    result = extract_json_object(ai_text)

    queries = result.get("queries")

    if not isinstance(queries, list):
        raise ValueError("LLM không trả về danh sách queries.")

    cleaned_queries = []

    for query in queries:

        if not isinstance(query, str):
            continue

        query = query.strip()

        if query and query not in cleaned_queries:
            cleaned_queries.append(query)

    if not cleaned_queries:
        raise ValueError("Không tách được yêu cầu từ câu hỏi.")

    return cleaned_queries


# ==========================================
# 19. MAIN MULTI-QUERY ROUTER
# ==========================================

def route_query(user_message: str) -> dict:
    """
    Router tổng.

    Pipeline:

    1. Validate input.
    2. Kiểm tra khả năng có nhiều yêu cầu.
    3. Nếu cần, dùng Gemini tách yêu cầu.
    4. Phân loại từng yêu cầu riêng biệt.
    5. Tổng hợp kết quả.
    6. Trả về sub_queries cho chatbot service.

    Lưu ý:
    retrieval_modes ở cấp ngoài là danh sách hợp nhất.
    Khi xử lý từng yêu cầu, phải dùng retrieval_modes
    nằm bên trong từng sub_query.
    """

    if (
        not isinstance(user_message, str)
        or not user_message.strip()
    ):
        raise ValueError("Câu hỏi không được để trống.")

    user_message = user_message.strip()

    # --------------------------------------
    # STEP 1. DEFAULT: ONE QUERY
    # --------------------------------------

    queries = [user_message]

    # --------------------------------------
    # STEP 2. CHECK MULTIPLE REQUESTS
    # --------------------------------------

    if may_contain_multiple_requests(user_message):

        try:
            queries = decompose_query_by_llm(user_message)

        except Exception as error:

            print(
                "[QUERY ROUTER] Decomposition failed:",
                str(error),
            )

            # Nếu Gemini tách lỗi, quay lại xử lý
            # toàn bộ tin nhắn như một yêu cầu.
            queries = [user_message]

    # --------------------------------------
    # STEP 3. ROUTE EACH SUB-QUERY
    # --------------------------------------

    sub_queries = []

    for query in queries:

        try:
            route = _route_single_query(query)

        except Exception as error:

            print(
                "[QUERY ROUTER] Single query routing failed:",
                str(error),
            )

            route = {
                "intent": "general_question",
                "operation_type": None,
                "retrieval_modes": ["no_rag"],
                "entity_type": "none",
                "entity_name": None,
                "source": "fallback",
                "query": query,
            }

        sub_queries.append({
            "query": query,
            "intent": route["intent"],
            "operation_type": route.get("operation_type"),
            "retrieval_modes": route["retrieval_modes"],
            "entity_type": route["entity_type"],
            "entity_name": route["entity_name"],
            "source": route["source"],
        })

    # --------------------------------------
    # STEP 4. COMBINE RETRIEVAL MODES
    # --------------------------------------

    all_modes = []

    for item in sub_queries:

        for mode in item["retrieval_modes"]:

            if mode not in all_modes:
                all_modes.append(mode)

    # --------------------------------------
    # STEP 5. BACKWARD COMPATIBILITY
    # --------------------------------------

    # Các service cũ có thể vẫn đang đọc:
    # route["intent"]
    # route["entity_name"]
    # route["retrieval_modes"]
    #
    # Vì vậy giữ lại các trường này ở cấp ngoài.
    #
    # Tuy nhiên, chúng chỉ đại diện cho yêu cầu đầu tiên.

    primary = sub_queries[0]

    # --------------------------------------
    # STEP 6. RETURN
    # --------------------------------------

    return {
        "intent": primary["intent"],
        "operation_type": primary["operation_type"],
        "retrieval_modes": all_modes,
        "entity_type": primary["entity_type"],
        "entity_name": primary["entity_name"],
        "source": primary["source"],
        "query": user_message,

        # Thông tin mới dành cho multi-query.
        "is_compound": len(sub_queries) > 1,
        "sub_queries": sub_queries,
    }
