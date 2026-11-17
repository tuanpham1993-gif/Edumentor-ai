
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
    "organization",
    "instructor",
    "rating",
    "level",
    "popular",
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
    "lien quan ve",
    "lien quan",
    "nao lien quan nua",
    "lien quan nua",
    "nao lien quan",
    "nao nua",
    "nua",
    "khac",
    "nao khac",
    "con lai",
    "them",
    "nua khong",
    "khac khong",
    "nao",
    "gi nua",
    "gi khac",
    "con gi nua",
    "khoa hoc",
    "cac khoa hoc",
    "nhung khoa hoc",
    "ky nang",
    "cac ky nang",
    "nhung ky nang",
    "none",
    "null",
    "duoc hoc nhieu nhat",
    "hoc nhieu nhat",
    "nhieu nguoi hoc nhat",
    "pho bien nhat",
    "noi bat nhat",
    "noi bat",
    "pho bien",
    "hot nhat",
    "top",
    "hay nhat",
    "tot nhat",
}

COMMON_TECH_SKILLS = [
    # Ngôn ngữ & Môi trường chạy
    "python", "sql", "javascript", "js", "typescript", "ts", "html", "css",
    "c++", "cpp", "c#", "java", "golang", "go", "php", "ruby", "rust",
    # Framework & Thư viện
    "react", "reactjs", "vue", "angular", "nextjs", "nodejs", "express",
    "fastapi", "django", "flask", "spring", "bootstrap", "tailwind",
    "pandas", "numpy", "matplotlib", "seaborn", "scikit-learn", "sklearn",
    "pytorch", "tensorflow", "keras",
    # Cơ sở dữ liệu & DevOps
    "postgresql", "postgres", "mysql", "mongodb", "sqlite", "redis",
    "docker", "kubernetes", "k8s", "git", "github", "gitlab", "linux", "bash",
    # Lĩnh vực & Kiến trúc
    "machine learning", "deep learning", "ai", "artificial intelligence",
    "data", "data analysis", "data analyst", "data science", "data engineer",
    "backend", "frontend", "fullstack", "devops", "rest api", "graphql",
    "web accessibility", "accessibility", "a11y", "ui/ux", "ui ux", "figma",
    "microservices", "oop",
    # Khái niệm lập trình cốt lõi
    "list comprehension", "dictionary", "dict", "tuple", "lambda",
    "generator", "decorator", "recursion", "de quy", "closure",
    "con tro", "pointer", "struct", "class", "object", "interface",
    "inheritance", "ke thua", "polymorphism", "da hinh", "encapsulation",
    "join", "inner join", "left join", "right join", "full join",
    "groupby", "group by", "having", "aggregate", "window function",
    "index", "trigger", "stored procedure", "view", "transaction",
    "primary key", "khoa chinh", "foreign key", "khoa ngoai", "deadlock",
    "async await", "promise", "callback", "thread", "multiprocessing",
    "regex", "regular expression", "vong lap", "for loop", "while loop",
    "ham", "function", "bien", "variable", "mang", "array",
    "linked list", "danh sach lien ket", "stack", "queue", "hang doi",
    "tree", "binary tree", "cay nhi phan", "graph",
    "bubble sort", "quick sort", "merge sort", "binary search",
    "tim kiem nhi phan", "bfs", "dfs", "dynamic programming", "quy hoach dong"
]

COMMON_CODE_ERRORS = [
    "keyerror", "indexerror", "typeerror", "valueerror", "syntaxerror",
    "attributeerror", "nameerror", "zerodivisionerror", "importerror",
    "modulenotfounderror", "indentationerror", "recursionerror",
    "stopiteration", "filenotfounderror", "permissionerror", "overflowerror",
    "runtimeerror", "unboundlocalerror", "nullpointerexception",
    "segmentation fault", "segfault", "out of memory", "stack overflow"
]


# ==========================================
# 2. TEXT NORMALIZATION
# ==========================================

def remove_accents(text: str) -> str:
    """Loại bỏ dấu tiếng Việt để so sánh từ khóa."""

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
    """
    Chuẩn hóa văn bản phục vụ so sánh và nhận diện pattern.

    Lưu ý:
    Hàm này không dùng để lưu tên Entity cuối cùng,
    vì nó chuyển chữ thành chữ thường và bỏ dấu.
    """

    if not isinstance(text, str):
        return ""

    # Tách khoảng cách nếu dấu câu/ngoặc bị viết liền với từ (ví dụ: (a11y)trong -> (a11y) trong)
    text = re.sub(r"([)\]}>,;!?])([a-zA-Z0-9_À-ỹ])", r"\1 \2", text)
    text = re.sub(r"([a-zA-Z0-9_À-ỹ])([(<\[{])", r"\1 \2", text)

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
# 4. ENTITY NORMALIZATION
# ==========================================

def clean_entity_name(entity_name: str) -> str:
    """
    Làm sạch tên Entity:
    1. Loại bỏ khoảng trắng và dấu câu ở hai đầu.
    2. Loại bỏ các cụm từ đệm, từ để hỏi hoặc trợ từ đuôi/đầu
       (ví dụ: 'nào không', 'có không', 'ạ', 'cho tôi xem đi', 'trong hệ thống của bạn').
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
        r"^(?:co\s+|con\s+|chua\s+|day\s+|giang\s+day\s+|chuyen\s+ve\s+|ve\s+|cho\s+|lien\s+quan\s+(?:den|toi|ve)\s+|lien\s+quan\s+)",
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
        "nao", "nua", "khac", "lien quan", "lien quan nua", "lien quan khac",
        "nao nua", "nao khac", "con lai", "them", "gi", "sao", "the nao", "ra sao"
    }
    if remove_accents(name).strip() in standalone_noise:
        return ""

    return name


def is_generic_entity(entity_name: str) -> bool:
    """Kiểm tra Entity có phải cụm chung chung không."""

    if not isinstance(entity_name, str) or not entity_name.strip():
        return True

    normalized = normalize_text(entity_name)

    return normalized in GENERIC_ENTITIES


def normalize_entity_name(entity_name: str) -> str:
    """
    Chuẩn hóa cách viết một số tên công nghệ phổ biến.

    Không xóa từ và không thay đổi tên Entity không nằm
    trong danh sách alias.
    """

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


def finalize_entity(entity_name: str) -> str | None:
    """
    Chuẩn hóa Entity sau khi trích xuất.

    Không làm sạch nội dung bên trong tên.
    Chỉ trả về None nếu Entity rỗng hoặc chung chung.
    """

    entity_name = clean_entity_name(entity_name)

    if not entity_name or is_generic_entity(entity_name):
        return None

    return normalize_entity_name(entity_name)


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

    # Kiểm tra xem có chứa tên kỹ năng / công nghệ / khái niệm lập trình
    for skill in sorted(COMMON_TECH_SKILLS, key=len, reverse=True):
        if re.search(r"\b" + re.escape(skill) + r"\b", normalized):
            return "skill"

    # Các từ khóa hỏi khái niệm lập trình
    explanation_markers = [
        "la gi", "giai thich", "khai niem", "hoat dong nhu the nao",
        "hoat dong ra sao", "dung de lam gi", "cach dung", "cach viet"
    ]
    if any(marker in normalized for marker in explanation_markers):
        return "skill"

    return "none"


# ==========================================
# 6. SKILL SEARCH ENTITY EXTRACTION
# ==========================================

def extract_skill_search_entity(user_message: str) -> dict:
    """
    Trích xuất chủ đề Skill người dùng muốn tìm.

    Ví dụ:
    - Tìm skill về Python -> Python
    - Skill nào liên quan đến SQL? -> SQL
    - Trong hệ thống có skill nào liên quan đến SQL cần học không?
      -> SQL
    """

    text = normalize_text(user_message)

    # 1. Kiểm tra câu hỏi tiếp nối / đại từ tham chiếu (anaphoric)
    anaphoric_markers = [
        "skill do", "ky nang do", "khoa hoc do", "mon do", "chu de do",
        "skill nay", "ky nang nay", "khoa hoc nay", "mon nay", "chu de nay",
        "do thi sao", "cai do", "no thi sao", "ve no", "den no", "ve chung", "den chung",
        "nao nua", "nua khong", "con nua", "con khac", "gi nua", "gi khac",
    ]
    if any(re.search(r"\b" + re.escape(m) + r"\b", text) for m in anaphoric_markers):
        return {
            "entity_type": "skill",
            "entity_name": None,
        }

    # 1.1. Tiêu chí Kỹ năng nổi bật / Được học nhiều nhất (Popular skills)
    popular_skill_markers = [
        "duoc hoc nhieu nhat", "hoc nhieu nhat", "nhieu nguoi hoc nhat",
        "pho bien nhat", "noi bat nhat", "noi bat", "hot nhat", "pho bien",
        "hang dau", "tieu bieu", "quan trong nhat", "hay nhat", "tot nhat"
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

    # 2. Khớp các mẫu câu ngữ pháp trích xuất đầy đủ tên kỹ năng
    patterns = [
        # "Có skill nào liên quan đến/về SQL cần học không?"
        # Dừng trước các cụm diễn đạt yêu cầu phía sau Entity.
        (
            r"(?:skill|skills|ky nang|kien thuc)"
            r".*?"
            r"(?:lien quan den|lien quan toi|lien quan ve|ve)"
            r"\s+(.+?)"
            r"(?=\s+(?:can hoc|nen hoc|muon hoc|co the hoc|"
            r"phu hop|trong he thong|ngoai he thong)\b|[?.!]*$)"
        ),

        # "Những skill liên quan đến/về SQL"
        (
            r"(?:lien quan den|lien quan toi|lien quan ve)"
            r"\s+(.+?)"
            r"(?=\s+(?:can hoc|nen hoc|muon hoc|co the hoc|"
            r"phu hop|trong he thong|ngoai he thong)\b|[?.!]*$)"
        ),

        # "Tìm skill về SQL"
        (
            r"(?:tim|search|find)"
            r"\s+(?:cho toi\s+|cho minh\s+)?"
            r"(?:cac\s+|nhung\s+)?"
            r"(?:skill|skills|ky nang)"
            r"\s+(?:ve|cua)?\s*(.+?)[?.!]*$"
        ),

        # "Skill về SQL" / "kỹ năng về SQL"
        (
            r"(?:skill|skills|ky nang)"
            r"\s+(?:ve|cua)\s+(.+?)[?.!]*$"
        ),

        # "kỹ năng nào liên quan về/đến SQL" (có 'nào' chen giữa)
        (
            r"(?:skill|skills|ky nang)"
            r"\s+(?:nao\s+)?"
            r"(?:lien quan\s+)?(?:den|toi|ve)"
            r"\s+(.+?)[?.!]*$"
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

        raw_match = match.group(1)
        # Giữ nguyên hoa/thường nếu user_message khớp độ dài
        start, end = match.span(1)
        if len(user_message) == len(text):
            raw_match = user_message[start:end]

        entity_name = finalize_entity(raw_match)

        if entity_name:
            return {
                "entity_type": "skill",
                "entity_name": entity_name,
            }

    # 3. Fallback: nếu câu hỏi nhắc đến một kỹ năng / công nghệ đã biết
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


# ==========================================
# 7. COURSE REVIEW ENTITY EXTRACTION
# ==========================================

def extract_course_review_entity(user_message: str) -> dict:

    text = normalize_text(user_message)

    patterns = [
        (
            r"(?:khoa hoc|course|courses)"
            r"\s+(?:ve\s+)?(.+?)[?.!]*$"
        ),
        (
            r"(?:on tap|kiem tra|lam bai|quiz|review)"
            r"\s+(?:khoa hoc|course)\s+(.+?)[?.!]*$"
        ),
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
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


# ==========================================
# 8. SKILL REVIEW ENTITY EXTRACTION
# ==========================================

def extract_skill_review_entity(user_message: str) -> dict:

    text = normalize_text(user_message)

    patterns = [
        (
            r"(?:skill|skills|ky nang)"
            r"\s+(?:ve\s+)?(.+?)[?.!]*$"
        ),
        (
            r"(?:on tap|kiem tra|lam bai|quiz|review)"
            r"\s+(?:ve\s+)?(.+?)[?.!]*$"
        ),
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            entity_name = finalize_entity(match.group(1))

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
# 9. LEARNING PATH ENTITY EXTRACTION
# ==========================================

def extract_learning_path_entity(user_message: str) -> dict:
    """Trích xuất chủ đề người dùng muốn học."""

    text = normalize_text(user_message)

    patterns = [
        # Gợi ý/Tư vấn/Tạo lộ trình các kỹ năng để trở thành Lập trình viên Web Full Stack
        (
            r"(?:lo trinh|learning path).*?(?:de\s+)?(?:tro thanh|lam)\s+(.+?)[?.!]*$"
        ),
        (
            r"(?:goi y|tu van|de xuat|tao|xay dung|generate|create).*?(?:lo trinh|learning path)\s+(?:cac ky nang\s+)?(?:can hoc\s+)?(?:de\s+)?(?:tro thanh\s+)?(?:ve\s+|cho\s+)?(.+?)[?.!]*$"
        ),
        (
            r"(?:tao|generate|create)\s+"
            r"(?:cho toi\s+|cho minh\s+)?"
            r"(?:mot\s+)?"
            r"(?:lo trinh hoc|learning path)"
            r"\s+(?:ve\s+|cho\s+)?(.+?)[?.!]*$"
        ),
        (
            r"(?:lo trinh hoc|learning path|lo trinh)\s+(?:ve\s+|cho\s+|hoc\s+)?(.+?)[?.!]*$"
        ),
        (
            r"(?:hoc|learn)\s+"
            r"(.+?)\s+"
            r"(?:theo\s+)?(?:mot\s+)?"
            r"(?:lo trinh|learning path)[?.!]*$"
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

        raw_match = match.group(1).strip()
        # Loại bỏ các từ đệm ở đầu: "học", "cho", "về", "các kỹ năng"
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


# ==========================================
# 10. COURSE SEARCH ENTITY EXTRACTION
# ==========================================

def extract_course_search_entity(user_message: str) -> dict:
    """
    Tìm chủ đề Skill hoặc tiêu chí (tổ chức, giảng viên, rating, cấp độ)
    mà người dùng muốn tìm Course.

    Ví dụ:
    - Python có những khóa học nào? -> skill: Python
    - Khóa học của University of Alberta -> organization: University of Alberta
    - Khóa học của giảng viên Martha White -> instructor: Martha White
    - Khóa học 5 sao / đánh giá cao nhất -> rating: 5
    - Khóa học cấp độ cơ bản / beginner -> level: beginner
    """

    text = normalize_text(user_message)

    # 1. Kiểm tra câu hỏi tiếp nối / đại từ tham chiếu (anaphoric)
    is_course_by_instructor = bool(
        re.search(r"\bkhoa hoc do\s+(?:day|giang day|huong dan)\b", text)
        or re.search(r"\bkhoa hoc do\s+[a-z\s]+?\s+(?:day|giang day)\b", text)
    )
    anaphoric_markers = [
        "khoa hoc do thi sao", "ve khoa hoc do", "mon hoc do", "mon do", "course do",
        "khoa hoc nay", "mon nay", "course nay",
        "skill do", "ky nang do", "chu de do",
        "cai do", "do thi sao", "no thi sao", "ve no", "den no",
        "nao nua", "nua khong", "con nua", "con khac", "gi nua", "gi khac",
    ]
    if not is_course_by_instructor:
        if (
            any(re.search(r"\b" + re.escape(m) + r"\b", text) for m in anaphoric_markers)
            or re.search(r"\bkhoa hoc do\b(?:\s+(?:thi|co|la|nhu the nao|gom|chua|[?.!]))?", text)
        ):
            return {
                "entity_type": "skill",
                "entity_name": None,
            }

    # 1.1. Tiêu chí Được học nhiều nhất / Nổi bật / Phổ biến (Popular / Most Enrolled)
    popular_course_markers = [
        "duoc hoc nhieu nhat", "hoc nhieu nhat", "nhieu nguoi hoc nhat",
        "pho bien nhat", "noi bat nhat", "hot nhat", "hang dau",
        "top khoa hoc", "khoa hoc noi bat", "khoa hoc pho bien", "khoa hoc hot",
        "noi bat", "pho bien"
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

    # 2. Tiêu chí Đánh giá / Rating (5 sao, đánh giá cao nhất,...)
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

    # 3. Tiêu chí Cấp độ / Level
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
            return {
                "entity_type": "level",
                "entity_name": lvl,
            }

    # 4. Tiêu chí Giảng viên (Instructor)
    instructor_patterns = [
        r"(?:khoa hoc|courses?).*?(?:cua|do|boi)?\s*(?:giang vien|giao vien|thay|co|instructor)\s+(.+?)(?=\s+(?:day|giang day|trong he thong|tren he thong|cho toi|co khong)\b|[?.!]*$)",
        r"(?:giang vien|giao vien|thay|co|instructor)\s+(.+?)\s+(?:co\s+)?(?:nhung\s+|cac\s+)?(?:khoa hoc|courses?)",
        r"(?:khoa hoc|courses?).*?(?:do|boi)\s+(.+?)\s+(?:day|giang day)",
        r"(?:giang vien|giao vien|thay|co|instructor)\s+([a-zA-Z0-9\s.'-]+?)(?=\s+(?:day|giang day|trong he thong|tren he thong|cho toi|co khong)\b|[?.!]*$)",
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

    # 5. Tiêu chí Tổ chức / Trường đại học (Organization)
    org_patterns = [
        r"(?:khoa hoc|courses?).*?(?:cua|tu|thuoc)\s+(?:to chuc|truong dai hoc|truong|dai hoc|vien|doi tac)?\s*(.+?)(?=\s+(?:trong he thong|tren he thong|cho toi|co khong)\b|[?.!]*$)",
        r"(?:to chuc|truong dai hoc|truong|dai hoc|vien|doi tac)\s+(.+?)\s+(?:co\s+)?(?:nhung\s+|cac\s+)?(?:khoa hoc|courses?)",
        r"(?:to chuc|truong dai hoc|truong|dai hoc|vien|doi tac)\s+([a-zA-Z0-9\s.'-]+?)(?=\s+(?:trong he thong|tren he thong|cho toi|co khong)\b|[?.!]*$)",
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

    # 6. Mẫu câu ngữ pháp tìm khóa học theo Kỹ năng / Chủ đề
    patterns = [
        # các khóa học có kỹ năng HTML / chứa kỹ năng Python
        (
            r"(?:khoa hoc|courses?)\s+(?:co\s+|chua\s+)?(?:ky nang|skill)\s+(.+?)[?.!]*$"
        ),

        # Python có những khóa học nào?
        (
            r"^(.+?)\s+co\s+"
            r"(?:nhung\s+|cac\s+)?"
            r"(?:khoa hoc|courses?)\s+nao"
        ),

        # Khóa học liên quan đến Python / dạy Python / có Python / có khóa học nào liên quan đến
        (
            r"(?:co\s+)?(?:nhung\s+|cac\s+)?"
            r"(?:khoa hoc|courses?)"
            r"\s+(?:nao\s+)?"
            r"(?:ve|cua|cho|day|giang day|chuyen ve|lien quan den|lien quan toi|lien quan ve|co|chua)"
            r"\s+(.+?)[?.!]*$"
        ),

        # Tìm các khóa học về Python
        (
            r"(?:tim|search|find)\s+"
            r"(?:cho toi\s+|giup toi\s+|cho minh\s+)?"
            r"(?:cac\s+|nhung\s+)?"
            r"(?:khoa hoc|courses?)"
            r"\s+(?:nao\s+)?"
            r"(?:ve|cua|cho|day|giang day|chuyen ve|lien quan den|lien quan toi|lien quan ve|co|chua)?\s*"
            r"(.+?)[?.!]*$"
        ),

        # Cho tôi khóa học của Python / cho tôi xem khóa học ...
        (
            r"(?:cho toi|cho minh|toi muon)\s+"
            r"(?:xem\s+)?"
            r"(?:nhung\s+|cac\s+)?"
            r"(?:khoa hoc|courses?)\s*"
            r"(?:nao\s+)?"
            r"(?:cua|ve|cho|day|giang day|lien quan den|lien quan toi|lien quan ve|co|chua)?\s*"
            r"(.+?)[?.!]*$"
        ),

        # Danh sách khóa học Python
        (
            r"(?:danh sach|liet ke)\s+"
            r"(?:cac\s+|nhung\s+)?"
            r"(?:khoa hoc|courses?)\s*"
            r"(?:nao\s+)?"
            r"(?:ve|cua|cho|day|lien quan den|lien quan toi|lien quan ve|co|chua)?\s*"
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

    # 7. Fallback: nếu câu hỏi nhắc đến một kỹ năng / công nghệ đã biết
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


# ==========================================
# 11. COURSE ENROLLMENT ENTITY EXTRACTION
# ==========================================

def extract_course_enrollment_entity(user_message: str) -> dict:
    """Trích xuất tên Course hoặc chủ đề Course cần tìm link."""

    text = normalize_text(user_message)

    patterns = [
        # Khóa học liên quan đến Python
        (
            r"(?:khoa hoc|course|courses).*?"
            r"(?:lien quan den|lien quan toi|lien quan ve)"
            r"\s+(.+?)[?.!]*$"
        ),

        # Khóa học về Python
        (
            r"(?:khoa hoc|course|courses)"
            r"\s+(?:ve|cua|cho|day|co chu de)\s+"
            r"(.+?)[?.!]*$"
        ),

        # Link tham gia khóa học Python
        (
            r"(?:link|duong dan|url).*?"
            r"(?:tham gia|dang ky|ghi danh|enroll|join)"
            r"\s+(?:vao\s+)?"
            r"(?:khoa hoc|course|courses)"
            r"\s+(.+?)[?.!]*$"
        ),

        # Tham gia khóa học Python
        (
            r"(?:tham gia|dang ky|ghi danh|enroll|join)"
            r"\s+(?:vao\s+)?"
            r"(?:khoa hoc|course|courses)"
            r"\s+(.+?)[?.!]*$"
        ),

        # Khóa học Python
        (
            r"(?:khoa hoc|course|courses)"
            r"\s+(.+?)[?.!]*$"
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

        entity_name = finalize_entity(match.group(1))

        if entity_name:
            return {
                "entity_type": entity_type,
                "entity_name": entity_name,
            }

    # Bổ sung trích xuất nâng cao cho skill_question
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

        # Quét tên công nghệ / kỹ năng có sẵn
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


# ==========================================
# 13. GEMINI ENTITY EXTRACTION
# ==========================================

def extract_entity_by_llm(user_message: str) -> dict:

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
9. Nếu câu có dạng "skill liên quan đến SQL cần học không",
   Entity cần lấy là SQL.
10. Giữ nguyên tên Course nhiều từ.
11. Không tự ý rút gọn tên Course.
12. Nếu không có Entity cụ thể, trả về none và null.
13. Không xác nhận Entity tồn tại trong database.
14. Không giải thích.
15. Không Markdown.

Câu hỏi:
{user_message}
"""

    ai_text = generate_text(prompt)

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
        "bi loi",
        "bao loi",
        "fix loi",
        "fix bug",
        "loi nay la sao",
        "loi gi",
        "chay khong duoc",
        "loi runtime",
        "loi syntax",
    ]

    code_error_match = any(err in text for err in COMMON_CODE_ERRORS)
    code_syntax_match = any(
        kw in user_message
        for kw in ["def ", "class ", "import ", "return ", "const ", "let ", "console.log", "SELECT "]
    )

    if (
        "```" in user_message
        or code_error_match
        or any(keyword in text for keyword in code_keywords)
        or (code_syntax_match and any(w in text for w in ["loi", "sao", "giup", "fix", "chay"]))
    ):
        err_entity = None
        for err in COMMON_CODE_ERRORS:
            if err in text:
                err_entity = err
                break

        return {
            "intent": "code_help",
            "entity_type": "skill" if err_entity else "none",
            "entity_name": err_entity,
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
    # 3. LEARNING PATH CREATION & ADVISOR
    # --------------------------------------

    learning_path_keywords = [
        "tao lo trinh",
        "tao learning path",
        "generate learning path",
        "create learning path",
        "tao lo trinh hoc",
        "goi y lo trinh",
        "tu van lo trinh",
        "de xuat lo trinh",
        "xay dung lo trinh",
        "huong dan lo trinh",
        "lo trinh cac ky nang",
        "lo trinh ky nang",
        "lo trinh hoc",
        "lo trinh tro thanh",
        "lo trinh de tro thanh",
        "lo trinh hoc tap",
        "ai lo trinh",
        "learning path",
    ]

    has_learning_path = any(
        keyword in text
        for keyword in ["lo trinh", "learning path", "roadmap"]
    )

    has_path_request_keyword = any(
        keyword in text
        for keyword in [
            "tao", "generate", "create", "goi y", "de xuat", "tu van",
            "xay dung", "huong dan", "lap", "dinh huong", "can hoc",
            "tro thanh", "bat dau", "muon hoc", "nen hoc", "nhu the nao"
        ]
    )

    has_link_request_lp = any(
        keyword in text
        for keyword in ["link", "duong dan", "url", "dia chi trang"]
    )

    if not has_link_request_lp and (
        any(keyword in text for keyword in learning_path_keywords)
        or (has_learning_path and has_path_request_keyword)
    ):
        entity = extract_learning_path_entity(user_message)

        return {
            "intent": "learning_path_request",
            "entity_type": entity["entity_type"],
            "entity_name": entity["entity_name"],
        }

    # --------------------------------------
    # 4. REVIEW & PRACTICE
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
        "luyen tap",
        "cau hoi luyen tap",
        "bai tap",
        "cau hoi on tap",
        "cho minh vai cau hoi",
        "cho minh cau hoi",
    ]

    has_course_kw = any(
        keyword in text
        for keyword in ["khoa hoc", "course", "courses"]
    )

    if any(keyword in text for keyword in review_keywords):

        if entity_type == "course" or has_course_kw:
            entity = extract_course_review_entity(user_message)

            return {
                "intent": "course_review",
                "entity_type": "course",
                "entity_name": entity["entity_name"],
            }

        entity = extract_skill_review_entity(user_message)

        return {
            "intent": "skill_review",
            "entity_type": "skill",
            "entity_name": entity.get("entity_name"),
        }

    # --------------------------------------
    # 5. SKILL SEARCH
    # --------------------------------------

    skill_search_patterns = [
        (
            r"(?:cho toi|cho minh|toi muon|liet ke|danh sach)"
            r".*(?:skill|skills|ky nang)"
            r".*(?:lien quan|ve|related)"
        ),
        (
            r"(?:tim|search|find)"
            r".*(?:skill|skills|ky nang)"
        ),
        (
            r"(?:nhung|cac)?\s*"
            r"(?:skill|skills|ky nang)"
            r".*(?:lien quan|ve)"
        ),
        (
            r"(?:skill|skills|ky nang)"
            r".*(?:nao|danh sach|liet ke)"
        ),
        (
            r"(?:skill|skills|ky nang).*(?:noi bat|duoc hoc nhieu|pho bien|hot nhat|tieu bieu|quan trong)"
        ),
        (
            r"(?:noi bat|duoc hoc nhieu|pho bien|hot nhat).*(?:skill|skills|ky nang)"
        ),
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
        # còn khóa học nào liên quan nữa không / có khóa học nào nữa không / khóa học khác
        (
            r"(?:co|con)\s+(?:khoa hoc|courses?)\s+(?:nao\s+)?(?:lien quan\s+)?(?:nua|khac)"
        ),
        (
            r"(?:khoa hoc|courses?)\s+(?:nao\s+)?(?:lien quan\s+)?(?:nua|khac)"
        ),
        (
            r"(?:co|con)\s+(?:khoa hoc|courses?)\s+nao"
        ),
        (
            r"(?:khoa hoc|courses?)\s+nao\s+(?:lien quan|khac|nua)"
        ),
        # các khóa học có kỹ năng... / khóa học chứa kỹ năng...
        (
            r"(?:khoa hoc|courses?)\s+.*(?:ky nang|skill)"
        ),
        (
            r".+\s+co\s+(?:nhung\s+|cac\s+)?"
            r"(?:khoa hoc|courses?)\s+nao"
        ),
        (
            r"(?:co\s+)?(?:nhung\s+|cac\s+)?"
            r"(?:khoa hoc|courses?)\s+(?:nao\s+)?"
            r"(?:cua|ve|cho|day|giang day|chuyen ve|co|chua|lien quan den|lien quan toi|lien quan ve)\s+.+"
        ),
        (
            r"(?:cho toi|cho minh|toi muon)\s+(?:xem\s+)?"
            r"(?:nhung\s+|cac\s+)?"
            r"(?:khoa hoc|courses?)"
        ),
        (
            r"(?:tim|search|find)\s+.*"
            r"(?:khoa hoc|courses?)"
        ),
        (
            r"(?:danh sach|liet ke)\s+.*"
            r"(?:khoa hoc|courses?)"
        ),
        (
            r"(?:khoa hoc|courses?)\s+"
            r"(?:ve|cua|cho|day|giang day|chuyen ve|co|chua|lien quan den|lien quan toi|lien quan ve)\s+.+"
        ),
        (
            r"(?:he thong|ban)\s+co\s+.*(?:khoa hoc|courses?)"
        ),
        (
            r"(?:khoa hoc|courses?).*(?:trong he thong|cho toi xem|cho minh xem)"
        ),
        # Tìm theo tổ chức / giảng viên / rating / level
        (
            r"(?:khoa hoc|courses?).*?(?:5\s*sao|danh gia cao|danh gia tot|rating cao|top rating)"
        ),
        (
            r"(?:5\s*sao|danh gia cao nhat|danh gia tot nhat).*?(?:khoa hoc|courses?)"
        ),
        (
            r"(?:khoa hoc|courses?).*?(?:giang vien|giao vien|thay|co|instructor)"
        ),
        (
            r"(?:khoa hoc|courses?).*?(?:to chuc|truong dai hoc|truong|dai hoc|vien|doi tac)"
        ),
        (
            r"(?:khoa hoc|courses?).*?(?:cap do|trinh do|level|beginner|intermediate|advanced|co ban|nang cao|trung cap)"
        ),
        (
            r"(?:tim|search|find|danh sach|liet ke|cho toi|cho minh)\s+.*?(?:khoa hoc|courses?).*?(?:beginner|co ban|nang cao|trung cap|5\s*sao)"
        ),
        (
            r"(?:khoa hoc|courses?).*?(?:duoc hoc nhieu|hoc nhieu nhat|nhieu nguoi hoc|pho bien|noi bat|hot nhat)"
        ),
        (
            r"(?:duoc hoc nhieu|hoc nhieu nhat|nhieu nguoi hoc|pho bien|noi bat|hot nhat).*?(?:khoa hoc|courses?)"
        ),
    ]

    has_tech_skill = any(
        re.search(r"\b" + re.escape(skill) + r"\b", text)
        for skill in COMMON_TECH_SKILLS
    )
    is_course_question_specific = any(
        kw in text
        for kw in [
            "thoi luong", "hoc phi", "de cuong", "bai hoc",
            "bao nhieu bai", "may bai", "chuong trinh hoc"
        ]
    )

    if (
        any(
            re.search(pattern, text, flags=re.IGNORECASE)
            for pattern in course_search_patterns
        )
        or (has_course_kw and has_tech_skill and not is_course_question_specific)
    ):
        entity = extract_course_search_entity(user_message)

        return {
            "intent": "course_search",
            "entity_type": entity.get("entity_type", "skill"),
            "entity_name": entity.get("entity_name"),
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
        "ai tutor",
        "tutor",
        "gia su ai",
        "gia su",
        "learning path",
        "lo trinh",
        "ai lo trinh",
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
        "khoa hoc",
        "course",
        "courses",
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

    explanation_patterns = [
        r"giai thich (?:ve |giup |cho )?(.+?)(?: giup| cho| kem| nhe|[?.!]|$)",
        r"khai niem (?:ve )?(.+?)(?: la gi|[?.!]|$)",
        r"(.+?)\s+la gi[?.!]*$",
        r"(.+?)\s+hoat dong (?:nhu the nao|ra sao)",
        r"cach (?:dung|su dung|viet) (.+?)(?: trong| cho|[?.!]|$)",
        r"so sanh (.+?) va (.+)",
        r"vi du (?:ve )?(.+?)(?: trong|[?.!]|$)",
    ]

    for pat in explanation_patterns:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            extracted = finalize_entity(m.group(1))
            if extracted and not is_generic_entity(extracted):
                return {
                    "intent": "skill_question",
                    "entity_type": "skill",
                    "entity_name": extracted,
                }

    if entity_type == "skill":
        matched_skill = None
        for s in sorted(COMMON_TECH_SKILLS, key=len, reverse=True):
            if re.search(r"\b" + re.escape(s) + r"\b", text):
                matched_skill = s
                break

        return {
            "intent": "skill_question",
            "entity_type": "skill",
            "entity_name": matched_skill,
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

- "Trong hệ thống có skill nào liên quan đến SQL cần học không?"
  => skill_search, skill, SQL.

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

QUY TẮC ENTITY:

1. Entity phải là tên Skill hoặc Course thực sự được nhắc đến.
2. Giữ nguyên đầy đủ tên Course, kể cả tên có nhiều từ.
3. Không lấy "của riêng mình", "của tôi",
   "cho bản thân" làm Entity.
4. Không lấy "liên quan đến" làm Entity.
5. Không lấy "được không", "nhé", "ạ" làm Entity.
6. Không lấy các từ nghi vấn như "nào", "gì", "không".
7. Không tự nghĩ ra tên Skill hoặc Course.
8. Không tự xác nhận Entity tồn tại trong database.
9. Không tự tạo ID.
10. Nếu không có tên cụ thể, entity_name là null.
11. Không nhầm tên Course với Skill.
12. Nếu không chắc chắn, chọn general_question.
13. Chỉ phân loại yêu cầu trong câu được cung cấp.
14. Không tự thêm yêu cầu khác.

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

    entity_name = finalize_entity(entity_name)

    if not entity_name:
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

    normalized_input = normalize_text(user_message)
    is_continuation_query = any(
        m in normalized_input
        for m in [
            "con nua khong", "con khac khong", "nua khong", "khac khong",
            "con gi nua", "co cai nao nua", "co cai nao khac",
            "con khoa hoc nao", "khoa hoc nao nua", "khoa hoc nao khac",
            "con ky nang nao", "ky nang nao nua", "ky nang nao khac",
            "cho them", "vi du khac", "cau hoi khac", "bai khac"
        ]
    )

    if (
        intent in ENTITY_REQUIRED_INTENTS
        and entity_name is None
        and not is_continuation_query
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

    # Chuẩn hóa alias, không xóa nội dung Entity.
    entity_name = finalize_entity(entity_name)

    # --------------------------------------
    # STEP 3. ENFORCE ENTITY TYPE
    # --------------------------------------

    if intent in {
        "skill_question",
        "skill_review",
    }:
        entity_type = "skill"

    elif intent == "skill_search":
        if entity_type != "popular":
            entity_type = "skill"

    elif intent == "course_search":
        if entity_type not in {"organization", "instructor", "rating", "level", "popular"}:
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
    """

    text = normalize_text(user_message)

    connectors = [
        " ngoai ra ",
        " ben canh do ",
        " dong thoi ",
        " them nua ",
        " them cho toi ",
        " sau do ",
        " tiep theo ",
        " khong nhung ",
        " ma con ",
        " cung nhu ",
        ";",
        "\n",
    ]

    has_multiple_questions = user_message.count("?") > 1

    return any(connector in text for connector in connectors) or has_multiple_questions


# ==========================================
# 18. GEMINI MULTI-QUERY DECOMPOSITION
# ==========================================

def decompose_query_by_llm(user_message: str) -> list:
    """
    Dùng Gemini tách một tin nhắn thành các yêu cầu độc lập.

    Hàm này chỉ tách yêu cầu, không phân loại intent.
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

    # Các service cũ vẫn có thể đọc:
    # route["intent"]
    # route["entity_name"]
    # route["retrieval_modes"]
    #
    # Các trường ở cấp ngoài đại diện cho yêu cầu đầu tiên.

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
        "is_compound": len(sub_queries) > 1,
        "sub_queries": sub_queries,
    }
