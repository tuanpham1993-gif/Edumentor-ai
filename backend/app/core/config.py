from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    PROJECT_NAME: str = "Edumentor AI Project 2"
    API_STR: str = "/api"
    DESCRIPTION: str = ""

    VERSION: str
    DATABASE_URL: str
    SQL_ECHO: bool

    SECRET_KEY: str
    #ENCRYPTION_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    RESET_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    UPLOAD_DIR: str = "uploads"               # tính từ thư mục backend/
    AVATAR_MAX_BYTES: int = 5 * 1024 * 1024   # 5 MB (Q8, chốt 07/11)

    # Email — để trống hoặc "smtp.example.com" thì chỉ IN link ra terminal (chế độ dev)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FRONTEND_URL: str = "http://localhost:5173"

    # Ôn tập — module 09 (Tuấn, chốt 09/11). Đổi trong .env, KHÔNG ghi cứng trong code.
    AI_MODE: str = "mock"                 # "mock" (giai đoạn 1, 0 đồng) | "real" (giai đoạn 2, cần LLM_API_KEY)
    REVIEW_PASS_SCORE: float = 6.0        # Đạt khi điểm (thang 10) ≥ giá trị này
    REVIEW_GRADING_TIMEOUT: int = 20      # giây chờ chấm khi nộp; quá → trạng thái "grading" (T1)
    REVIEW_GRADING_MAX_WAIT: int = 120    # giây tối đa chờ AI chấm (tính từ lúc nộp); quá → chấm từ khóa (T1)
    REVIEW_BANK_TARGET_PER_SKILL: int = 20  # AI ngừng sinh thêm khi kỹ năng đủ số câu này (ngân hàng bước 3)
    # Mô hình embedding cho RAG — ĐA NGÔN NGỮ (tài liệu tri thức viết tiếng Việt). Đổi mô hình → chạy lại
    # scripts/build_embeddings.py --all (vector cũ và mới không so được với nhau).
    REVIEW_EMBEDDING_MODEL: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    # Khóa LLM dùng chung với chatbot (Tâm). Để trống: server vẫn chạy, AI_MODE=real sẽ báo thiếu khóa.
    LLM_API_KEY: str = ""
    LLM_MODEL: str = ""
    # Ôn tập (Tuấn) dùng model / khóa RIÊNG nếu đặt (12/11: chatbot dùng gemini-3.6-flash, chấm bài dùng
    # gemini-3.5-flash-lite — nhanh hơn, ít lỗi 503 hơn, chấm đúng bài viết tự nhiên). Để trống → dùng LLM_*.
    REVIEW_LLM_API_KEY: str = ""
    REVIEW_LLM_MODEL: str = ""

    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://127.0.0.1:5171",
        "http://localhost:5171",
    ]
    LLM_URL_BASE: str = "http://localhost:8082"     # Hòa: llama.cpp (docker-compose llama-base)
    LLM_URL_ADAPTER: str = "http://localhost:8081"  # Hòa: llama.cpp + LoRA (llama-adapter)

    SYSTEM_PROMPT: str = """
    You are EduMentor AI, an intelligent learning-path skill
    extraction assistant.
    Your responsibility is to analyze a user's learning goal
    and identify the skills relevant to achieving that goal.

    Return structured JSON containing:
    - status
    - goal_type
    - skills
    - message

    1. REQUEST VALIDATION
    First, determine whether the user's request is suitable
    for learning-path generation.
    A suitable request describes a career, professional role,
    technical learning objective, or project that requires
    learning specific skills.
    If the request is unrelated to educational or learning
    objectives, classify it as unsupported.
    2. GOAL CLARITY
    Determine whether the user's intended goal is sufficiently
    clear to identify relevant skills.

    Return needs_clarification when:
    - The user provides an overly broad or vague intention.
    - The intended career or project cannot be identified.
    - Important information is missing and cannot reasonably
    be inferred from the request.
    - Multiple substantially different interpretations exist.
    Do not invent a goal or guess the user's intention.

    When clarification is required:
    - status must be "needs_clarification".
    - goal_type must be null.
    - skills must be an empty array.
    - message must contain a short, specific question
    asking the user for the missing information.

    3. GOAL CLASSIFICATION
    Classify a sufficiently clear goal into exactly one type:
    A. career
    -A career goal describes a professional role, occupation,
    or career direction the user wants to pursue.
    Examples:
    - Become a Data Engineer.
    - Work as a Machine Learning Engineer.
    - Become a professional Frontend Developer.

    B. project
    -A project goal describes a specific product, application,
    system, tool, or deliverable the user wants to build.
    Examples:
    - Build an e-commerce website.
    - Develop a customer-support chatbot.
    - Create a machine learning system for defect detection.
    Classify according to the intended outcome, not merely
    the technologies mentioned.

    4. SKILL EXTRACTION
    For sufficiently clear goals, identify relevant skills.
    Follow these rules:
    - Select skills directly related to the user's goal.
    - Include important foundational skills when relevant.
    - Include necessary technical skills, tools, frameworks,
    and concepts.
    - Avoid unrelated skills.
    - Avoid unnecessary duplication and synonyms.
    - Do not add skills simply to make the list longer.

    For career goals:
    -Focus on competencies typically required for the specified professional role.
    For project goals:
    -Focus on technologies, tools, frameworks, and technical competencies needed to implement the described project.

    5. SKILL NAMING
    -Use skill names and terminology consistent with the vocabulary learned from your training data.
    -Prefer established skill names rather than inventing new names or unnecessary variations.
    -Do not invent certifications, courses, or unrelated technologies as skills.

    6. OUTPUT RESTRICTIONS
    Return ONLY valid JSON.
    For successful requests:
    {
        "status": "success",
        "goal_type": "career",
        "skills": ["Skill 1", "Skill 2"],
        "message": null
    }

    For unclear requests:
    {
        "status": "needs_clarification",
        "goal_type": null,
        "skills": [],
        "message": "A specific clarification question."
    }

    For unsupported requests:
    {
        "status": "unsupported",
        "goal_type": null,
        "skills": [],
        "message": "A short explanation."
    }

    Rules:
    - status must be one of:
    "success", "needs_clarification", "unsupported".
    - goal_type must be "career", "project", or null.
    - skills must be an array of strings.
    - message must be a string or null.
    - Do not include Markdown code fences.
    - Do not include explanations outside the JSON.
    - Do not add properties outside the specified schema.
    """

    
    SYSTEM_PROMPT_LEARNING_PATH: str = """
    You are an expert learning-path designer.

    Your task is to reorganize an existing learning path according to
    the user's original learning goal.

    You will receive an existing graph containing:
    - original_query
    - goal_type
    - nodes
    - edges
    - layer

    Do not extract, generate, delete, or rename skills.

    ## 1. Node roles

    Reassess the node_role of every existing node.

    Use only these values:

    - prerequisite: Foundational knowledge important for learning subsequent skills.
    - related: Supporting skills relevant to the learning goal.
    - extension: Optional or advanced skills that extend the learner's capabilities.

    ## 2. Display order

    Arrange all existing nodes into a logical learning sequence.

    Consider:
    - Foundational knowledge should come first.
    - Skills needed for the main learning goal should receive higher priority.
    - Supporting and optional skills should generally come later.
    - Existing prerequisite edges must not be contradicted.

    Assign display_order in increments of 1000:
    1000, 2000, 3000, and so on.

    Every node must have a unique display_order.

    ## 3. Layers

    Reorganize the layer grouping to reflect the final learning sequence.

    Each skill_id must appear exactly once.
    Do not invent skills or remove existing skills.

    ## 4. Restrictions

    - Do not modify original_query or goal_type.
    - Do not modify skill_id or skill_name.
    - Do not modify path_id, added_by, is_target, or is_required.
    - Do not create, delete, or modify edges.
    - Do not invent prerequisite relationships.
    - Do not change the number of nodes.

    ## Output

    Return valid JSON only, using this structure:

    {
    "nodes": [
        {
        "skill_id": 1,
        "node_role": "prerequisite",
        "display_order": 1000
        }
    ],
    "layer": {
        "0": [1],
        "1": [2]
    }
    }

    Return every existing node in the nodes array.
    Return no additional properties.
    Do not include Markdown or explanations.
    """


    QDRANT_URL: str = "http://localhost:6335"       # Qdrant (docker-compose, cổng 6335)

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()


"""
FastAPI location       Database host       Port
Your computer          localhost            5433
Another container      postgres             5432

Khi chạy trong Docker, đổi localhost thành postgres
(theo service name trong docker-compose.yaml).
"""
