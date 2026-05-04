from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from sqlalchemy import func
from app.database import get_db
from app.models import Student, Teacher, Attendance
from app.schemas.attendance import (
    AttendanceResponse, AttendanceUpdate, AttendanceWithStudent,
    BulkAttendanceResult, AttendanceFilter, AttendanceStatus
)
from app.services.face_recognition import face_service
from app.services.email_service import email_service
from app.services.cloudinary_service import upload_group_image
from app.utils.auth import get_current_teacher

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("/take", response_model=BulkAttendanceResult)
async def take_attendance(
    background_tasks: BackgroundTasks,
    group_image: UploadFile = File(...),
    attendance_date: date = Form(default=None),
    subject: Optional[str] = Form(default=None),
    send_notifications: bool = Form(default=True),
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """
    Process a group photo and mark attendance using face recognition.
    """
    if attendance_date is None:
        attendance_date = date.today()
    
    # Read image bytes
    image_bytes = await group_image.read()
    
    # Process attendance using face recognition
    matched_ids, total_faces = face_service.process_attendance(
        db=db,
        image_bytes=image_bytes,
        branch=teacher.branch,
        semester=teacher.semester
    )
    
    if total_faces == 0:
        raise HTTPException(
            status_code=400,
            detail="No faces detected in the image. Please upload a clearer photo."
        )
    
    # Get all students in the class
    all_students = db.query(Student).filter(
        Student.branch == teacher.branch,
        Student.semester == teacher.semester
    ).all()
    
    if not all_students:
        raise HTTPException(
            status_code=404,
            detail="No students found for this branch and semester"
        )
    
    present_students = []
    absent_students = []
    
    for student in all_students:
        # Check if attendance already exists for this date and subject
        existing = db.query(Attendance).filter(
            Attendance.student_id == student.id,
            Attendance.date == attendance_date,
            Attendance.subject == subject
        ).first()
        
        status_value = "present" if student.id in matched_ids else "absent"
        
        if existing:
            # Update existing attendance

            existing.status = status_value
            existing.teacher_id = teacher.id
            existing.marked_manually = False
        else:
            # Create new attendance record
            attendance = Attendance(
                student_id=student.id,
                teacher_id=teacher.id,
                date=attendance_date,
                subject=subject,
                status=status_value,
                marked_manually=False
            )
            db.add(attendance)
        
        if status_value == "present":
            present_students.append(student.full_name)
        else:
            absent_students.append({
                "email": student.email,
                "name": student.full_name
            })
    
    db.commit()
    
    # Send notifications to absent students in background
    if send_notifications and absent_students:
        background_tasks.add_task(
            email_service.send_bulk_absence_notifications,
            absent_students,
            attendance_date,
            subject
        )
    
    return BulkAttendanceResult(
        date=attendance_date,
        subject=subject,
        total_students=len(all_students),
        present_count=len(present_students),
        absent_count=len(absent_students),
        recognized_students=present_students,
        unrecognized_count=total_faces - len(matched_ids)
    )


@router.get("/daily", response_model=List[AttendanceWithStudent])
async def get_daily_attendance(
    attendance_date: date = None,
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """Get attendance for a specific date."""
    if attendance_date is None:
        attendance_date = date.today()
    
    query = db.query(Attendance, Student).join(Student).filter(
        Attendance.date == attendance_date,
        Student.branch == teacher.branch,
        Student.semester == teacher.semester
    ).order_by(func.lower(Student.full_name).asc())
    #changed
    if subject:
        query = query.filter(Attendance.subject == subject)
    
    results = query.all()
    
    attendance_list = []
    for attendance, student in results:
        attendance_list.append(AttendanceWithStudent(
            id=attendance.id,
            student_id=attendance.student_id,
            date=attendance.date,
            subject=attendance.subject,
            status=attendance.status,
            teacher_id=attendance.teacher_id,
            marked_manually=attendance.marked_manually,
            created_at=attendance.created_at,
            student_name=student.full_name,
            roll_number=student.roll_number,
            branch=student.branch,
            semester=student.semester
        ))
    
    return attendance_list


@router.get("/overall", response_model=List[AttendanceWithStudent])
async def get_overall_attendance(
    filters: AttendanceFilter = Depends(),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """Get overall attendance with filters."""
    
    query = db.query(Attendance, Student).join(Student).filter(
        Student.branch == teacher.branch,
        Student.semester == teacher.semester
    )
    
    if filters.date_from:
        query = query.filter(Attendance.date >= filters.date_from)
    if filters.date_to:
        query = query.filter(Attendance.date <= filters.date_to)
    if filters.subject:
        query = query.filter(Attendance.subject == filters.subject)
    if filters.status:
        query = query.filter(Attendance.status == filters.status.value)
    
    results = query.order_by(Attendance.date.desc(),func.lower(Student.full_name).asc()
    ).offset(skip).limit(limit).all()
    #results = query.order_by(Attendance.date.desc()).offset(skip).limit(limit).all()
    
    attendance_list = []
    for attendance, student in results:
        attendance_list.append(AttendanceWithStudent(
            id=attendance.id,
            student_id=attendance.student_id,
            date=attendance.date,
            subject=attendance.subject,
            status=attendance.status,
            teacher_id=attendance.teacher_id,
            marked_manually=attendance.marked_manually,
            created_at=attendance.created_at,
            student_name=student.full_name,
            roll_number=student.roll_number,
            branch=student.branch,
            semester=student.semester
        ))
    
    return attendance_list


@router.put("/{attendance_id}", response_model=AttendanceResponse)
async def update_attendance(
    attendance_id: int,
    update_data: AttendanceUpdate,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """Manually update attendance status."""
    
    attendance = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    
    if not attendance:
        raise HTTPException(status_code=404, detail="Attendance record not found")
    
    # Verify the student belongs to the teacher's class
    student = db.query(Student).filter(Student.id == attendance.student_id).first()
    if student.branch != teacher.branch or student.semester != teacher.semester:
        raise HTTPException(
            status_code=403,
            detail="You can only modify attendance for students in your class"
        )
    
    attendance.status = update_data.status.value
    attendance.marked_manually = True
    attendance.teacher_id = teacher.id
    
    db.commit()
    db.refresh(attendance)
    
    return attendance


@router.post("/manual", response_model=AttendanceResponse)
async def create_manual_attendance(
    student_id: int = Form(...),
    attendance_date: date = Form(...),
    subject: Optional[str] = Form(default=None),
    status: AttendanceStatus = Form(...),
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """Manually create an attendance record."""
    
    # Verify student exists and belongs to teacher's class
    student = db.query(Student).filter(Student.id == student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    if student.branch != teacher.branch or student.semester != teacher.semester:
        raise HTTPException(
            status_code=403,
            detail="You can only mark attendance for students in your class"
        )
    
    # Check for existing record
    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == attendance_date,
        Attendance.subject == subject
    ).first()
    
    if existing:
        # Update existing
        existing.status = status.value
        existing.marked_manually = True
        existing.teacher_id = teacher.id
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new record
    attendance = Attendance(
        student_id=student_id,
        teacher_id=teacher.id,
        date=attendance_date,
        subject=subject,
        status=status.value,
        marked_manually=True
    )
    
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    
    return attendance


@router.post("/notify-absent")
async def send_absence_notifications(
    background_tasks: BackgroundTasks,
    attendance_date: date = Form(...),
    subject: Optional[str] = Form(default=None),
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """Send email notifications to all absent students for a given date."""
    
    query = db.query(Student).join(Attendance).filter(
        Attendance.date == attendance_date,
        Attendance.status == "absent",
        Student.branch == teacher.branch,
        Student.semester == teacher.semester
    )
    
    if subject:
        query = query.filter(Attendance.subject == subject)
    
    absent_students = query.all()
    
    if not absent_students:
        return {"message": "No absent students found for this date"}
    
    students_data = [{"email": s.email, "name": s.full_name} for s in absent_students]
    
    background_tasks.add_task(
        email_service.send_bulk_absence_notifications,
        students_data,
        attendance_date,
        subject
    )
    
    return {
        "message": f"Sending notifications to {len(absent_students)} students",
        "students": [s.full_name for s in absent_students]
    }
