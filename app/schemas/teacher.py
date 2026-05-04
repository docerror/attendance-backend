from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class TeacherBase(BaseModel):
    name: str
    email: EmailStr
    branch: str
    semester: int


class TeacherCreate(TeacherBase):
    password: str = Field(
        ...,
        min_length=6,
        max_length=72,  # 🔥 bcrypt limit
        description="Password must be between 6 and 72 characters"
    )

class TeacherLogin(BaseModel):
    email: EmailStr
    password: str


class TeacherResponse(TeacherBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    teacher_id: Optional[int] = None
    email: Optional[str] = None
