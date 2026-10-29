from pydantic import BaseModel, ConfigDict

class SkillRequestResponse(BaseModel):
    skill: str
    skill_id: int
    model_config = ConfigDict(from_attributes=True)