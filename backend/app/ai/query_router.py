
import json
import re

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


# ==========================================
# 2. TEXT NORMALIZATION
# ==========================================

def normalize_text(text: str) -> str:
    return text.lower().strip()


def detect_operation_type(user_message: str) -> str:
    """
    Phân biệt người dùng chỉ xin đường dẫn với người dùng cần
    hướng dẫn thao tác từng bước trên hệ thống.
    """

    text = normalize_text(user_message)

    step_by_step_keywords = [
        "hướng dẫn", "huong dan",
        "cách", "cach",
        "làm sao", "lam sao",
        "how to", "how can i",
        "đã truy cập", "da truy cap",
        "đã vào", "da vao",
        "đang ở trang", "dang o trang",
        "đã mở trang", "da mo trang",
        "tôi vào rồi", "toi vao roi",
        "bước tiếp theo", "buoc tiep theo",
        "cần nhập", "can nhap",
        "cần điền", "can dien",
        "thực hiện như thế nào", "thuc hien nhu the nao",
    ]

    if any(keyword in text for keyword in step_by_step_keywords):
        return "step_by_step"

    direct_link_keywords = [
        "link",
        "đường dẫn", "duong dan",
        "url",
        "địa chỉ trang", "dia chi trang",
        "truy cập trang nào", "truy cap trang nao",
        "vào trang nào", "vao trang nao",
        "cho tôi link", "cho toi link",
    ]

    if any(keyword in text for keyword in direct_link_keywords):
        return "direct_link"

    return "general_operation"


def clean_entity_name(entity_name: str) -> str:
    """
    Làm sạch tên Skill/Course trước khi truy vấn SQL.

    Không tự ý xóa những từ có thể thuộc tên Course.
    """

    if not isinstance(entity_name, str):
        return ""

    entity_name = entity_name.strip()

    stop_phrases = [
        r"\s+để\s+ôn\s+tập.*$",
        r"\s+de\s+on\s+tap.*$",
        r"\s+ôn\s+tập.*$",
        r"\s+on\s+tap.*$",
        r"\s+tham\s+gia.*$",
        r"\s+vào\s+ôn\s+tập.*$",
        r"\s+trong\s+hệ\s+thống.*$",
        r"\s+trong\s+he\s+thong.*$",
        r"\s+ngoài\s+hệ\s+thống.*$",
        r"\s+ngoai\s+he\s+thong.*$",
        r"\s+giúp\s+tôi.*$",
        r"\s+giup\s+toi.*$",
    ]

    for pattern in stop_phrases:
        entity_name = re.sub(
            pattern,
            "",
            entity_name,
            flags=re.IGNORECASE,
        )

    trailing_words = [
        "nào", "nao",
        "không", "khong",
        "chưa", "chua",
        "vậy", "vay",
        "thế", "the",
        "ạ", "nhỉ", "nhi",
        "nhé", "nhe",
        "đi", "giùm", "giup",
    ]

    while True:
        previous = entity_name

        entity_name = entity_name.strip(" \t\n.,!?;:\"'`")

        for word in trailing_words:
            entity_name = re.sub(
                rf"\s+{re.escape(word)}$",
                "",
                entity_name,
                flags=re.IGNORECASE,
            ).strip()

        if entity_name == previous:
            break

    return entity_name.strip(" \t\n.,!?;:\"'`")


def normalize_entity_name(entity_name: str) -> str:
    """
    Chuẩn hóa một số tên Skill phổ biến.
    """

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
    }

    return known_names.get(
        entity_name.casefold(),
        entity_name,
    )


# ==========================================
# 3. ENTITY TYPE DETECTION
# ==========================================

def detect_entity_type(text: str) -> str:

    normalized = normalize_text(text)

    course_keywords = [
        "khóa học",
        "khoa hoc",
        "course",
        "courses",
        "môn học",
        "mon hoc",
    ]

    skill_keywords = [
        "skill",
        "skills",
        "kỹ năng",
        "ky nang",
        "kiến thức",
        "kien thuc",
    ]

    if any(keyword in normalized for keyword in course_keywords):
        return "course"

    if any(keyword in normalized for keyword in skill_keywords):
        return "skill"

    return "none"


# ==========================================
# 4. SKILL SEARCH ENTITY EXTRACTION
# ==========================================

def extract_skill_search_entity(user_message: str) -> dict:

    text = user_message.strip()

    patterns = [
        (
            r"(?:liên quan đến|lien quan den|"
            r"liên quan tới|lien quan toi)"
            r"\s+(.+?)(?:\s+trong hệ thống.*)?[?.!]*$"
        ),
        (
            r"(?:tìm|tim|search|find)\s+"
            r"(?:cho tôi\s+|cho mình\s+)?"
            r"(?:các\s+|những\s+)?"
            r"(?:skill|skills|kỹ năng|ky nang)"
            r"\s+(?:về|ve|của|cua)?\s*(.+?)[?.!]*$"
        ),
        (
            r"(?:skill|skills|kỹ năng|ky nang)"
            r"\s+(?:về|ve|của|cua)\s+(.+?)[?.!]*$"
        ),
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            entity_name = clean_entity_name(match.group(1))
            entity_name = normalize_entity_name(entity_name)

            if entity_name:
                return {
                    "entity_type": "skill",
                    "entity_name": entity_name,
                }

    return {
        "entity_type": "skill",
        "entity_name": None,
    }


# ==========================================
# 5. COURSE REVIEW ENTITY EXTRACTION
# ==========================================

def extract_course_review_entity(user_message: str) -> dict:

    text = user_message.strip()

    patterns = [
        (
            r"(?:khóa học|khoa hoc|course|courses)"
            r"\s+(?:về\s+|ve\s+)?"
            r"(.+?)$"
        ),
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
        entity_name = normalize_entity_name(entity_name)

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
# 6. SKILL REVIEW ENTITY EXTRACTION
# ==========================================

def extract_skill_review_entity(user_message: str) -> dict:

    text = user_message.strip()

    patterns = [
        (
            r"\b(?:skill|skills|kỹ năng|ky nang)"
            r"\s+(?:về\s+|ve\s+)?"
            r"(.+?)"
            r"(?:\s+để\s+ôn\s+tập.*"
            r"|\s+de\s+on\s+tap.*"
            r"|\s+ôn\s+tập.*"
            r"|\s+on\s+tap.*"
            r"|\s+tham\s+gia.*)?$"
        ),
        (
            r"(?:ôn\s+tập|on\s+tap|kiểm\s+tra|kiem\s+tra"
            r"|làm\s+bài|lam\s+bai|quiz|review)"
            r"\s+(?:về\s+|ve\s+)?"
            r"(.+?)$"
        ),
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            entity_name = clean_entity_name(match.group(1))
            entity_name = normalize_entity_name(entity_name)

            if entity_name:
                return {
                    "entity_type": "skill",
                    "entity_name": entity_name,
                }

    return {
        "entity_type": "skill",
        "entity_name": None,
    }


# ==========================================
# 7. LEARNING PATH ENTITY EXTRACTION
# ==========================================

def extract_learning_path_entity(user_message: str) -> dict:

    text = user_message.strip()

    patterns = [
        (
            r"(?:(?:hãy|hay|tôi muốn|toi muon|"
            r"hướng dẫn tôi|huong dan toi|"
            r"giúp tôi|giup toi)\s+)?"
            r"(?:tạo|tao|generate|create)\s+"
            r"(?:cho tôi\s+|cho mình\s+|cho minh\s+)?"
            r"(?:một\s+)?"
            r"(?:lộ trình học|lo trinh hoc|learning path)"
            r"\s+(?:về\s+|ve\s+|cho\s+)?"
            r"(.+?)[?.!]*$"
        ),
        (
            r"(?:lộ trình học|lo trinh hoc|learning path)"
            r"\s+(?:về\s+|ve\s+|cho\s+)"
            r"(.+?)[?.!]*$"
        ),
        (
            r"(?:học|hoc|learn)\s+"
            r"(.+?)\s+"
            r"(?:theo\s+)?(?:một\s+)?"
            r"(?:lộ trình|lo trinh|learning path)"
            r"[?.!]*$"
        ),
    ]

    generic_entities = {
        "của riêng mình",
        "cua rieng minh",
        "riêng mình",
        "rieng minh",
        "của tôi",
        "cua toi",
        "của bản thân",
        "cua ban than",
        "cho bản thân",
        "cho ban than",
        "cá nhân",
        "ca nhan",
        "bản thân",
        "ban than",
        "mình",
        "minh",
        "tôi",
        "toi",
    }

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if not match:
            continue

        entity_name = clean_entity_name(match.group(1))

        if not entity_name:
            continue

        if entity_name.casefold().strip() in generic_entities:
            continue

        entity_name = normalize_entity_name(entity_name)

        return {
            "entity_type": "skill",
            "entity_name": entity_name,
        }

    return {
        "entity_type": "none",
        "entity_name": None,
    }


# ==========================================
# 8. COURSE SEARCH ENTITY EXTRACTION
# ==========================================

def extract_course_search_entity(user_message: str) -> dict:

    text = user_message.strip()

    patterns = [
        (
            r"(?:liên quan đến|lien quan den|"
            r"liên quan tới|lien quan toi)"
            r"\s+(.+?)[?.!]*$"
        ),
        (
            r"(?:khóa học|khoa hoc|courses?)"
            r"\s+(?:về|ve|của|cua|cho|dạy|day)"
            r"\s+(.+?)[?.!]*$"
        ),
        (
            r"^(.+?)\s+có\s+(?:những\s+|các\s+)?"
            r"(?:khóa học|khoa hoc|courses?)\s+nào"
        ),
        (
            r"^(?:cho tôi\s+|cho mình\s+|tôi muốn\s+)?"
            r"(?:những\s+|các\s+)?"
            r"(?:khóa học|khoa hoc|courses?)\s+"
            r"(?:của|cua|về|ve|cho|dạy|day)"
            r"\s+(.+?)[?.!]*$"
        ),
        (
            r"^(?:tìm|tim|search|find)\s+"
            r"(?:cho tôi\s+|giúp tôi\s+)?"
            r"(?:các\s+|những\s+)?"
            r"(?:khóa học|khoa hoc|courses?)"
            r"\s+(?:về|ve|của|cua|cho|dạy|day)?"
            r"\s*(.+?)[?.!]*$"
        ),
        (
            r"^(?:ở đây\s+|o day\s+)?"
            r"(?:có\s+|co\s+)?"
            r"(?:những\s+|các\s+)?"
            r"(?:khóa học|khoa hoc|courses?)"
            r"\s+(.+?)\s+nào(?:\s+không)?[?.!]*$"
        ),
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

        if not entity_name:
            continue

        entity_name = normalize_entity_name(entity_name)

        return {
            "entity_type": "skill",
            "entity_name": entity_name,
        }

    return {
        "entity_type": "skill",
        "entity_name": None,
    }


# ==========================================
# 9. COURSE ENROLLMENT ENTITY EXTRACTION
# ==========================================

def extract_course_enrollment_entity(user_message: str) -> dict:
    """
    Trích xuất tên khóa học khi người dùng muốn lấy
    link tham gia hoặc đăng ký một Course cụ thể.
    """

    text = user_message.strip()

    patterns = [
        # khóa học trực tiếp ABC
        (
            r"(?:khóa học|khoa hoc|courses?)"
            r"\s+(?:trực tiếp\s+)?"
            r"(.+?)[?.!]*$"
        ),

        # tham gia khóa học ABC
        (
            r"(?:tham gia|đăng ký|dang ky|ghi danh|enroll|join)"
            r"\s+(?:vào\s+|vao\s+)?"
            r"(?:khóa học|khoa hoc|courses?)"
            r"\s+(?:trực tiếp\s+)?"
            r"(.+?)[?.!]*$"
        ),

        # link để tham gia khóa học ABC
        (
            r"(?:link|đường dẫn|duong dan|url)"
            r"\s+(?:để\s+|de\s+)?"
            r"(?:tham gia|đăng ký|dang ky|ghi danh)"
            r"\s+(?:khóa học|khoa hoc|course|courses)"
            r"\s+(?:trực tiếp\s+)?"
            r"(.+?)[?.!]*$"
        ),
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

        if not entity_name:
            continue

        return {
            "entity_type": "course",
            "entity_name": entity_name,
        }

    return {
        "entity_type": "course",
        "entity_name": None,
    }


# ==========================================
# 10. GENERAL ENTITY EXTRACTION
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

    text = user_message.strip()

    if intent == "skill_search":
        return extract_skill_search_entity(text)

    if intent == "course_search":
        return extract_course_search_entity(text)

    if intent == "skill_review":
        return extract_skill_review_entity(text)

    if intent == "course_review":
        return extract_course_review_entity(text)

    entity_type = detect_entity_type(text)

    if entity_type == "course":
        markers = [
            "khóa học",
            "khoa hoc",
            "courses",
            "course",
            "môn học",
            "mon hoc",
        ]

    elif entity_type == "skill":
        markers = [
            "kỹ năng",
            "ky nang",
            "kiến thức",
            "kien thuc",
            "skills",
            "skill",
        ]

    else:
        markers = []

    for marker in sorted(markers, key=len, reverse=True):

        pattern = re.escape(marker) + r"\s+(.+)$"

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            entity_name = clean_entity_name(match.group(1))
            entity_name = normalize_entity_name(entity_name)

            if entity_name:
                return {
                    "entity_type": entity_type,
                    "entity_name": entity_name,
                }

    return {
        "entity_type": entity_type,
        "entity_name": None,
    }


# ==========================================
# 11. GEMINI ENTITY EXTRACTION
# ==========================================

def extract_entity_by_llm(user_message: str) -> dict:

    prompt = f"""
Bạn là Entity Extractor của hệ thống EduMentor AI.

Nhiệm vụ:
Xác định tên Skill hoặc Course mà người dùng đang nhắc đến.

Chỉ trả về JSON hợp lệ:

{{
    "entity_type": "skill",
    "entity_name": "Python"
}}

Quy tắc:

- entity_type chỉ được là skill, course hoặc none.
- entity_name là tên đối tượng thực sự được nhắc đến.
- Không lấy từ nghi vấn như: nào, gì, không, vậy.
- Không lấy các từ chung chung như: khóa học, kỹ năng.
- Không lấy các cụm chỉ mục đích như "liên quan đến",
  "trong hệ thống", "ngoài hệ thống".
- Không lấy cụm chỉ sở hữu như "của tôi", "của riêng mình".
- Không tự nghĩ ra tên nếu người dùng không cung cấp.
- Nếu không xác định được, dùng none và null.
- Không xác nhận đối tượng tồn tại trong database.
- Không giải thích.
- Không Markdown.

Câu hỏi:
{user_message}
"""

    ai_text = generate_text(prompt)

    if not ai_text or not ai_text.strip():
        raise ValueError("Gemini không trả về Entity.")

    text = ai_text.strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\s*```$", "", text)

    result = json.loads(text)

    if not isinstance(result, dict):
        raise ValueError("Entity phải là JSON object.")

    entity_type = result.get("entity_type")
    entity_name = result.get("entity_name")

    if entity_type not in ALLOWED_ENTITY_TYPES:
        entity_type = "none"

    entity_name = clean_entity_name(entity_name)
    entity_name = normalize_entity_name(entity_name)

    if not entity_name:
        entity_name = None

    return {
        "entity_type": entity_type,
        "entity_name": entity_name,
    }


# ==========================================
# 12. RULE-BASED INTENT CLASSIFICATION
# ==========================================

def classify_by_rules(user_message: str) -> dict | None:
    """
    Phân loại Intent bằng luật.
    Hàm này không gọi Gemini.
    """

    text = normalize_text(user_message)

    entity_type = detect_entity_type(text)

    # --------------------------------------
    # 1. CODE HELP
    # --------------------------------------

    code_keywords = [
        "đoạn code",
        "doan code",
        "đoạn mã",
        "doan ma",
        "sửa lỗi",
        "sua loi",
        "debug",
        "traceback",
        "exception",
        "giải thích code",
        "giai thich code",
        "tối ưu code",
        "toi uu code",
        "lỗi code",
        "loi code",
        "error trong code",
        "explain this code",
        "fix this code",
        "debug this",
    ]

    has_code_block = "```" in user_message

    if has_code_block or any(keyword in text for keyword in code_keywords):
        return {
            "intent": "code_help",
            "entity_type": "none",
            "entity_name": None,
        }

    # --------------------------------------
    # 2. COURSE ENROLLMENT LINK
    # Phải đặt trước SYSTEM OPERATION.
    # --------------------------------------

    has_link_keyword = any(
        keyword in text
        for keyword in [
            "link",
            "đường dẫn",
            "duong dan",
            "url",
        ]
    )

    has_course_keyword = any(
        keyword in text
        for keyword in [
            "khóa học",
            "khoa hoc",
            "course",
            "courses",
        ]
    )

    has_enrollment_keyword = any(
        keyword in text
        for keyword in [
            "tham gia",
            "đăng ký",
            "dang ky",
            "ghi danh",
            "enroll",
            "join",
        ]
    )

    if (
        has_link_keyword
        and has_course_keyword
        and has_enrollment_keyword
    ):
        entity = extract_course_enrollment_entity(user_message)

        return {
            "intent": "course_enrollment_link",
            "entity_type": "course",
            "entity_name": entity["entity_name"],
        }

    # --------------------------------------
    # 3. LEARNING PATH
    # --------------------------------------

    learning_path_keywords = [
        "tạo lộ trình",
        "tao lo trinh",
        "tạo learning path",
        "tao learning path",
        "generate learning path",
        "create learning path",
        "lộ trình học",
        "lo trinh hoc",
        "learning path",
    ]

    if any(keyword in text for keyword in learning_path_keywords):
        return {
            "intent": "learning_path_request",
            "entity_type": "none",
            "entity_name": None,
        }

    # --------------------------------------
    # 4. REVIEW
    # --------------------------------------

    review_keywords = [
        "ôn tập",
        "on tap",
        "kiểm tra",
        "kiem tra",
        "làm bài",
        "lam bai",
        "bài quiz",
        "bai quiz",
        "trắc nghiệm",
        "trac nghiem",
        "quiz",
        "review",
        "practice test",
    ]

    if any(keyword in text for keyword in review_keywords):

        if entity_type == "course":
            return {
                "intent": "course_review",
                "entity_type": "course",
                "entity_name": None,
            }

        if entity_type == "skill":
            return {
                "intent": "skill_review",
                "entity_type": "skill",
                "entity_name": None,
            }

        if re.search(r"\bskill\b|\bskills\b|kỹ năng|ky nang", text):
            return {
                "intent": "skill_review",
                "entity_type": "skill",
                "entity_name": None,
            }

        return None

    # --------------------------------------
    # 5. SKILL SEARCH
    # --------------------------------------

    skill_search_patterns = [
        r"(?:cho tôi|cho mình|tôi muốn|liệt kê|danh sách)"
        r".*(?:skill|skills|kỹ năng|ky nang)"
        r".*(?:liên quan|lien quan|về|ve|related)",

        r"(?:tìm|tim|search|find)"
        r".*(?:skill|skills|kỹ năng|ky nang)",

        r"(?:những|các)?\s*(?:skill|skills|kỹ năng|ky nang)"
        r".*(?:liên quan|lien quan)",

        r"(?:skill|skills|kỹ năng|ky nang)"
        r".*(?:nào|danh sách|liệt kê)",
    ]

    if any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in skill_search_patterns
    ):
        return {
            "intent": "skill_search",
            "entity_type": "skill",
            "entity_name": None,
        }

    # --------------------------------------
    # 6. COURSE SEARCH
    # --------------------------------------

    course_search_patterns = [
        r".+\s+có\s+(?:những\s+|các\s+)?"
        r"(?:khóa học|khoa hoc|courses?)\s+nào",

        r"(?:cho tôi|cho mình|tôi muốn)\s+"
        r"(?:những\s+|các\s+)?"
        r"(?:khóa học|khoa hoc|courses?)\s+"
        r"(?:của|cua|về|ve|cho|dạy|day|liên quan đến|lien quan den)\s+.+",

        r"(?:tìm|tim|search|find)\s+.*"
        r"(?:khóa học|khoa hoc|courses?)",

        r"(?:có|co)\s+(?:những\s+|các\s+)?"
        r"(?:khóa học|khoa hoc|courses?)\s+.+",

        r"(?:khóa học|khoa hoc|courses?)\s+"
        r"(?:về|ve|của|cua|dạy|day|liên quan đến|lien quan den)\s+.+",

        r"(?:danh sách|liệt kê)\s+.*"
        r"(?:khóa học|khoa hoc|courses?)",
    ]

    if any(
        re.search(pattern, text, flags=re.IGNORECASE)
        for pattern in course_search_patterns
    ):
        return {
            "intent": "course_search",
            "entity_type": "skill",
            "entity_name": None,
        }

    # --------------------------------------
    # 7. SYSTEM OPERATION
    # --------------------------------------

    link_keywords = [
        "link",
        "đường dẫn",
        "duong dan",
        "url",
        "trang",
        "vào trang",
        "vao trang",
        "mở trang",
        "mo trang",
        "truy cập",
        "truy cap",
        "đi tới",
        "di toi",
        "open page",
        "go to",
    ]

    operation_keywords = [
        "cách sử dụng",
        "cach su dung",
        "làm sao để",
        "lam sao de",
        "làm sao",
        "lam sao",
        "hướng dẫn",
        "huong dan",
        "cách tạo",
        "cach tao",
        "cách lưu",
        "cach luu",
        "cách xem",
        "cach xem",
        "cách quản lý",
        "cach quan ly",
        "cách đăng nhập",
        "cach dang nhap",
        "cách đăng ký",
        "cach dang ky",
        "how to",
        "how can i",
    ]

    system_features = [
        "edumentor",
        "ai review",
        "learning path",
        "lộ trình",
        "lo trinh",
        "tiến độ",
        "tien do",
        "lưu tiến độ",
        "luu tien do",
        "khóa học",
        "khoa hoc",
        "course",
        "dashboard",
        "tài khoản",
        "tai khoan",
        "đăng nhập",
        "dang nhap",
        "đăng ký",
        "dang ky",
        "login",
        "register",
        "bookmark",
        "đánh dấu",
        "danh dau",
        "lưu khóa học",
        "luu khoa hoc",
        "my courses",
        "profile",
        "hồ sơ",
        "ho so",
        "quiz",
        "ôn tập",
        "on tap",
        "skill",
    ]

    has_link_request = any(keyword in text for keyword in link_keywords)
    has_operation_request = any(keyword in text for keyword in operation_keywords)
    has_system_feature = any(keyword in text for keyword in system_features)

    if has_link_request and has_system_feature:
        return {
            "intent": "system_operation",
            "entity_type": "none",
            "entity_name": None,
        }

    if has_operation_request and has_system_feature:
        return {
            "intent": "system_operation",
            "entity_type": "none",
            "entity_name": None,
        }

    auth_keywords = [
        "đăng nhập",
        "dang nhap",
        "đăng ký",
        "dang ky",
        "login",
        "register",
    ]

    if any(keyword in text for keyword in auth_keywords):
        return {
            "intent": "system_operation",
            "entity_type": "none",
            "entity_name": None,
        }

    # --------------------------------------
    # 8. COURSE QUESTION
    # --------------------------------------

    course_question_keywords = [
        "khóa học",
        "khoa hoc",
        "course",
        "courses",
        "môn học",
        "mon hoc",
    ]

    if any(keyword in text for keyword in course_question_keywords):
        return {
            "intent": "course_question",
            "entity_type": "course",
            "entity_name": None,
        }

    # --------------------------------------
    # 9. SKILL QUESTION
    # --------------------------------------

    skill_question_keywords = [
        "skill",
        "skills",
        "kỹ năng",
        "ky nang",
        "kiến thức",
        "kien thuc",
    ]

    if any(keyword in text for keyword in skill_question_keywords):
        return {
            "intent": "skill_question",
            "entity_type": "skill",
            "entity_name": None,
        }

    return None


# ==========================================
# 13. GEMINI INTENT CLASSIFICATION
# ==========================================

def build_classifier_prompt(user_message: str) -> str:

    return f"""
Bạn là Query Classifier của hệ thống EduMentor AI.

Nhiệm vụ:
Phân loại ý định của người dùng.

Các Intent hợp lệ:

1. skill_question:
   Người dùng hỏi kiến thức hoặc muốn tìm hiểu một Skill.

2. skill_review:
   Người dùng muốn ôn tập hoặc kiểm tra một Skill.

3. skill_search:
   Người dùng muốn tìm danh sách Skill theo chủ đề
   hoặc tìm các Skill có liên quan với nhau.

4. course_question:
   Người dùng hỏi thông tin về một Course cụ thể.

5. course_review:
   Người dùng muốn ôn tập một Course.

6. course_search:
   Người dùng muốn tìm các khóa học trong EduMentor
   theo tên hoặc theo chủ đề.

7. course_enrollment_link:
   Người dùng muốn lấy link tham gia, đăng ký hoặc ghi danh
   vào một khóa học cụ thể.

8. system_operation:
   Người dùng hỏi cách sử dụng hoặc thao tác trên EduMentor,
   bao gồm yêu cầu link đến trang chức năng.

9. code_help:
   Người dùng muốn giải thích, sửa lỗi hoặc tối ưu code.

10. learning_path_request:
    Người dùng muốn tạo lộ trình học bằng AI.

11. general_question:
    Câu hỏi kiến thức chung hoặc trường hợp khác.

Entity type hợp lệ:
- skill
- course
- none

Quy tắc:

- "Cho tôi những skill liên quan đến SQL"
  => skill_search, skill, SQL.

- "Tìm các kỹ năng về Python"
  => skill_search, skill, Python.

- "Python có những khóa học nào?"
  => course_search, skill, Python.

- "Cho tôi những khóa học của Python"
  => course_search, skill, Python.

- "Cho tôi link để tham gia khóa học Analytical Solutions
  to Common Healthcare Problems"
  => course_enrollment_link, course,
     Analytical Solutions to Common Healthcare Problems.

- "Cho tôi link đăng ký khóa học Python"
  => course_enrollment_link, course, Python.

- "Cho tôi link vào trang đăng nhập"
  => system_operation, none, null.

- "Làm sao lưu khóa học trên EduMentor?"
  => system_operation, none, null.

- "Hướng dẫn tôi tạo lộ trình của riêng mình"
  => learning_path_request, none, null.

- "Tạo lộ trình học Python"
  => learning_path_request, skill, Python.

- "Tôi muốn tạo lộ trình học về SQL"
  => learning_path_request, skill, SQL.

- Nếu người dùng hỏi thông tin một khóa học cụ thể,
  dùng course_question và entity_type là course.

- Nếu người dùng hỏi kiến thức về một Skill,
  dùng skill_question và entity_type là skill.

- Nếu hỏi cách thao tác trong EduMentor,
  chọn system_operation.

- Nếu hỏi cách tạo lộ trình học,
  chọn learning_path_request.

- Nếu hỏi cách ôn tập Course,
  chọn course_review.

- Nếu hỏi cách ôn tập Skill,
  chọn skill_review.

- Không lấy cụm "của riêng mình", "của tôi",
  "cho bản thân" làm Entity.
- Không tự xác nhận Skill hoặc Course tồn tại trong database.
- Không tự tạo ID.
- Nếu không xác định được tên, entity_name là null.

Chỉ trả về JSON hợp lệ, không Markdown.

Cấu trúc:

{{
    "intent": "skill_search",
    "entity_type": "skill",
    "entity_name": "SQL"
}}

Câu hỏi người dùng:
{user_message}
"""


def classify_by_llm(user_message: str) -> dict:

    prompt = build_classifier_prompt(user_message)

    ai_text = generate_text(prompt)

    if not ai_text or not ai_text.strip():
        raise ValueError("Gemini không trả về kết quả phân loại.")

    text = ai_text.strip()

    if text.startswith("```"):
        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )
        text = re.sub(r"\s*```$", "", text)

    result = json.loads(text)

    if not isinstance(result, dict):
        raise ValueError("Kết quả phân loại phải là JSON object.")

    intent = result.get("intent")
    entity_type = result.get("entity_type")
    entity_name = result.get("entity_name")

    if intent not in ALLOWED_INTENTS:
        raise ValueError("Intent không hợp lệ.")

    if entity_type not in ALLOWED_ENTITY_TYPES:
        entity_type = "none"

    entity_name = clean_entity_name(entity_name)
    entity_name = normalize_entity_name(entity_name)

    if not entity_name:
        entity_name = None

    return {
        "intent": intent,
        "entity_type": entity_type,
        "entity_name": entity_name,
    }


# ==========================================
# 14. MAIN QUERY ROUTER
# ==========================================

def route_query(user_message: str) -> dict:

    if (
        not isinstance(user_message, str)
        or not user_message.strip()
    ):
        raise ValueError("Câu hỏi không được để trống.")

    # ======================================
    # STEP 1. RULE-BASED INTENT CLASSIFICATION
    # ======================================

    result = classify_by_rules(user_message)

    if result is not None:
        source = "rule"

    else:
        # ==================================
        # STEP 2. GEMINI CLASSIFICATION
        # ==================================

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

    # ======================================
    # STEP 3. RULE-BASED ENTITY EXTRACTION
    # ======================================

    entity = extract_entity_by_rules(
        user_message=user_message,
        intent=intent,
    )

    entity_type = result.get("entity_type", "none")
    entity_name = result.get("entity_name")

    if entity["entity_name"] is not None:
        entity_name = entity["entity_name"]
        entity_type = entity["entity_type"]

    # ======================================
    # STEP 4. OPTIONAL LLM ENTITY EXTRACTION
    # ======================================

    if (
        source == "llm"
        and intent in ENTITY_REQUIRED_INTENTS
        and entity_name is None
    ):

        try:
            llm_entity = extract_entity_by_llm(user_message)

            if llm_entity["entity_name"] is not None:
                entity_name = llm_entity["entity_name"]
                entity_type = llm_entity["entity_type"]
                source = "hybrid"

        except Exception as error:

            print(
                "[QUERY ROUTER] Entity extraction failed:",
                str(error),
            )

    # ======================================
    # STEP 5. ENFORCE ENTITY TYPE
    # ======================================

    if intent in {
        "skill_search",
        "skill_question",
        "skill_review",
    }:
        entity_type = "skill"

    if intent == "course_search" and entity_name is not None:
        entity_type = "skill"

    if intent in {
        "course_question",
        "course_review",
        "course_enrollment_link",
    }:
        entity_type = "course"

    # Intent không cần Entity.
    if (
        intent not in ENTITY_REQUIRED_INTENTS
        and intent != "learning_path_request"
    ):
        entity_type = "none"
        entity_name = None

    # Learning Path có Entity tùy chọn.
    if intent == "learning_path_request" and not entity_name:
        entity_type = "none"
        entity_name = None

    # ======================================
    # STEP 6. BACKEND RETRIEVAL DECISION
    # ======================================

    retrieval_modes = RETRIEVAL_MAP[intent].copy()

    # Learning Path:
    # - Không có Skill: RAG.
    # - Có Skill: SQL + RAG.

    if intent == "learning_path_request" and entity_name:
        retrieval_modes = ["sql", "rag"]

    # ======================================
    # STEP 7. OPERATION TYPE
    # ======================================

    operation_type = None

    if intent == "system_operation":
        operation_type = detect_operation_type(user_message)

    # ======================================
    # STEP 8. RETURN
    # ======================================

    return {
        "intent": intent,
        "operation_type": operation_type,
        "retrieval_modes": retrieval_modes,
        "entity_type": entity_type,
        "entity_name": entity_name,
        "source": source,
        "query": user_message,
    }
