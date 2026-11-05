from datetime import datetime
from pydantic import BaseModel, ConfigDict

class UserMe(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    user_id: int
    full_name: str
    email: str
    role: str
    avatar_url: str | None = None
    created_at: datetime