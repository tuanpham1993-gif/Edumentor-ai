"""Phân loại kỹ năng theo DANH MỤC bằng từ khóa trong tên (module 01 · Tuấn · FĐ6, 08/11/2026).

Vì sao cần: bảng `skills` (của Hòa) KHÔNG có cột danh mục, bảng `courses` cũng không có chủ đề.
Thầy gợi ý trang "Khám phá kỹ năng" duyệt theo danh mục → tạm phân loại bằng quy tắc từ khóa.

Cách hoạt động: duyệt CATEGORIES theo thứ tự, kỹ năng thuộc danh mục ĐẦU TIÊN có từ khóa khớp
(thứ tự quan trọng: "Web Application Security" → An ninh mạng chứ không phải Web).
Không khớp gì → "other" (Khác). Đo trên 5.893 kỹ năng thật: ~70% vào danh mục cụ thể.

Hạn chế (đã báo Tuấn): là ƯỚC LƯỢNG theo tên, có thể xếp nhầm vài kỹ năng. Lâu dài nên đề xuất
nhóm thêm cột `category` vào bảng `skills` (Hòa) và dùng file này làm dữ liệu ban đầu.
"""

import re
from functools import lru_cache

# (key, nhãn tiếng Việt, mẫu từ khóa) — thứ tự = thứ tự ưu tiên khi khớp
CATEGORIES = [
    (
        "security",
        "An ninh mạng",
        r"secur|cyber|penetrat|ethical hack|cryptograph|malware|forensic|vulnerab|firewall|\bsiem\b|threat|encrypt|identity|authenticat|privacy|owasp|phishing|incident",
    ),
    (
        "ai",
        "AI & Machine Learning",
        r"machine learning|deep learning|neural|\bai\b|artificial intelligence|\bnlp\b|natural language|computer vision|\bllms?\b|large language|generative|\bgpt|prompt|tensorflow|pytorch|keras|scikit|reinforcement|chatbot|transformer|hugging ?face|langchain|\bml\b|classification|regression|clustering|mlops|opencv|image (?:classif|recog|segment)|speech recog|\bmcmc\b|bayesian",
    ),
    (
        "database",
        "Cơ sở dữ liệu",
        r"database|\bsql\b|\bsql |mysql|postgres|mongo|nosql|oracle|dbms|sqlite|redis|dynamodb|\bquer(?:y|ies)\b|relational|\borm\b",
    ),
    (
        "data",
        "Dữ liệu & Phân tích",
        r"\bdata\b|analytic|analysis|analyz|statistic|excel|tableau|power ?bi|visuali[sz]|dashboard|pandas|numpy|seaborn|matplotlib|business intelligence|\betl\b|extract.{0,20}transform|warehous|big data|spark|hadoop|kafka|snowflake|bigquery|databricks|looker|spreadsheet|forecast|probabilit|\br programming|\br\b|mean and deviation",
    ),
    (
        "cloud",
        "Cloud & DevOps",
        r"cloud|\baws\b|amazon|azure|google cloud|\bgcp\b|devops|docker|kubernetes|ci/cd|terraform|ansible|jenkins|linux|serverless|microservice|infrastructure|deploy|\bshell|bash|containe|site reliab|unix|ubuntu|vmware|virtuali|monitoring|logging|persistent volume|distributed",
    ),
    (
        "web",
        "Web & Mobile",
        r"\bweb|html|css|react|angular|\bvue|node|express|django|flask|spring|front-?end|back-?end|full-?stack|\bapis?\b|\brest\b|restful|mobile|android|\bios\b|swift|kotlin|flutter|jquery|bootstrap|laravel|wordpress|\bphp\b|javascript|typescript|graphql|asp\.?net|\.net\b|ruby on rails|app development|website|dependency injection",
    ),
    (
        "design",
        "Thiết kế & Đa phương tiện",
        r"(?<!system )(?<!database )design(?! pattern)|\bux\b|\bui\b|user experience|user interface|figma|adobe|photoshop|illustrator|graphic|\b3d\b|animation|video|prototyp|wireframe|blender|unity|unreal|\bgame|drawing|\bart\b|photograph|typograph|tinkercad",
    ),
    (
        "programming",
        "Lập trình & Phần mềm",
        r"python|\bjava\b|c\+\+|c#|\bc programming|programming|coding|algorithm|data structure|\boop\b|object.oriented|software|debug|\brust\b|golang|\bruby\b|\bscala\b|matlab|compiler|\bgit\b|github|version control|testing|\btest|selenium|\bcode\b|developer|scripting|functional|design pattern|numeric operator|computational thinking",
    ),
    (
        "network",
        "Mạng & Phần cứng",
        r"network|cisco|\btcp|routing|router|protocol|operating system|windows|\biot\b|internet of things|embedded|hardware|arduino|raspberry|electronic|circuit|fpga|wireless|wi-?fi|\b5g\b|telecom|robot|sd-?wan|printer|macos",
    ),
    (
        "finance",
        "Tài chính & Kế toán",
        r"financ|accounting|\baccount|invest|\btax|budget|econom|trading|banking|\baudit|valuation|portfolio|capital|insurance|payroll|crypto|blockchain|fintech|ledger|\bstocks?\b|market(?:s)? risk",
    ),
    (
        "marketing",
        "Marketing & Bán hàng",
        r"marketing|\bseo\b|sales|brand|advertis|social media|content|customer|\bcrm\b|salesforce|e-?commerce|copywrit|influenc|public relations|market research|target audience|value proposition|promotion",
    ),
    (
        "business",
        "Kinh doanh & Quản lý",
        r"manage|business|project|product|agile|scrum|kanban|strateg|entrepreneur|operation|supply chain|planning|stakeholder|\blean\b|six sigma|process|consult|governance|\brisk|compliance|\bhr\b|human resource|recruit|logistic|procurement|startup|innovation|diversity|pmi|capm|\bpmp\b|transformation",
    ),
    (
        "soft",
        "Kỹ năng mềm",
        r"communicat|teamwork|leadership|problem.solving|critical thinking|presentation|writing|time management|emotional|collaborat|creativ|public speaking|negotiat|decision|mentor|coaching|empathy|listening|adaptab|conflict|interpersonal|resilien|career|teaching|education|\blanguage|english|interview|facilitat|willpower|self-awareness|ethic|motivat|mindful",
    ),
    (
        "science",
        "Khoa học & Kỹ thuật",
        r"math|calculus|algebra|physic|chemi|biolog|geometr|science|health|medic|clinical|genetic|genom|ecolog|environment|energy|engineering|quantum|astronom|psycholog|nutrition|agricultur|climate|solar|photovolta|sustainab|diffraction|optics|\blight\b|senses",
    ),
]
OTHER = ("other", "Khác")

_COMPILED = [
    (key, re.compile(pattern, re.IGNORECASE)) for key, _, pattern in CATEGORIES
]
LABELS = {key: label for key, label, _ in CATEGORIES} | {OTHER[0]: OTHER[1]}
KEYS = [key for key, _, _ in CATEGORIES] + [OTHER[0]]


# lru_cache: tên kỹ năng hầu như không đổi → nhớ kết quả, lần gọi sau không chạy lại 15 biểu thức
# (đo 08/11: phân loại 5.893 tên mất ~285 ms lần đầu, các lần sau ~ vài ms).
@lru_cache(maxsize=None)
def categorize(skill_name: str) -> str:
    """Tên kỹ năng → key danh mục (vd 'Python Programming' → 'programming')."""
    for key, pattern in _COMPILED:
        if pattern.search(skill_name):
            return key
    return OTHER[0]
