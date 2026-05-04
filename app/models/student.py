from sqlalchemy import Column, Integer, String, DateTime, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Student(Base):
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), nullable=False)
    roll_number = Column(String(20), unique=True, nullable=False, index=True)
    branch = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    semester = Column(Integer, nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    profile_image_url = Column(Text, nullable=True)
    face_encoding = Column(Text, nullable=True)  # JSON serialized face encoding
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    attendances = relationship("Attendance", back_populates="student")
    
    __table_args__ = (
        Index('idx_student_branch_semester', 'branch', 'semester'),
    )
