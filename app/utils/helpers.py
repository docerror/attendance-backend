from datetime import date

def attendance_already_marked(db, student_id):
    from ..models.attendance import Attendance
    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.date == date.today()
    ).first()
    return existing is not None
