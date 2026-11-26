import secrets
from datetime import UTC, datetime
from typing import Literal

from sqlalchemy import Select, case, func, select
from sqlalchemy.orm import Session

from app.models.learning_path import LearningPath, LearningPathEdge, LearningPathNode
from app.services.learning_path_edge_service import add_new_learning_path_edges
from app.services.learning_path_node_service import add_new_learning_path_nodes


def build_learning_path_query(
    student_id: int | None = None,
    keyword: str | None = None,
    goal_type: Literal["career", "project"] | None = None,
    status: Literal["completed", "ongoing", "abandoned"] | None = None,
) -> Select:
    select_query = select(LearningPath)

    if student_id is not None:
        select_query = select_query.where(LearningPath.student_id == student_id)

    if keyword and keyword.strip():
        pattern = f"%{keyword.strip()}%"
        select_query = select_query.where(LearningPath.original_query.ilike(pattern))

    if goal_type is not None:
        select_query = select_query.where(LearningPath.goal_type == goal_type)

    if status is not None:
        select_query = select_query.where(LearningPath.status == status)
    return select_query.order_by(LearningPath.record_id.desc())


def count_total_learning_path(select_query: Select):
    return select(func.count()).select_from(select_query.order_by(None).subquery())


def list_learning_path(db: Session, skip: int = 0, limit: int = 10, **filters) -> tuple[int, list[LearningPath]]:
    select_query = build_learning_path_query(**filters)
    total = db.execute(count_total_learning_path(select_query)).scalar_one()
    # lazy joined effect we use unique to filter out distinct row-> scalars take value out of each row return object
    # .all() return as list
    items = db.execute(select_query.offset(skip).limit(limit)).unique().scalars().all()
    return total, list(items)


def get_learning_path(db: Session, record_id: int, student_id: int | None = None) -> LearningPath | None:
    query = select(LearningPath).where(LearningPath.record_id == record_id)

    if student_id is not None:
        query = query.where(LearningPath.student_id == student_id)
    return db.scalar(query)


def get_learning_path_statistics(
    db: Session,
    student_id: int,
) -> dict[str, int]:
    query = select(
        func.count(LearningPath.record_id).label("total"),
        func.count(case((LearningPath.status == "ongoing", 1))).label("ongoing"),
        func.count(case((LearningPath.status == "completed", 1))).label("completed"),
    ).where(LearningPath.student_id == student_id)
    result = db.execute(query).one()

    return {
        "total": result.total,
        "ongoing": result.ongoing,
        "completed": result.completed,
    }


def add_learning_path(
    db: Session,
    student_id: int,
    original_query: str,
    goal_type: Literal["career", "project"],
) -> LearningPath:

    new_path = LearningPath(
        student_id=student_id,
        original_query=original_query,
        goal_type=goal_type,
        status="ongoing",
    )

    db.add(new_path)
    db.flush()
    return new_path


def create_learning_path(
    db: Session,
    student_id: int,
    original_query: str,
    goal_type: str,
    nodes: list,
    edges: list,
) -> LearningPath:
    try:
        # 1. Create parent learning path.
        new_path = add_learning_path(db=db, student_id=student_id, original_query=original_query, goal_type=goal_type)

        db.flush()  # Generate record_id before creating nodes and edges.

        # 2. Create all nodes.
        add_new_learning_path_nodes(db=db, path_id=new_path.record_id, nodes=nodes)

        # 3. Create all edges.
        add_new_learning_path_edges(db=db, path_id=new_path.record_id, edges=edges, nodes=nodes)

        # 4. Commit everything together.
        db.commit()
        db.refresh(new_path)
        return new_path

    except Exception:
        db.rollback()
        raise


"""
{
  "original_query": "I want to become a backend developer using Python.",
  "goal_type": "career",
  "nodes": [
    {
      "skill_id": 101,
      "skill_name": "Cascading Style Sheets (CSS)",
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 1000
    },
    {
      "skill_id": 102,
      "skill_name": "Computer Programming",
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 2000
    },
    {
      "skill_id": 103,
      "skill_name": "Database (DBMS)",
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 3000
    },
    {
      "skill_id": 104,
      "skill_name": "HTML",
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 4000
    },
    {
      "skill_id": 105,
      "skill_name": "Web Development",
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 5000
    },
    {
      "skill_id": 106,
      "skill_name": "Backend Systems",
      "node_role": null,
      "is_target": true,
      "added_by": "system",
      "is_required": true,
      "display_order": 6000
    },
    {
      "skill_id": 167,
      "skill_name": "Python Programming",
      "node_role": null,
      "is_target": true,
      "added_by": "system",
      "is_required": true,
      "display_order": 7000
    },
    {
      "skill_id": 107,
      "skill_name": "RESTful API",
      "node_role": null,
      "is_target": true,
      "added_by": "system",
      "is_required": true,
      "display_order": 8000
    },
    {
      "skill_id": 108,
      "skill_name": "SQL",
      "node_role": null,
      "is_target": true,
      "added_by": "system",
      "is_required": true,
      "display_order": 9000
    },
    {
      "skill_id": 109,
      "skill_name": "Flask",
      "node_role": "related",
      "is_target": false,
      "added_by": "system",
      "is_required": false,
      "display_order": 10000
    }
  ],
  "edges": [
    {
      "from_skill_id": 101,
      "from_skill_name": "Cascading Style Sheets (CSS)",
      "to_skill_id": 105,
      "to_skill_name": "Web Development",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 102,
      "from_skill_name": "Computer Programming",
      "to_skill_id": 167,
      "to_skill_name": "Python Programming",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 103,
      "from_skill_name": "Database (DBMS)",
      "to_skill_id": 108,
      "to_skill_name": "SQL",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 104,
      "from_skill_name": "HTML",
      "to_skill_id": 105,
      "to_skill_name": "Web Development",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 105,
      "from_skill_name": "Web Development",
      "to_skill_id": 106,
      "to_skill_name": "Backend Systems",
      "relation_type": "extension"
    },
    {
      "from_skill_id": 105,
      "from_skill_name": "Web Development",
      "to_skill_id": 107,
      "to_skill_name": "RESTful API",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 167,
      "from_skill_name": "Python Programming",
      "to_skill_id": 109,
      "to_skill_name": "Flask",
      "relation_type": "prerequisite"
    },
    {
      "from_skill_id": 107,
      "from_skill_name": "RESTful API",
      "to_skill_id": 109,
      "to_skill_name": "Flask",
      "relation_type": "related"
    }
  ]
}
"""


def abandon_learning_path(
    db: Session,
    record_id: int,
    student_id: int,
) -> LearningPath | None:
    try:
        learning_path = get_learning_path(
            db=db,
            record_id=record_id,
            student_id=student_id,
        )
        if learning_path is None:
            return None
        if learning_path.status == "abandoned":
            raise ValueError("Learning path is already abandoned.")
        learning_path.status = "abandoned"
        db.commit()
        db.refresh(learning_path)
        return learning_path

    except Exception:
        db.rollback()
        raise


def generate_unique_share_code(db: Session, length: int = 10) -> str:
    """Sinh mã chia sẻ ngẫu nhiên an toàn, đảm bảo không trùng lặp."""
    for _ in range(10):
        code = secrets.token_urlsafe(length)[:length]
        existing = db.scalar(select(LearningPath).where(LearningPath.share_code == code))
        if not existing:
            return code
    # Fallback nếu thử nhiều lần bị trùng
    return secrets.token_hex(length // 2)


def enable_learning_path_share(db: Session, record_id: int, student_id: int) -> LearningPath:
    """Bật tính năng chia sẻ lộ trình cho học viên sở hữu."""
    path = get_learning_path(db=db, record_id=record_id, student_id=student_id)
    if not path:
        raise ValueError("Lộ trình không tồn tại hoặc bạn không có quyền chia sẻ.")

    if path.status == "abandoned":
        raise ValueError("Không thể chia sẻ lộ trình đã bị hủy bỏ.")

    if not path.share_code:
        path.share_code = generate_unique_share_code(db)

    path.is_shared = True
    path.shared_at = datetime.now(UTC)
    db.commit()
    db.refresh(path)
    return path


def disable_learning_path_share(db: Session, record_id: int, student_id: int) -> LearningPath:
    """Tắt tính năng chia sẻ lộ trình."""
    path = get_learning_path(db=db, record_id=record_id, student_id=student_id)
    if not path:
        raise ValueError("Lộ trình không tồn tại hoặc bạn không có quyền chỉnh sửa.")

    path.is_shared = False
    db.commit()
    db.refresh(path)
    return path


def get_shared_learning_path(db: Session, share_code: str) -> LearningPath | None:
    """Lấy thông tin lộ trình được chia sẻ thông qua mã share_code."""
    query = select(LearningPath).where(
        LearningPath.share_code == share_code,
        LearningPath.is_shared == True,
        LearningPath.status != "abandoned",
    )
    return db.scalar(query)


def clone_shared_learning_path(db: Session, share_code: str, student_id: int) -> LearningPath:
    """Sao chép lộ trình được chia sẻ về tài khoản của học viên hiện tại trong một Transaction duy nhất."""
    source_path = get_shared_learning_path(db=db, share_code=share_code)
    if not source_path:
        raise ValueError("Lộ trình được chia sẻ không tồn tại hoặc đã ngừng chia sẻ.")

    # Ràng buộc an toàn: Không cho phép tự clone lộ trình của chính mình
    if source_path.student_id == student_id:
        raise ValueError("Đây là lộ trình của bạn. Bạn không thể tự sao chép lộ trình của chính mình.")

    try:
        # 1. Tạo bản ghi LearningPath mới cho học viên
        new_path = LearningPath(
            student_id=student_id,
            original_query=source_path.original_query,
            goal_type=source_path.goal_type,
            status="ongoing",
            is_shared=False,
            share_code=None,
            clone_count=0,
            cloned_from_id=source_path.record_id,
        )
        db.add(new_path)
        db.flush()  # Sinh record_id cho new_path

        # 2. Sao chép toàn bộ nodes
        for node in source_path.nodes:
            new_node = LearningPathNode(
                path_id=new_path.record_id,
                skill_id=node.skill_id,
                node_role=node.node_role,
                is_target=node.is_target,
                added_by="system",
                is_required=node.is_required,
                display_order=node.display_order,
            )
            db.add(new_node)

        # 3. Sao chép toàn bộ edges
        for edge in source_path.edges:
            new_edge = LearningPathEdge(
                path_id=new_path.record_id,
                from_skill_id=edge.from_skill_id,
                to_skill_id=edge.to_skill_id,
                relation_type=edge.relation_type,
            )
            db.add(new_edge)

        # 4. Tăng lượt clone_count của lộ trình gốc
        source_path.clone_count = (source_path.clone_count or 0) + 1

        # 5. Commit toàn bộ
        db.commit()
        db.refresh(new_path)
        return new_path

    except Exception:
        db.rollback()
        raise
