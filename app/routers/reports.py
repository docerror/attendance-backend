from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import io

from app.database import get_db
from app.models import Teacher
from app.schemas.student import StudentAttendanceStats
from app.services.report_service import report_service
from app.utils.auth import get_current_teacher

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/stats", response_model=List[StudentAttendanceStats])
async def get_attendance_stats(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """Get attendance statistics for all students in the teacher's class."""
    
    stats = report_service.generate_attendance_stats(
        db=db,
        branch=teacher.branch,
        semester=teacher.semester,
        date_from=date_from,
        date_to=date_to,
        subject=subject
    )
    
    return stats


@router.get("/export/excel")
async def export_excel_report(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """Export attendance report as Excel file."""
    
    stats = report_service.generate_attendance_stats(
        db=db,
        branch=teacher.branch,
        semester=teacher.semester,
        date_from=date_from,
        date_to=date_to,
        subject=subject
    )
    
    title = f"Attendance Report - {teacher.branch} Semester {teacher.semester}"
    if date_from and date_to:
        title += f" ({date_from} to {date_to})"
    
    excel_bytes = report_service.generate_excel_report(stats, title)
    
    filename = f"attendance_report_{teacher.branch}_sem{teacher.semester}.xlsx"
    
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


@router.get("/export/pdf")
async def export_pdf_report(
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    subject: Optional[str] = None,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """Export attendance report as PDF file."""
    
    stats = report_service.generate_attendance_stats(
        db=db,
        branch=teacher.branch,
        semester=teacher.semester,
        date_from=date_from,
        date_to=date_to,
        subject=subject
    )
    
    title = f"Attendance Report - {teacher.branch} Semester {teacher.semester}"
    if date_from and date_to:
        title += f" ({date_from} to {date_to})"
    
    pdf_bytes = report_service.generate_pdf_report(stats, title)
    
    filename = f"attendance_report_{teacher.branch}_sem{teacher.semester}.pdf"
    
    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
