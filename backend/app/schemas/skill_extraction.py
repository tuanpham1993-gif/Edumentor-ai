from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Literal


class SkillExtractionRequest(BaseModel):
    prompt: str = Field(..., min_length=3, description="User's learning goal")
    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, value: str) -> str:
        value = value.strip()
        if not value: raise ValueError("Learning goal cannot be empty.")
        return value


class SkillExtractionResponse(BaseModel):
    status: Literal["success","needs_clarification","unsupported"]
    goal_type: Literal["career", "project"] | None
    skills: list[str]
    message: str | None
    