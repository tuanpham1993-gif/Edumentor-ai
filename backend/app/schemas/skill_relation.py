
from typing import Literal
from pydantic import BaseModel, ConfigDict


RelationType = Literal["prerequisite","related","extension"]


class SkillRelationBase(BaseModel):
    from_skill_id: int
    to_skill_id: int
    relation_type: RelationType


class SkillRelationCreate(SkillRelationBase):
    pass


class SkillRelationResponse(SkillRelationBase):
    model_config = ConfigDict(from_attributes=True)
