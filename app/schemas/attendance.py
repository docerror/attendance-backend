from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List
from enum import Enum


class AttendanceStatus(str, Enum):
    present = "present"
    absent = "absent"


class AttendanceBase(BaseModel):
    student_id: int
    date: date
    subject: Optional[str] = None
    status: AttendanceStatus = AttendanceStatus.absent


class AttendanceCreate(AttendanceBase):
    pass


class AttendanceUpdate(BaseModel):
    status: AttendanceStatus
    marked_manually: bool = True


class AttendanceResponse(AttendanceBase):
    id: int
    teacher_id: Optional[int] = None
    marked_manually: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class AttendanceWithStudent(AttendanceResponse):
    student_name: str
    roll_number: str
    branch: str
    semester: int


class BulkAttendanceResult(BaseModel):
    date: date
    subject: Optional[str]
    total_students: int
    present_count: int
    absent_count: int
    recognized_students: List[str]
    unrecognized_count: int


class AttendanceFilter(BaseModel):
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    branch: Optional[str] = None
    semester: Optional[int] = None
    subject: Optional[str] = None
    status: Optional[AttendanceStatus] = None
