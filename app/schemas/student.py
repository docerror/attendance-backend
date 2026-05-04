from pydantic import BaseModel, EmailStr, field_validator
from datetime import datetime
from typing import Optional
import re


class StudentBase(BaseModel):
    full_name: str
    roll_number: str
    branch: str
    year: int
    semester: int
    email: EmailStr
    
    @field_validator('roll_number')
    @classmethod
    def validate_roll_number(cls, v):
        if not re.match(r'^\d{2}/\d{3}$', v):
            raise ValueError('Roll number must be in format YY/XXX (e.g., 24/001)')
        return v
    
    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        if v < 1 or v > 5:
            raise ValueError('Year must be between 1 and 5')
        return v
    
    @field_validator('semester')
    @classmethod
    def validate_semester(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Semester must be between 1 and 10')
        return v


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    full_name: Optional[str] = None
    branch: Optional[str] = None
    year: Optional[int] = None
    semester: Optional[int] = None
    email: Optional[EmailStr] = None


class StudentResponse(StudentBase):
    id: int
    profile_image_url: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class StudentAttendanceStats(BaseModel):
    student_id: int
    full_name: str
    roll_number: str
    branch: str
    semester: int
    total_classes: int
    present_days: int
    absent_days: int
    attendance_percentage: float
