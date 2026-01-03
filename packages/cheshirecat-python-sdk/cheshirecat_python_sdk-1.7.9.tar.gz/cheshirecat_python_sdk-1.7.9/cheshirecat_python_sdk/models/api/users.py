from typing import Dict, List
from pydantic import BaseModel


class UserOutput(BaseModel):
    username: str
    permissions: Dict[str, List[str]]
    id: str
    created_at: float | None = None
    updated_at: float | None = None
