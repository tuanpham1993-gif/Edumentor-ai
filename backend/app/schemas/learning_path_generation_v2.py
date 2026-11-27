"""AI learning path v2: POST /generate_ai_2 (preview) and POST /confirm-2 (save).

Request of /generate_ai_2 is the G1 input itself (app/utils/learner_analyzer/schemas.G1Input):
    {"original_query": "...", "learner_input": {current_job_title, career_level, ...}}

Preview nodes/edges keep the field names of the v1 preview (learning_path_generation.py) so the
saved path uses the same learning_path_nodes / learning_path_edges tables, plus:
    node.state  known | satisfied | learning | eligible | locked
    node.layer  column in the graph (0 = start)
"""
from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator

from app.schemas.learner_profile import LearnerProfileResponse
from app.schemas.learning_path_generation import GoalType, LearningPathPreviewEdge, LearningPathPreviewNode
from app.utils.learner_analyzer.schemas import ClarificationItem, NormalizedG1Output

NodeState = Literal["known", "satisfied", "learning", "eligible", "locked"]
TargetSource = Literal["role", "technology"]


class PreviewNode2(LearningPathPreviewNode):
    state: NodeState
    layer: int = Field(ge=0)


class GraphTarget(BaseModel):
    skill_id: int
    skill_name: str
    source: TargetSource


class MatchedRole(BaseModel):
    role_id: int
    role_name: str
    match_method: Optional[str] = None
    match_score: Optional[float] = None


class GraphStats(BaseModel):
    full_graph_nodes: int = 0
    kept_nodes: int = 0
    known_or_satisfied: int = 0
    trimmed_nodes: int = 0
    remaining_to_learn: int = 0
    eligible_now: int = 0
    all_targets_satisfied: bool = False


class LearningPathPreview2Response(BaseModel):
    status: Literal["ready", "needs_clarification"]
    clarification_required: list[ClarificationItem] = Field(default_factory=list)

    original_query: str
    goal_type: GoalType
    profile: NormalizedG1Output                 # G1 output after skill / role linking
    role: Optional[MatchedRole] = None
    targets: list[GraphTarget] = Field(default_factory=list)

    nodes: list[PreviewNode2] = Field(default_factory=list)
    edges: list[LearningPathPreviewEdge] = Field(default_factory=list)
    layer: dict[int, list[int]] = Field(default_factory=dict)

    retrieval_status: Literal["complete", "incomplete"] = "complete"
    warnings: list[str] = Field(default_factory=list)
    stats: GraphStats = Field(default_factory=GraphStats)
    generator_version: str


class LearningPathConfirm2Request(BaseModel):
    """The preview returned by /generate_ai_2, sent back when the learner accepts or rejects it."""
    confirmed: bool

    original_query: Optional[str] = None
    goal_type: Optional[GoalType] = None
    profile: Optional[NormalizedG1Output] = None
    role: Optional[MatchedRole] = None
    targets: list[GraphTarget] = Field(default_factory=list)
    nodes: Optional[list[PreviewNode2]] = None
    edges: list[LearningPathPreviewEdge] = Field(default_factory=list)
    layer: dict[int, list[int]] = Field(default_factory=dict)
    retrieval_status: Literal["complete", "incomplete"] = "complete"
    warnings: list[str] = Field(default_factory=list)
    generator_version: Optional[str] = None

    @model_validator(mode="after")
    def check_confirmed(self):
        if self.confirmed:
            if not self.original_query or not self.original_query.strip():
                raise ValueError("original_query is required when confirming a learning path.")
            if self.goal_type is None:
                raise ValueError("goal_type is required when confirming a learning path.")
            if self.profile is None:
                raise ValueError("profile is required when confirming a learning path.")
            if not self.nodes:
                raise ValueError("Learning path must contain at least one node.")
            ids = {n.skill_id for n in self.nodes}
            for e in self.edges:
                if e.from_skill_id not in ids or e.to_skill_id not in ids:
                    raise ValueError(f"Edge {e.from_skill_id} -> {e.to_skill_id} references a skill outside the path.")
        return self


class LearningPathConfirm2Response(BaseModel):
    confirmed: Literal[True] = True
    record_id: int
    profile_id: int
    graph_id: int


# ---- form options -------------------------------------------------------

class CertificationOption(BaseModel):
    cert_id: int
    name: str
    issuer: Optional[str] = None


class TechnicalDomainOption(BaseModel):
    domain_id: int
    name: str


class LearningPathFormOptions(BaseModel):
    career_levels: list[str]
    proficiency_levels: list[str]
    certifications: list[CertificationOption]
    technical_domains: list[TechnicalDomainOption]


class LearningPathProfileResponse(BaseModel):
    """GET /learning-paths/{record_id}/profile: learner profile snapshot + generated graph info."""
    record_id: int
    profile: LearnerProfileResponse
    role_id: Optional[int] = None
    targets: list[GraphTarget] = Field(default_factory=list)
    node_states: dict[str, NodeState] = Field(default_factory=dict)
    retrieval_status: Optional[str] = None
    warnings: list[str] = Field(default_factory=list)
    generator_version: Optional[str] = None
    created_at: Optional[datetime] = None
