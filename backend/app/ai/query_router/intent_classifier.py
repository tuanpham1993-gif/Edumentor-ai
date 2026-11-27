"""
Intent classifier module for Query Router.
Classifies user query intent using rules or LLM fallback.
"""

import re

from app.ai.client import generate_text
from app.ai.query_router.config import (
    ALLOWED_ENTITY_TYPES,
    ALLOWED_INTENTS,
    COMMON_CODE_ERRORS,
    COMMON_TECH_SKILLS,
)
from app.ai.query_router.entity_extractor import (
    detect_entity_type,
    extract_course_enrollment_entity,
    extract_course_recommendation_entity,
    extract_course_review_entity,
    extract_course_search_entity,
    extract_course_web_search_entity,
    extract_learning_path_entity,
    extract_skill_review_entity,
    extract_skill_search_entity,
)
from app.ai.query_router.normalizer import (
    extract_json_object,
    finalize_entity,
    is_generic_entity,
    normalize_entity_name,
    normalize_text,
)


def classify_by_rules(user_message: str) -> dict | None:
    """Phân loại Intent bằng luật. Không gọi Gemini."""
    text = normalize_text(user_message)
    entity_type = detect_entity_type(user_message)

    # --------------------------------------
    # 1. CODE HELP / CODE ANALYSIS / CODE FIX
    # --------------------------------------
    code_fix_keywords = [
        "sua loi",
        "fix loi",
        "fix bug",
        "debug",
        "sua giup",
        "fix this code",
        "fix this error",
        "fix error",
        "fix python error",
        "fix my code",
        "fix code",
        "help me fix",
        "help fix",
        "solve this error",
        "resolve error",
        "chay bi loi",
        "chay khong duoc",
        "bao loi",
        "loi nay la sao",
    ]
    code_analysis_keywords = [
        "giai thich code",
        "phan tich code",
        "toi uu code",
        "explain this code",
        "with an example",
        "with code example",
        "kem vi du code",
        "cho vi du code",
        "explain with example",
        "explain with an example",
        "doan code",
        "doan ma",
        "code nay lam gi",
        "doan code sau",
    ]
    code_general_keywords = [
        "traceback",
        "exception",
        "loi code",
        "error trong code",
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
        or any(k in text for k in code_fix_keywords)
        or any(k in text for k in code_analysis_keywords)
        or any(k in text for k in code_general_keywords)
        or (code_syntax_match and any(w in text for w in ["loi", "sao", "giup", "fix", "chay"]))
    ):
        err_entity = None
        for err in COMMON_CODE_ERRORS:
            if err in text:
                err_entity = err
                break

        # Distinguish code_fix vs code_analysis
        if any(k in text for k in code_fix_keywords) or code_error_match:
            intent = "code_fix"
        elif any(k in text for k in code_analysis_keywords):
            intent = "code_analysis"
        else:
            intent = "code_help"

        return {
            "intent": intent,
            "entity_type": "skill" if err_entity else "none",
            "entity_name": err_entity,
        }

    # --------------------------------------
    # 2. COURSE ENROLLMENT LINK
    # --------------------------------------
    has_link_keyword = any(k in text for k in ["link", "duong dan", "url"])
    has_course_keyword = any(k in text for k in ["khoa hoc", "course", "courses"])

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
    has_learning_path = any(k in text for k in ["lo trinh", "learning path", "roadmap"])
    has_path_request_keyword = any(
        k in text
        for k in [
            "tao",
            "generate",
            "create",
            "goi y",
            "de xuat",
            "tu van",
            "xay dung",
            "huong dan",
            "lap",
            "dinh huong",
            "can hoc",
            "tro thanh",
            "bat dau",
            "muon hoc",
            "nen hoc",
            "nhu the nao",
        ]
    )
    has_link_request_lp = any(k in text for k in ["link", "duong dan", "url", "dia chi trang"])

    if not has_link_request_lp and (
        any(k in text for k in learning_path_keywords) or (has_learning_path and has_path_request_keyword)
    ):
        entity = extract_learning_path_entity(user_message)
        return {
            "intent": "learning_path_request",
            "entity_type": entity["entity_type"],
            "entity_name": entity["entity_name"],
        }

    # --------------------------------------
    # 4. REVIEW & PRACTICE / REINFORCEMENT
    # --------------------------------------
    has_link_request_review = any(k in text for k in ["link", "duong dan", "url", "dia chi trang", "trang web", "web on tap"])
    reinforcement_keywords = [
        "cau hoi on tap",
        "cau hoi luyen tap",
        "cho minh vai cau hoi",
        "cho minh cau hoi",
        "tao cau hoi",
        "kiem tra kien thuc",
        "quiz kien thuc",
        "kiem tra giup",
        "do kien thuc",
        "cau hoi trac nghiem",
        "luyen tap trac nghiem",
        "practice questions",
        "practice question",
        "practice quiz",
        "practice exercises",
        "practice exercise",
        "create practice questions",
        "give me questions",
        "give me exercises",
        "quiz questions",
        "quiz question",
        "exercises about",
        "exercises on",
        "exercises",
        "exercise",
    ]
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
        "bai tap",
    ]
    has_course_kw = any(k in text for k in ["khoa hoc", "course", "courses"])

    # Nếu người dùng hỏi xin LINK / đường dẫn ôn tập, điều hướng sang system_operation để xử lý link an toàn, không gen quiz
    if not has_link_request_review:
        if any(k in text for k in reinforcement_keywords):
            entity = extract_skill_review_entity(user_message)
            return {
                "intent": "reinforcement_request",
                "entity_type": "skill",
                "entity_name": entity.get("entity_name"),
            }

    # --------------------------------------
    # 4.3 COURSE WEB SEARCH (SYLLABUS / MODULES / LESSONS)
    # --------------------------------------
    MODULE_KW = r"(?:modules?|moudules?|moudles?|moduls?)"
    web_curriculum_patterns = [
        r"(?:chi\s+tiet|thong\s+tin\s+chi\s+tiet|noi\s+dung\s+chi\s+tiet)\s+(?:ve\s+)?(?:khoa\s*hoc|khoa|course|courses)\b",
        r"(?:khoa\s*hoc|khoa|course|courses)\s+(?:so|thu)?\s*[0-9]+\b",
        r"(?:giao trinh|syllabus|curriculum|de cuong chi tiet|de cuong|cac " + MODULE_KW + r"|nhung " + MODULE_KW + r"|co nhung " + MODULE_KW + r" nao|" + MODULE_KW + r" nao|cac tuan hoc|nhung tuan hoc|tuan hoc|lo trinh bai hoc|cac bai hoc|danh sach bai hoc|bai giang|noi dung chi tiet cac tuan|noi dung cac tuan).*(?:khoa\s*hoc|khoa|course|courses)",
        r"(?:khoa\s*hoc|khoa|course|courses).*(?:giao trinh|syllabus|curriculum|de cuong|cac " + MODULE_KW + r"|nhung " + MODULE_KW + r"|co nhung " + MODULE_KW + r" nao|" + MODULE_KW + r" nao|cac tuan hoc|nhung tuan hoc|tuan hoc|lo trinh bai hoc|cac bai hoc|danh sach bai hoc|bai giang|noi dung chi tiet cac tuan|noi dung cac tuan)",
        r"(?:khoa\s*hoc|khoa|course|courses)\s*.+?\s*(?:co\s+)?(?:nhung\s+)?" + MODULE_KW + r"\s+nao",
        r"(?:khoa\s*hoc|khoa|course|courses)\s*.+?\s*(?:co\s+)?(?:nhung\s+)?tuan\s+hoc\s+nao",
        r"(?:khoa|khoa\s*hoc)\s*.+?\s*gom\s+(?:nhung\s+)?tuan\s+hoc\s+nao",
        r"noi dung chi tiet cac tuan",
        r"(?:co\s+)?(?:may|bao nhieu|nhung|cac)\s+" + MODULE_KW + r".*?(?:trong|cua)?\s*(?:khoa\s*hoc|khoa|course|courses)?\b",
        r"(?:may|bao nhieu)\s+(?:" + MODULE_KW + r"|bai|chu de|tuan).*?(?:trong|cua)?\s*(?:khoa\s*hoc|khoa|course|courses)?\b",
        r"(?:" + MODULE_KW + r")\s+(?:co\s+)?(?:trong|cua)\s+(?:khoa\s*hoc|khoa|course|courses)?\b",
        r"(?:khoa\s*hoc|khoa|course|courses).*?(?:co\s+)?(?:may|bao nhieu)\s+" + MODULE_KW + r"\b",
        r"(?:co\s+)?(?:may|bao nhieu)\s+" + MODULE_KW + r"\b",
        r"(?:co\s+)?(?:may|bao nhieu)\s+(?:tuan|chuong|phan)\s+(?:trong\s+)?(?:khoa\s*hoc|khoa|course|courses)\b",
        r"(?:" + MODULE_KW + r")\s+(?:co\s+trong|trong|cua)\b",
        r"(?:cac|nhung|danh sach)?\s*(?:" + MODULE_KW + r")\s+(?:co\s+trong|trong|cua)\b",
        r"(?:cac|nhung|danh sach)\s+(?:" + MODULE_KW + r")\b",
    ]
    if any(re.search(p, text, flags=re.IGNORECASE) for p in web_curriculum_patterns):
        c_web_ent = extract_course_web_search_entity(user_message)
        return {
            "intent": "course_web_search",
            "entity_type": "course",
            "entity_name": c_web_ent.get("entity_name"),
            "organization": c_web_ent.get("organization"),
        }

    # --------------------------------------
    # 4.4 COURSE RECOMMENDATION
    # --------------------------------------
    recommendation_patterns = [
        r"(?:goi y|de xuat|tu van)\s+(?:cho toi\s+|cho minh\s+)?(?:khoa hoc|khoa|course|courses)\b",
        r"(?:nen\s+)?(?:hoc|bat dau|chon)(?:\s+voi|\s+bang)?\s+(?:nhung\s+)?(?:khoa hoc|khoa|course|courses)\s+(?:nao|gi)\b",
        r"(?:khoa hoc|khoa|course|courses)\s+nao\s+phu hop\b",
        r"(?:moi hoc|chua biet gi|chua biet bat dau|nguoi moi|bat dau hoc|nhap mon).*?(?:nen\s+)?(?:hoc|chon|bat dau)(?:\s+voi|\s+bang)?\s+(?:nhung\s+)?(?:khoa|khoa hoc|course|courses)\b",
        r"(?:muon tro thanh|dinh huong lam|muon lam)\s+.+?(?:nen\s+)?(?:hoc|chon)\s+(?:nhung\s+)?(?:khoa|khoa hoc|course|courses)\b",
        r"(?:da biet|da hoc|biet ve)\s+.+?(?:nen\s+hoc\s+(?:nhung\s+)?khoa\s+nao\s+tiep\s+theo|nen\s+hoc\s+gi\s+tiep\s+theo|hoc\s+khoa\s+nao\s+tiep\b)",
        r"(?:tim|kiem)\s+(?:khoa hoc|khoa)\s+phu hop\s+voi\b",
        r"(?:phu hop voi)\s+(?:trinh do|ky nang|kha nang)\s+(?:cua toi|cua minh|hien tai)\b",
        r"(?:chua biet bat dau tu dau|chua biet hoc tu dau)\b",
    ]
    if any(re.search(p, text, flags=re.IGNORECASE) for p in recommendation_patterns):
        c_rec_ent = extract_course_recommendation_entity(user_message)
        return {
            "intent": "course_recommendation",
            "entity_type": "course",
            "entity_name": c_rec_ent.get("entity_name"),
            "level": c_rec_ent.get("level"),
            "target_role": c_rec_ent.get("target_role"),
            "known_skill": c_rec_ent.get("known_skill"),
        }

    if not has_link_request_review and any(k in text for k in review_keywords):
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
    # 4.5 SKILLS ASSOCIATED WITH A COURSE
    # --------------------------------------
    course_skill_patterns = [
        r"(?:skill|skills|ky nang).*?(?:trong|cua)\s+(?:he thong\s+)?(?:khoa hoc|khoa|course|courses)\b",
        r"(?:skill|skills|ky nang).*?lien quan(?:\s+den|\s+toi|\s+ve)?\s+(?:khoa hoc|khoa|course|courses)\b",
        r"(?:khoa hoc|khoa|course|courses).*?(?:day|co|hoc|chua|gom|tap trung|lien quan).*?(?:skill|skills|ky nang)\b",
        r"(?:trong|cua)\s+(?:khoa hoc|khoa|course|courses).*?(?:co\s+)?(?:skill|skills|ky nang)\b",
    ]
    if any(re.search(p, text, flags=re.IGNORECASE) for p in course_skill_patterns):
        entity = extract_course_review_entity(user_message)
        return {
            "intent": "course_question",
            "entity_type": "course",
            "entity_name": entity["entity_name"],
        }

    # --------------------------------------
    # 4.6 DIRECT COURSE QUESTION (HỎI VỀ MỘT KHÓA HỌC CỤ THỂ)
    # --------------------------------------
    course_question_patterns = [
        r"(?:cho toi hoi|hoi|tim hieu|xem|chi tiet|thong tin|noi dung|gioi thieu)\s+(?:ve\s+)?(?:khoa hoc|khoa|course|courses)\s+(.+)",
        r"(?:ban\s+)?(?:co\s+)?(?:khoa hoc|khoa|course|courses)\s+(?:nay\s+)?(?:trong he thong\s+)?(?:khong|ha|nhi)?\s+(.+)",
        r"(?:co|tim|tim thay)?\s*(?:khoa hoc|khoa|course|courses)\s+(?:nay|do)\s+(?:trong he thong\s+)?(?:khong|ha|nhi|la gi|noi ve gi|co gi|gom nhung gi)[?.!\s]*$",
        r"(?:khoa hoc|khoa|course|courses)\s+(?:nay|do)\s+(?:la gi|noi ve gi|co gi|gom nhung gi)[?.!\s]*$",
    ]
    for cqp in course_question_patterns:
        m_cq = re.search(cqp, text, flags=re.IGNORECASE)
        if m_cq:
            # Nếu pattern bắt được group(1) có nội dung cụ thể, lấy trực tiếp
            matched_group = m_cq.group(1).strip() if m_cq.lastindex and m_cq.group(1) else ""
            matched_group = re.sub(r"^(?:nay\s+|do\s+|trong he thong\s+|khong\s+)+", "", matched_group, flags=re.IGNORECASE).strip()
            if matched_group and not is_generic_entity(matched_group):
                return {
                    "intent": "course_question",
                    "entity_type": "course",
                    "entity_name": finalize_entity(matched_group),
                }
            entity = extract_course_review_entity(user_message)
            return {
                "intent": "course_question",
                "entity_type": "course",
                "entity_name": entity.get("entity_name"),
            }

    # --------------------------------------
    # 5. SKILL SEARCH
    # --------------------------------------
    skill_search_patterns = [
        r"(?:cho toi|cho minh|toi muon|liet ke|danh sach).*(?:skill|skills|ky nang).*(?:lien quan|ve|related)",
        r"(?:tim|search|find).*(?:skill|skills|ky nang)",
        r"(?:nhung|cac)?\s*(?:skill|skills|ky nang).*(?:lien quan|ve)",
        r"(?:skill|skills|ky nang).*(?:nao|danh sach|liet ke)",
        r"(?:skill|skills|ky nang).*(?:noi bat|duoc hoc nhieu|pho bien|hot nhat|tieu bieu|quan trong)",
        r"(?:noi bat|duoc hoc nhieu|pho bien|hot nhat).*(?:skill|skills|ky nang)",
    ]
    if any(re.search(p, text, flags=re.IGNORECASE) for p in skill_search_patterns):
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
        r"(?:co|con)\s+(?:khoa hoc|courses?)\s+(?:nao\s+)?(?:lien quan\s+)?(?:nua|khac)",
        r"(?:khoa hoc|courses?)\s+(?:nao\s+)?(?:lien quan\s+)?(?:nua|khac)",
        r"(?:co|con)\s+(?:khoa hoc|courses?)\s+nao",
        r"(?:khoa hoc|courses?)\s+nao\s+(?:lien quan|khac|nua)",
        r"(?:khoa hoc|courses?)\s+.*(?:ky nang|skill)",
        r".+\s+co\s+(?:nhung\s+|cac\s+)?(?:khoa hoc|courses?)\s+nao",
        r"(?:(?:edumentor|he thong|ban|web|o day|hien tai)\s+)?(?:co\s+)?(?:nhung\s+|cac\s+)?(?:khoa hoc|courses?)\s+(?:nao\s+)?(?:cua|ve|cho|day|giang day|chuyen ve|co|chua|lien quan den|lien quan toi|lien quan ve)\s+.+",
        r"(?:cho toi|cho minh|toi muon)\s+(?:xem\s+)?(?:nhung\s+|cac\s+)?(?:khoa hoc|courses?)",
        r"(?:tim|search|find)\s+.*(?:khoa hoc|courses?)",
        r"(?:danh sach|liet ke)\s+.*(?:khoa hoc|courses?)",
        r"(?:khoa hoc|courses?)\s+(?:ve|cua|cho|day|giang day|chuyen ve|co|chua|lien quan den|lien quan toi|lien quan ve)\s+.+",
        r"(?:edumentor|he thong|ban)\s+co\s+.*(?:khoa hoc|courses?)",
        r"(?:khoa hoc|courses?).*(?:trong he thong|cho toi xem|cho minh xem)",
        r"(?:khoa hoc|courses?).*?(?:5\s*sao|danh gia cao|danh gia tot|rating cao|top rating)",
        r"(?:5\s*sao|danh gia cao nhat|danh gia tot nhat).*?(?:khoa hoc|courses?)",
        r"(?:khoa hoc|courses?).*?(?:giang vien|giao vien|thay|co|instructor)",
        r"(?:khoa hoc|courses?).*?(?:to chuc|truong dai hoc|truong|dai hoc|vien|doi tac)",
        r"(?:khoa hoc|courses?).*?(?:cap do|trinh do|level|beginner|intermediate|advanced|co ban|nang cao|trung cap)",
        r"(?:tim|search|find|danh sach|liet ke|cho toi|cho minh)\s+.*?(?:khoa hoc|courses?).*?(?:beginner|co ban|nang cao|trung cap|5\s*sao)",
        r"(?:khoa hoc|courses?).*?(?:duoc hoc nhieu|hoc nhieu nhat|nhieu nguoi hoc|pho bien|noi bat|hot nhat|tot nhat|hay nhat)",
        r"(?:duoc hoc nhieu|hoc nhieu nhat|nhieu nguoi hoc|pho bien|noi bat|hot nhat|tot nhat|hay nhat).*?(?:khoa hoc|courses?)",
        r".*?(?:co cai nao|co khoa nao|co lop nao).*?(?:to chuc|giang day|day|cung cap)",
        r".*?(?:do|boi|tu)\s+(?:to chuc|truong|dai hoc|doi tac|cong ty).*",
    ]
    has_tech_skill = any(re.search(r"\b" + re.escape(s) + r"\b", text) for s in COMMON_TECH_SKILLS)
    is_course_question_specific = any(
        kw in text
        for kw in ["thoi luong", "hoc phi", "de cuong", "bai hoc", "bao nhieu bai", "may bai", "chuong trinh hoc"]
    )

    if any(re.search(p, text, flags=re.IGNORECASE) for p in course_search_patterns) or (
        has_course_kw and has_tech_skill and not is_course_question_specific
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
    has_operation_request = any(k in text for k in operation_keywords)
    has_link_request = any(k in text for k in link_keywords)
    has_system_feature = any(k in text for k in system_features)
    auth_keywords = ["dang nhap", "dang ky", "login", "register"]

    if ((has_operation_request or has_link_request) and has_system_feature) or any(k in text for k in auth_keywords):
        return {
            "intent": "system_operation",
            "entity_type": "none",
            "entity_name": None,
        }

    # --------------------------------------
    # 8. COURSE QUESTION
    # --------------------------------------
    course_question_patterns = [
        r"(?:cho toi hoi|hoi|tim hieu|xem|chi tiet|thong tin|noi dung|gioi thieu)\s+(?:ve\s+)?(?:khoa hoc|khoa|course|courses)\s+(.+)",
        r"(?:co|tim|tim thay)?\s*(?:khoa hoc|khoa|course|courses)\s+(?:nay|do)\s+(?:trong he thong\s+)?(?:khong|ha|nhi|la gi|noi ve gi|co gi|gom nhung gi)",
        r"(?:ban\s+)?(?:co\s+)?(?:khoa hoc|khoa|course|courses)\s+(?:nay\s+)?(?:trong he thong\s+)?(?:khong|ha|nhi)?\s+(.+)",
        r"(?:khoa hoc|khoa|course|courses)\s+(?:nay|do)\s+(?:la gi|noi ve gi|co gi|gom nhung gi)",
    ]
    for cqp in course_question_patterns:
        m_cq = re.search(cqp, text, flags=re.IGNORECASE)
        if m_cq:
            entity = extract_course_review_entity(user_message)
            return {
                "intent": "course_question",
                "entity_type": "course",
                "entity_name": entity.get("entity_name"),
            }

    if entity_type == "course":
        entity = extract_course_review_entity(user_message)
        return {
            "intent": "course_question",
            "entity_type": "course",
            "entity_name": entity.get("entity_name"),
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


def build_classifier_prompt(user_message: str) -> str:
    return f"""
Bạn là Query Classifier của hệ thống EduMentor AI.

Nhiệm vụ:
Phân loại ý định người dùng và xác định Entity.

INTENT HỢP LỆ:
1. skill_question: Hỏi kiến thức về một Skill.
2. skill_review: Muốn ôn tập hoặc kiểm tra một Skill.
3. skill_search: Tìm danh sách Skill theo chủ đề.
4. course_question: Hỏi thông tin về một Course cụ thể.
5. course_review: Muốn ôn tập một Course.
6. course_search: Tìm các Course theo chủ đề hoặc tên Skill.
7. course_enrollment_link: Muốn lấy link tham gia hoặc đăng ký Course.
8. system_operation: Hỏi cách sử dụng hoặc thao tác trên EduMentor.
9. code_help: Giải thích, sửa lỗi hoặc tối ưu code.
10. code_analysis: Phân tích code, giải thích luồng hoạt động của code.
11. code_fix: Sửa lỗi code cụ thể.
12. reinforcement_request: Yêu cầu bài tập, câu hỏi ôn tập, câu hỏi trắc nghiệm.
13. learning_path_request: Muốn tạo lộ trình học bằng AI.
14. general_question: Câu hỏi kiến thức chung hoặc trường hợp khác.

ENTITY TYPE:
- skill
- course
- none

CHỈ TRẢ VỀ JSON HỢP LỆ:
{{
    "intent": "skill_search",
    "entity_type": "skill",
    "entity_name": "SQL"
}}

Câu hỏi:
{user_message}
"""


def classify_by_llm(user_message: str, custom_api_key: str | None = None) -> dict:
    prompt = build_classifier_prompt(user_message)
    ai_text = generate_text(prompt, api_key=custom_api_key)
    result = extract_json_object(ai_text)

    intent = result.get("intent")
    entity_type = result.get("entity_type")
    entity_name = result.get("entity_name")

    if intent not in ALLOWED_INTENTS:
        raise ValueError(f"Intent {intent} không hợp lệ.")

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
