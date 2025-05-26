from typing import Optional
from pydantic import BaseModel, Field

class AuthForm(BaseModel):
    identifier: str
    password: str
    device: Optional[str] = "unknown"
    ip_address: Optional[str] = "unknown"
    remember_me: Optional[bool] = Field(False)
