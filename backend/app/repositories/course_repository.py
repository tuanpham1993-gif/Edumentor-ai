import re
from typing import List, Literal, Optional, Tuple
from sqlalchemy import and_, case, delete, func, or_, select
from sqlalchemy.orm import Session, selectinload
from app.models.course import Courses
from app.models.course_skill import CourseSkill
from app.models.skill import Skills


MAX_SEARCH_TOKENS = 8


def _escape_like(value: str) -> str:
    """Escape ký tự wildcard của SQL LIKE (\\, %, _) để tránh khớp nhầm."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


def _tokenize_search(search: str) -> tuple[str, list[str]]:
    """Chuẩn hóa cụm tìm kiếm và tách từ multi-word (khử trùng lặp, tối đa 8 từ)."""
    phrase = " ".join(search.strip().split())
    if not phrase:
        return "", []
    tokens: list[str] = []
    seen: set[str] = set()
    for part in phrase.split(" "):
        low = part.lower()
        if low and low not in seen:
            seen.add(low)
            tokens.append(part)
            if len(tokens) >= MAX_SEARCH_TOKENS:
                break
    return phrase, tokens


def _column_matches_token(col, tok: str, is_postgres: bool):
    """Khớp token trên 1 cột văn bản.
    - Token ngắn (1–2 ký tự, vd 'ng', 'ai', 'ml', 'r', 'go'): khớp nguyên từ (word boundary)
      để tránh khớp nhầm vào đuôi '-ing' (vd 'Andrew Ng' khớp 'Programmi[ng]') hay 'AI' khớp 'Em[ai]l'.
    - Token từ 3 ký tự trở lên: khớp chuỗi con không phân biệt hoa thường (ILIKE).
    """
    if len(tok) <= 2:
        if is_postgres:
            regex = rf"(^|[^[:alnum:]]){re.escape(tok)}([^[:alnum:]]|$)"
            return col.op("~*")(regex)
        esc = _escape_like(tok)
        return or_(
            col.ilike(esc, escape="\\"),
            col.ilike(f"{esc} %", escape="\\"),
            col.ilike(f"% {esc}", escape="\\"),
            col.ilike(f"% {esc} %", escape="\\"),
            col.ilike(f"%({esc})%", escape="\\"),
            col.ilike(f"% {esc},%", escape="\\"),
            col.ilike(f"%-{esc}%", escape="\\"),
            col.ilike(f"%{esc}-%", escape="\\"),
            col.ilike(f"%.{esc}%", escape="\\"),
        )
    return col.ilike(f"%{_escape_like(tok)}%", escape="\\")


class CourseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, course_id: int) -> Optional[Courses]:
        return self.db.get(Courses, course_id)

    def get_by_url(self, url: Optional[str]) -> Optional[Courses]:
        if not url:
            return None
        stmt = select(Courses).where(Courses.url == url)
        return self.db.execute(stmt).scalars().unique().one_or_none()

    def list_courses(
        self,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        level: Optional[str] = None,
    ) -> Tuple[int, List[Courses]]:
        stmt = select(Courses)

        if search:
            search_term = f"%{search.strip()}%"
            stmt = stmt.where(
                or_(
                    Courses.title.ilike(search_term),
                    Courses.description.ilike(search_term),
                    Courses.instructor.ilike(search_term),
                    Courses.organization.ilike(search_term),
                )
            )

        if level and level.strip():
            stmt = stmt.where(Courses.level.ilike(level.strip()))

        # Count total
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        # Pagination
        offset = (page - 1) * page_size
        stmt = stmt.order_by(Courses.course_id.desc()).offset(offset).limit(page_size)
        items = list(self.db.execute(stmt).scalars().unique().all())

        return total, items

    def create(self, course_data: dict) -> Courses:
        course = Courses(**course_data)
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def update(self, course: Courses, update_data: dict) -> Courses:
        for key, value in update_data.items():
            if hasattr(course, key):
                setattr(course, key, value)
        self.db.commit()
        self.db.refresh(course)
        return course

    def delete(self, course: Courses) -> None:
        # Xóa các liên kết trong secondary table qua ORM
        course.skills_info = []
        self.db.flush()
        self.db.delete(course)
        self.db.commit()

    # CourseSkill relations
    def get_relation(self, course_id: int, skill_id: int) -> Optional[CourseSkill]:
        stmt = select(CourseSkill).where(
            CourseSkill.course_id == course_id,
            CourseSkill.skill_id == skill_id,
        )
        return self.db.execute(stmt).scalar_one_or_none()

    def list_relations(
        self,
        page: int = 1,
        page_size: int = 20,
        course_id: Optional[int] = None,
        skill_id: Optional[int] = None,
    ) -> Tuple[int, List[dict]]:
        stmt = (
            select(
                CourseSkill.course_id,
                Courses.title.label("course_title"),
                CourseSkill.skill_id,
                Skills.skill.label("skill_name"),
            )
            .join(Courses, CourseSkill.course_id == Courses.course_id)
            .join(Skills, CourseSkill.skill_id == Skills.skill_id)
        )

        if course_id is not None:
            stmt = stmt.where(CourseSkill.course_id == course_id)
        if skill_id is not None:
            stmt = stmt.where(CourseSkill.skill_id == skill_id)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar_one()

        offset = (page - 1) * page_size
        stmt = stmt.order_by(CourseSkill.course_id.asc(), CourseSkill.skill_id.asc()).offset(offset).limit(page_size)
        rows = self.db.execute(stmt).mappings().all()

        return total, [dict(r) for r in rows]

    def add_relation(self, course_id: int, skill_id: int) -> CourseSkill:
        relation = CourseSkill(course_id=course_id, skill_id=skill_id)
        self.db.add(relation)
        self.db.commit()
        return relation

    def delete_relation(self, course_id: int, skill_id: int) -> bool:
        stmt = delete(CourseSkill).where(
            CourseSkill.course_id == course_id,
            CourseSkill.skill_id == skill_id,
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount > 0


def list_courses(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    search: str | None = None,
    skill_id: int | None = None,
    level: str | None = None,
    sort_by: Literal["relevance", "rating", "num_reviews"] | None = None,
) -> tuple[int, list[Courses]]:
    """Truy vấn danh sách khóa học kèm tìm kiếm ưu tiên 4 tầng (title > organization > instructor > description)."""
    query = select(Courses)
    relevance_score = None

    # 1. Bộ lọc tìm kiếm từ khóa (multi-word AND trên 4 trường: title, organization, instructor, description)
    if search and search.strip():
        phrase, tokens = _tokenize_search(search)
        if tokens:
            is_postgres = db.bind is not None and db.bind.dialect.name == "postgresql"
            token_filters = []
            token_scores = []

            for tok in tokens:
                title_match = _column_matches_token(Courses.title, tok, is_postgres)
                org_match = _column_matches_token(Courses.organization, tok, is_postgres)
                instructor_match = _column_matches_token(Courses.instructor, tok, is_postgres)
                desc_match = _column_matches_token(Courses.description, tok, is_postgres)

                token_filters.append(or_(title_match, org_match, instructor_match, desc_match))

                # Thang điểm 4 tầng thuần túy: title (100) > organization (50) > instructor (25) > description (10)
                if sort_by == "relevance":
                    token_scores.append(
                        case(
                            (title_match, 100),
                            (org_match, 50),
                            (instructor_match, 25),
                            (desc_match, 10),
                            else_=0,
                        )
                    )

            query = query.where(and_(*token_filters))

            if sort_by == "relevance":
                escaped_phrase = _escape_like(phrase)
                phrase_title_bonus = case(
                    (Courses.title.ilike(f"{escaped_phrase}%", escape="\\"), 80),
                    (Courses.title.ilike(f"%{escaped_phrase}%", escape="\\"), 60),
                    else_=0,
                )
                phrase_org_bonus = case(
                    (Courses.organization.ilike(f"%{escaped_phrase}%", escape="\\"), 40),
                    else_=0,
                )
                phrase_instructor_bonus = case(
                    (Courses.instructor.ilike(f"%{escaped_phrase}%", escape="\\"), 30),
                    else_=0,
                )
                phrase_desc_bonus = case(
                    (Courses.description.ilike(f"%{escaped_phrase}%", escape="\\"), 10),
                    else_=0,
                )
                relevance_score = (
                    phrase_title_bonus
                    + phrase_org_bonus
                    + phrase_instructor_bonus
                    + phrase_desc_bonus
                )
                for score_expr in token_scores:
                    relevance_score = relevance_score + score_expr

    # 2. Bộ lọc theo độ khó
    if level and level.strip():
        query = query.where(Courses.level.ilike(level.strip()))

    # 3. Bộ lọc theo skill_id
    if skill_id is not None:
        query = query.join(CourseSkill, Courses.course_id == CourseSkill.course_id).where(
            CourseSkill.skill_id == skill_id
        )

    # Đếm tổng số bản ghi khớp điều kiện
    count_query = select(func.count()).select_from(query.order_by(None).subquery())
    total = db.scalar(count_query) or 0

    # 4. Sắp xếp
    if sort_by == "relevance" and relevance_score is not None:
        query = query.order_by(
            relevance_score.desc(),
            Courses.num_reviews.desc().nullslast(),
            Courses.rating.desc().nullslast(),
            Courses.course_id.asc(),
        )
    elif sort_by == "rating":
        query = query.order_by(
            Courses.rating.desc().nullslast(),
            Courses.num_reviews.desc().nullslast(),
            Courses.course_id.asc(),
        )
    elif sort_by in ("num_reviews", "relevance"):
        query = query.order_by(
            Courses.num_reviews.desc().nullslast(),
            Courses.rating.desc().nullslast(),
            Courses.course_id.asc(),
        )
    else:
        query = query.order_by(Courses.course_id.asc())

    # 5. Phân trang
    offset = max(0, (page - 1) * page_size)
    items = db.scalars(
        query.options(selectinload(Courses.skills_info))
        .offset(offset)
        .limit(page_size)
    ).unique().all()

    return total, list(items)


def get_course_by_id(db: Session, course_id: int) -> Courses | None:
    """Truy vấn thông tin chi tiết một khóa học theo ID kèm danh sách kỹ năng."""
    return db.scalars(
        select(Courses)
        .options(selectinload(Courses.skills_info))
        .where(Courses.course_id == course_id)
    ).unique().one_or_none()


def get_course_skills(db: Session, course_id: int) -> list[Skills] | None:
    """Truy vấn danh sách kỹ năng liên quan đến một khóa học."""
    course = get_course_by_id(db=db, course_id=course_id)
    if course is None:
        return None
    return list(course.skills_info)