from typing import Literal
from pydantic import BaseModel, Field, field_validator, model_validator
from app.schemas.learning_path import LearningPathResponse

GoalType = Literal["career", "project"]

RelationType = Literal[
    "prerequisite",
    "related",
    "extension",
]

# ====================
# 1. Generate request
# ====================

class LearningPathGenerateRequest(BaseModel):
    original_query: str = Field(min_length=1)
    #goal_type: GoalType

    @field_validator("original_query")
    @classmethod
    def validate_original_query(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Learning goal cannot be empty.")

        return value


# ======================================================
# 2. Preview node
# ======================================================

class LearningPathPreviewNode(BaseModel):
    path_id: int | None = None
    skill_id: int
    skill_name: str

    node_role: RelationType | None = None
    is_target: bool
    added_by: Literal["system", "user"]
    is_required: bool
    display_order: int


# ======================================================
# 3. Preview edge
# ======================================================

class LearningPathPreviewEdge(BaseModel):
    path_id: int | None = None

    from_skill_id: int
    from_skill_name: str

    to_skill_id: int
    to_skill_name: str

    relation_type: RelationType


# ======================================================
# 4. Preview response
# ======================================================

class LearningPathPreviewResponse(BaseModel):
    original_query: str
    goal_type: GoalType

    nodes: list[LearningPathPreviewNode]
    edges: list[LearningPathPreviewEdge]

    layer: dict[int, list[int]]

# =======================
# 5. Confirmation request
# =======================

class LearningPathConfirmRequest(BaseModel):
    confirmed: bool

    # Preview information
    original_query: str | None = None
    goal_type: GoalType | None = None

    nodes: list[LearningPathPreviewNode] | None = None
    edges: list[LearningPathPreviewEdge] | None = None

    # Only needed by the frontend for displaying the graph.
    # The backend does not persist this field.
    layer: dict[int, list[int]] | None = None

    @model_validator(mode="after")
    def validate_confirmation_data(self):
        if self.confirmed:
            if not self.original_query or not self.original_query.strip():
                raise ValueError("Original query is required when confirming a learning path.")

            if self.goal_type is None:
                raise ValueError("Goal type is required when confirming a learning path.")

            if not self.nodes:
                raise ValueError("Learning path must contain at least one node.")

        return self


# =====================
# 6. Rejection response
# =====================

class LearningPathRejectedResponse(BaseModel):
    confirmed: bool = False
    message: str
    next_action: str