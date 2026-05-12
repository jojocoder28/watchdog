from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime
from models.user import UserRole

class UserBase(BaseModel):
    email: EmailStr
    role: UserRole = UserRole.SRE

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)
