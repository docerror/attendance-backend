from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db
from app.models.student import Student
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.services.cloudinary_service import upload_image
from app.services.face_recognition import face_service
from app.utils.auth import get_current_teacher
from sqlalchemy import func
router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def register_student(
    full_name: str = Form(...),
    roll_number: str = Form(...),
    branch: str = Form(...),
    year: int = Form(...),
    semester: int = Form(...),
    email: str = Form(...),
    profile_image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Register a new student with profile image."""
    
    # Validate roll number format
    import re
    if not re.match(r'^\d{2}/\d{3}$', roll_number):
        raise HTTPException(
            status_code=400, 
            detail="Roll number must be in format YY/XXX (e.g., 24/001)"
        )
    
    # Check if student already exists
    existing = db.query(Student).filter(
        (Student.roll_number == roll_number) | (Student.email == email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Student with this roll number or email already exists"
        )
    
    # Upload image to Cloudinary
    image_url = await upload_image(profile_image, folder="presence/students")
    
    # Extract face encoding
    face_encoding = face_service.extract_face_encoding(image_url)
    
    if face_encoding is None:
        raise HTTPException(
            status_code=400,
            detail="No face detected in the uploaded image. Please upload a clear photo with your face visible."
        )
    
    # Create student
    student = Student(
        full_name=full_name,
        roll_number=roll_number,
        branch=branch,
        year=year,
        semester=semester,
        email=email,
        profile_image_url=image_url,
        face_encoding=json.dumps(face_encoding)
    )
    
    db.add(student)
    db.commit()
    db.refresh(student)
    
    return student


@router.get("/", response_model=List[StudentResponse])
async def get_students(
    branch: str = None,
    semester: int = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_teacher)
):
    """Get all students with optional filters."""
    query = db.query(Student)
    
    if branch:
        query = query.filter(Student.branch == branch)
    if semester:
        query = query.filter(Student.semester == semester)

    query = query.order_by(func.lower(Student.full_name).asc())
    students = query.offset(skip).limit(limit).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: int,
    db: Session = Depends(get_db)
):
    """Get a specific student by ID."""
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return student

@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: int,
    update_data: StudentUpdate,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_teacher)
):
    """Update student information."""
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(student, key, value)
    
    db.commit()
    db.refresh(student)
    
    return student


@router.put("/{student_id}/photo", response_model=StudentResponse)
async def update_student_photo(
    student_id: int,
    profile_image: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: str = Depends(get_current_teacher)
):
    """Update student's profile photo and face encoding."""
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Upload new image
    image_url = await upload_image(profile_image, folder="presence/students")
    
    # Extract new face encoding
    face_encoding = face_service.extract_face_encoding(image_url)
    
    if face_encoding is None:
        raise HTTPException(
            status_code=400,
            detail="No face detected in the uploaded image"
        )
    
    student.profile_image_url = image_url
    student.face_encoding = json.dumps(face_encoding)
    
    db.commit()
    db.refresh(student)
    
    return student


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_student(
    student_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(get_current_teacher)
):
    """Delete a student."""
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    db.delete(student)
    db.commit()
