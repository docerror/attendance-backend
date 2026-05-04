from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta

from app.database import get_db
from app.models.teacher import Teacher
from app.schemas.teacher import TeacherCreate, TeacherLogin, TeacherResponse, Token
from app.utils.auth import get_password_hash, verify_password, create_access_token, get_current_teacher
from app.config import settings

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.post("/register", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
async def register_teacher(
    teacher_data: TeacherCreate,
    db: Session = Depends(get_db)
):
    try:
        print("🔥 RECEIVED DATA:", teacher_data.dict())

        existing = db.query(Teacher).filter(Teacher.email == teacher_data.email).first()

        if existing:
            raise HTTPException(
                status_code=400,
                detail="A teacher with this email already exists"
            )

        teacher = Teacher(
            name=teacher_data.name,
            email=teacher_data.email,
            password_hash=get_password_hash(teacher_data.password),
            branch=teacher_data.branch,
            semester=teacher_data.semester
        )

        db.add(teacher)
        db.commit()
        db.refresh(teacher)

        return teacher

    except Exception as e:
        print("❌ BACKEND ERROR:", str(e))  # 🔥 THIS WILL SHOW REAL ERROR
        raise HTTPException(status_code=500, detail=str(e))
    # Create teacher
    teacher = Teacher(
        name=teacher_data.name,
        email=teacher_data.email,
        password_hash=get_password_hash(teacher_data.password),
        branch=teacher_data.branch,
        semester=teacher_data.semester
    )
    
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    
    return teacher


@router.post("/login", response_model=Token)
async def login_teacher(
    credentials: TeacherLogin,
    db: Session = Depends(get_db)
):
    """Authenticate a teacher and return a JWT token."""
    
    teacher = db.query(Teacher).filter(Teacher.email == credentials.email).first()
    
    if not teacher or not verify_password(credentials.password, teacher.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(
        data={"sub": teacher.id, "email": teacher.email},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes)
    )
    
    return Token(access_token=access_token)


@router.get("/me", response_model=TeacherResponse)
async def get_current_teacher_info(
    teacher: Teacher = Depends(get_current_teacher)
):
    """Get the current authenticated teacher's information."""
    return teacher


@router.put("/me", response_model=TeacherResponse)
async def update_teacher(
    name: str = None,
    branch: str = None,
    semester: int = None,
    db: Session = Depends(get_db),
    teacher: Teacher = Depends(get_current_teacher)
):
    """Update the current teacher's information."""
    
    if name:
        teacher.name = name
    if branch:
        teacher.branch = branch
    if semester:
        teacher.semester = semester
    
    db.commit()
    db.refresh(teacher)
    
    return teacher
