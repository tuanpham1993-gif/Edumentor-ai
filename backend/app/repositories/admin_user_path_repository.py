"""Repository tổng hợp số liệu lộ trình người dùng cho Admin (F14).

Chỉ truy vấn DB (SQLAlchemy 2.0), không chứa nghiệp vụ hay commit.
"""

from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.learning_path import LearningPath, LearningPathNode
from app.models.user import Users
from app.models.user_skill import UserSkill


class AdminUserPathRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_overview_stats(self) -> dict[str, int]:
        """Thống kê tổng hợp user thật và các lộ trình thuộc về user thật."""
        total_users = self.db.execute(select(func.count(Users.user_id))).scalar_one()

        path_stats_stmt = (
            select(
                func.count(func.distinct(LearningPath.student_id)).label("users_with_paths"),
                func.count(LearningPath.record_id).label("total_paths"),
                func.count(case((LearningPath.status == "ongoing", 1))).label("ongoing_paths"),
                func.count(case((LearningPath.status == "completed", 1))).label("completed_paths"),
                func.count(case((LearningPath.status == "abandoned", 1))).label("abandoned_paths"),
                func.count(case((LearningPath.is_shared.is_(True), 1))).label("shared_paths"),
            )
            .select_from(LearningPath)
            .join(Users, LearningPath.student_id == Users.user_id)
        )
        row = self.db.execute(path_stats_stmt).one()

        return {
            "total_users": int(total_users or 0),
            "users_with_paths": int(row.users_with_paths or 0),
            "total_paths": int(row.total_paths or 0),
            "ongoing_paths": int(row.ongoing_paths or 0),
            "completed_paths": int(row.completed_paths or 0),
            "abandoned_paths": int(row.abandoned_paths or 0),
            "shared_paths": int(row.shared_paths or 0),
        }

    def get_popular_goals(self, limit: int = 8) -> list[dict]:
        """Gom nhóm các mục tiêu lộ trình phổ biến của người dùng thật."""
        normalized_query = func.lower(func.trim(LearningPath.original_query))
        stmt = (
            select(
                func.min(func.trim(LearningPath.original_query)).label("title"),
                func.count(LearningPath.record_id).label("path_count"),
                func.count(func.distinct(LearningPath.student_id)).label("user_count"),
            )
            .select_from(LearningPath)
            .join(Users, LearningPath.student_id == Users.user_id)
            .group_by(normalized_query)
            .order_by(
                func.count(func.distinct(LearningPath.student_id)).desc(),
                func.count(LearningPath.record_id).desc(),
                func.min(func.trim(LearningPath.original_query)).asc(),
            )
            .limit(limit)
        )
        rows = self.db.execute(stmt).all()
        return [
            {
                "title": r.title,
                "path_count": int(r.path_count),
                "user_count": int(r.user_count),
            }
            for r in rows
        ]

    def list_users_with_summary(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        search_by: str = "user",
        goal: str | None = None,
    ) -> tuple[int, list]:
        """Lấy danh sách user phân trang kèm tổng số lộ trình và kỹ năng của từng user."""
        user_filter_stmt = select(Users)

        if goal and goal.strip():
            goal_norm = goal.strip().lower()
            matching_students_by_goal = select(LearningPath.student_id).where(
                func.lower(func.trim(LearningPath.original_query)) == goal_norm
            )
            user_filter_stmt = user_filter_stmt.where(
                Users.user_id.in_(matching_students_by_goal)
            )

        if search and search.strip():
            q = f"%{search.strip()}%"
            if search_by == "goal":
                matching_students_by_query = select(LearningPath.student_id).where(
                    LearningPath.original_query.ilike(q)
                )
                user_filter_stmt = user_filter_stmt.where(
                    Users.user_id.in_(matching_students_by_query)
                )
            else:
                user_filter_stmt = user_filter_stmt.where(
                    or_(Users.full_name.ilike(q), Users.email.ilike(q))
                )

        # Đếm tổng số user khớp bộ lọc
        count_stmt = select(func.count()).select_from(user_filter_stmt.subquery())
        total = int(self.db.execute(count_stmt).scalar_one() or 0)

        # Subquery tổng hợp theo bảng để tránh nhân chéo (Cartesian product)
        path_agg = (
            select(
                LearningPath.student_id.label("student_id"),
                func.count(LearningPath.record_id).label("total_paths"),
                func.count(case((LearningPath.status == "ongoing", 1))).label("ongoing_paths"),
                func.count(case((LearningPath.status == "completed", 1))).label("completed_paths"),
                func.count(case((LearningPath.status == "abandoned", 1))).label("abandoned_paths"),
                func.count(case((LearningPath.is_shared.is_(True), 1))).label("shared_paths"),
            )
            .group_by(LearningPath.student_id)
            .subquery()
        )

        skill_agg = (
            select(
                UserSkill.user_id.label("user_id"),
                func.count(case((UserSkill.status == "known", 1))).label("known_skills_count"),
                func.count(case((UserSkill.status == "learning", 1))).label("learning_skills_count"),
            )
            .group_by(UserSkill.user_id)
            .subquery()
        )

        filtered_users_subq = user_filter_stmt.subquery()
        total_paths_col = func.coalesce(path_agg.c.total_paths, 0).label("total_paths")

        offset = (page - 1) * page_size
        main_stmt = (
            select(
                Users,
                total_paths_col,
                func.coalesce(path_agg.c.ongoing_paths, 0).label("ongoing_paths"),
                func.coalesce(path_agg.c.completed_paths, 0).label("completed_paths"),
                func.coalesce(path_agg.c.abandoned_paths, 0).label("abandoned_paths"),
                func.coalesce(path_agg.c.shared_paths, 0).label("shared_paths"),
                func.coalesce(skill_agg.c.known_skills_count, 0).label("known_skills_count"),
                func.coalesce(skill_agg.c.learning_skills_count, 0).label("learning_skills_count"),
            )
            .join(filtered_users_subq, Users.user_id == filtered_users_subq.c.user_id)
            .outerjoin(path_agg, Users.user_id == path_agg.c.student_id)
            .outerjoin(skill_agg, Users.user_id == skill_agg.c.user_id)
            .order_by(total_paths_col.desc(), Users.user_id.asc())
            .offset(offset)
            .limit(page_size)
        )

        rows = self.db.execute(main_stmt).all()
        return total, rows

    def get_user_by_id(self, user_id: int) -> Users | None:
        return self.db.get(Users, user_id)

    def list_user_paths_with_graph(self, user_id: int) -> list[LearningPath]:
        stmt = (
            select(LearningPath)
            .where(LearningPath.student_id == user_id)
            .options(
                selectinload(LearningPath.nodes).selectinload(LearningPathNode.skill),
                selectinload(LearningPath.edges),
            )
            .order_by(LearningPath.record_id.desc())
        )
        return list(self.db.execute(stmt).scalars().unique().all())

    def get_user_skill_status_map(self, user_id: int) -> dict[int, str]:
        stmt = select(UserSkill.skill_id, UserSkill.status).where(UserSkill.user_id == user_id)
        rows = self.db.execute(stmt).all()
        return {row.skill_id: row.status for row in rows}
