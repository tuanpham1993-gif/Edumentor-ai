"""Schema request/response cho các chức năng quản trị (F14 - Admin User Paths)."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class AdminPopularGoalItem(BaseModel):
    title: str = Field(..., description="Tên mục tiêu lộ trình phổ biến")
    path_count: int = Field(..., ge=0, description="Số lượng lộ trình có mục tiêu này")
    user_count: int = Field(..., ge=0, description="Số lượng người dùng sở hữu mục tiêu này")


class AdminUserPathsStats(BaseModel):
    total_users: int = Field(..., ge=0, description="Tổng số tài khoản người dùng")
    users_with_paths: int = Field(..., ge=0, description="Số người dùng đã có ít nhất 1 lộ trình")
    total_paths: int = Field(..., ge=0, description="Tổng số lộ trình của tất cả người dùng")
    ongoing_paths: int = Field(..., ge=0, description="Số lộ trình đang học")
    completed_paths: int = Field(..., ge=0, description="Số lộ trình đã hoàn thành")
    abandoned_paths: int = Field(..., ge=0, description="Số lộ trình đã từ bỏ")
    shared_paths: int = Field(..., ge=0, description="Số lộ trình đang bật chia sẻ công khai")


class AdminUserPathsOverviewResponse(BaseModel):
    stats: AdminUserPathsStats
    popular_goals: list[AdminPopularGoalItem] = Field(default_factory=list)


class AdminUserPathSummaryItem(BaseModel):
    user_id: int
    full_name: str
    email: str
    role: Literal["student", "admin"]
    avatar_url: str | None = None
    created_at: datetime
    total_paths: int = 0
    ongoing_paths: int = 0
    completed_paths: int = 0
    abandoned_paths: int = 0
    shared_paths: int = 0
    known_skills_count: int = 0
    learning_skills_count: int = 0

    model_config = ConfigDict(from_attributes=True)


class AdminUserPathNodeItem(BaseModel):
    skill_id: int
    skill_name: str
    node_role: str | None = None
    is_target: bool
    is_required: bool
    added_by: str
    display_order: int
    user_skill_status: Literal["known", "learning", "unlearned"]


class AdminUserPathEdgeItem(BaseModel):
    from_skill_id: int
    to_skill_id: int
    relation_type: Literal["prerequisite", "related", "extension"]


class AdminUserPathDetailItem(BaseModel):
    record_id: int
    original_query: str
    goal_type: Literal["career", "project", "template"]
    status: Literal["ongoing", "completed", "abandoned"]
    is_shared: bool = False
    share_code: str | None = None
    shared_at: datetime | None = None
    clone_count: int = 0
    cloned_from_id: int | None = None
    target_skills: list[str] = Field(default_factory=list)
    progress_known: int = 0
    progress_learning: int = 0
    progress_total: int = 0
    nodes: list[AdminUserPathNodeItem] = Field(default_factory=list)
    edges: list[AdminUserPathEdgeItem] = Field(default_factory=list)


class AdminUserStatusCounts(BaseModel):
    all: int = 0
    ongoing: int = 0
    completed: int = 0
    abandoned: int = 0


class AdminUserBrief(BaseModel):
    user_id: int
    full_name: str
    email: str
    role: str
    avatar_url: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AdminUserPathsDetailResponse(BaseModel):
    user: AdminUserBrief
    status_counts: AdminUserStatusCounts
    paths: list[AdminUserPathDetailItem] = Field(default_factory=list)
