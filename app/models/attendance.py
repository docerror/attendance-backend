from sqlalchemy import Column, Integer, String, DateTime, Date, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Attendance(Base):
    __tablename__ = "attendances"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id", ondelete="SET NULL"), nullable=True)
    date = Column(Date, nullable=False, index=True)
    subject = Column(String(100), nullable=True)
    status = Column(String(20), default="absent")  # present, absent
    marked_manually = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    student = relationship("Student", back_populates="attendances")
    teacher = relationship("Teacher", back_populates="attendances")
    
    __table_args__ = (
        UniqueConstraint('student_id', 'date', 'subject', name='uq_student_date_subject'),
        Index('idx_attendance_date_status', 'date', 'status'),
    )
