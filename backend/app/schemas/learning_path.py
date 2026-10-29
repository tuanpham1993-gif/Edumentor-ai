from pydantic import BaseModel, ConfigDict
from typing import Literal

class SkillSummary(BaseModel):
    skill_id: int
    skill: str
    model_config = ConfigDict(from_attributes=True)
#**************************************************

######################################################
class LearningPathNodeBase(BaseModel):
    skill_id: int
    node_role: str | None = None
    is_target: bool
    added_by: Literal["system", "user"]
    is_required: bool
    display_order: int

class LearningPathNodeCreate(LearningPathNodeBase): pass

class LearningPathNodeResponse(LearningPathNodeBase):
    path_id: int
    skill: SkillSummary
    model_config = ConfigDict(from_attributes=True)

######################################################
class LearningPathEdgeBase(BaseModel):
    from_skill_id: int
    to_skill_id: int
    relation_type: Literal["prerequisite", "related", "extension"]

class LearningPathEdgeCreate(LearningPathEdgeBase): pass

class LearningPathEdgeResponse(LearningPathEdgeBase):
    path_id: int
    from_skill: SkillSummary
    to_skill: SkillSummary
    model_config = ConfigDict(from_attributes=True)
######################################################
class LearningPathBase(BaseModel):
    student_id: int
    original_query: str
    goal_type: Literal["career", "project"]
    status: Literal["completed", "ongoing", "abandoned"]

class LearningPathCreate(LearningPathBase): pass

class LearningPathResponse(LearningPathBase):
    record_id: int
    nodes: list[LearningPathNodeResponse]
    edges: list[LearningPathEdgeResponse]
    model_config = ConfigDict(from_attributes=True)


"""
sample output
{
  "record_id": 1,
  "student_id": 1,
  "original_query": "I want to become a backend developer using Python.",
  "goal_type": "career",
  "status": "completed",
  "nodes": [
    {
      "path_id": 1,
      "skill_id": 26,
      "node_role": "prerequisite",
      "is_target": false,
      "added_by": "system",
      "is_required": true,
      "display_order": 2000,
      "skill": {
        "skill_id": 26,
        "skill": "Computer Programming"
      }
    }
  ],
  "edges": []
}

"""