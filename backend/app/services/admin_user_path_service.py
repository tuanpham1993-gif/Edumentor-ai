"""Nghiệp vụ admin xem tổng hợp lộ trình và tiến độ kỹ năng của người dùng (F14)."""

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.repositories.admin_user_path_repository import AdminUserPathRepository
from app.schemas.admin import (
    AdminPopularGoalItem,
    AdminUserBrief,
    AdminUserPathDetailItem,
    AdminUserPathEdgeItem,
    AdminUserPathNodeItem,
    AdminUserPathsDetailResponse,
    AdminUserPathsOverviewResponse,
    AdminUserPathsStats,
    AdminUserPathSummaryItem,
    AdminUserStatusCounts,
)
from app.schemas.common import PaginatedResponse


class AdminUserPathService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AdminUserPathRepository(db)

    def get_overview(self) -> AdminUserPathsOverviewResponse:
        stats_dict = self.repo.get_overview_stats()
        popular_goals_raw = self.repo.get_popular_goals(limit=8)

        return AdminUserPathsOverviewResponse(
            stats=AdminUserPathsStats(**stats_dict),
            popular_goals=[AdminPopularGoalItem(**g) for g in popular_goals_raw],
        )

    def list_users(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        search_by: str = "user",
        goal: str | None = None,
    ) -> PaginatedResponse[AdminUserPathSummaryItem]:
        total, rows = self.repo.list_users_with_summary(
            page=page,
            page_size=page_size,
            search=search,
            search_by=search_by,
            goal=goal,
        )

        items: list[AdminUserPathSummaryItem] = []
        for row in rows:
            user = row[0]
            items.append(
                AdminUserPathSummaryItem(
                    user_id=user.user_id,
                    full_name=user.full_name,
                    email=user.email,
                    role=user.role,
                    avatar_url=user.avatar_url,
                    created_at=user.created_at,
                    total_paths=int(row.total_paths),
                    ongoing_paths=int(row.ongoing_paths),
                    completed_paths=int(row.completed_paths),
                    abandoned_paths=int(row.abandoned_paths),
                    shared_paths=int(row.shared_paths),
                    known_skills_count=int(row.known_skills_count),
                    learning_skills_count=int(row.learning_skills_count),
                )
            )

        return PaginatedResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    def get_user_paths_detail(self, user_id: int) -> AdminUserPathsDetailResponse:
        user = self.repo.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Không tìm thấy người dùng với ID {user_id}.",
            )

        paths = self.repo.list_user_paths_with_graph(user_id)
        skill_status_map = self.repo.get_user_skill_status_map(user_id)

        status_counts = {
            "all": len(paths),
            "ongoing": 0,
            "completed": 0,
            "abandoned": 0,
        }

        path_items: list[AdminUserPathDetailItem] = []
        for path in paths:
            if path.status in status_counts:
                status_counts[path.status] += 1

            nodes_dto: list[AdminUserPathNodeItem] = []
            target_skills: list[str] = []
            progress_known = 0
            progress_learning = 0

            for node in path.nodes:
                skill_name = node.skill.skill if node.skill else f"Kỹ năng #{node.skill_id}"
                skill_status = skill_status_map.get(node.skill_id, "unlearned")
                if skill_status not in ("known", "learning"):
                    skill_status = "unlearned"

                if skill_status == "known":
                    progress_known += 1
                elif skill_status == "learning":
                    progress_learning += 1

                if node.is_target:
                    target_skills.append(skill_name)

                nodes_dto.append(
                    AdminUserPathNodeItem(
                        skill_id=node.skill_id,
                        skill_name=skill_name,
                        node_role=node.node_role,
                        is_target=node.is_target,
                        is_required=node.is_required,
                        added_by=node.added_by,
                        display_order=node.display_order,
                        user_skill_status=skill_status,
                    )
                )

            edges_dto = [
                AdminUserPathEdgeItem(
                    from_skill_id=edge.from_skill_id,
                    to_skill_id=edge.to_skill_id,
                    relation_type=edge.relation_type,
                )
                for edge in path.edges
            ]

            path_items.append(
                AdminUserPathDetailItem(
                    record_id=path.record_id,
                    original_query=path.original_query,
                    goal_type=path.goal_type,
                    status=path.status,
                    is_shared=bool(path.is_shared),
                    share_code=path.share_code,
                    shared_at=path.shared_at,
                    clone_count=int(path.clone_count or 0),
                    cloned_from_id=path.cloned_from_id,
                    target_skills=target_skills,
                    progress_known=progress_known,
                    progress_learning=progress_learning,
                    progress_total=len(nodes_dto),
                    nodes=nodes_dto,
                    edges=edges_dto,
                )
            )

        return AdminUserPathsDetailResponse(
            user=AdminUserBrief.model_validate(user),
            status_counts=AdminUserStatusCounts(**status_counts),
            paths=path_items,
        )
