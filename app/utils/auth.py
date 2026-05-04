# from datetime import datetime, timedelta
# from typing import Optional
# from jose import JWTError, jwt
# from passlib.context import CryptContext
# from fastapi import Depends, HTTPException, status
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from sqlalchemy.orm import Session
# from app.config import settings
# from app.database import get_db
# from app.models.teacher import Teacher
# from app.schemas.teacher import TokenData

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# security = HTTPBearer()


# # def verify_password(plain_password: str, hashed_password: str) -> bool:
# #     return pwd_context.verify(plain_password, hashed_password)


# # def get_password_hash(password: str) -> str:
# #     return pwd_context.hash(password)

# ##chat gpt code below


# def get_password_hash(password: str) -> str:
#     return pwd_context.hash(password)

# def verify_password(plain_password: str, hashed_password: str) -> bool:
#     return pwd_context.verify(plain_password, hashed_password)





# def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
#     return encoded_jwt


# def decode_token(token: str) -> TokenData:
#     try:
#         payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
#         teacher_id: int = payload.get("sub")
#         email: str = payload.get("email")
#         if teacher_id is None:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token"
#             )
#         return TokenData(teacher_id=teacher_id, email=email)
#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token"
#         )


# def get_current_teacher(
#     credentials: HTTPAuthorizationCredentials = Depends(security),
#     db: Session = Depends(get_db)
# ) -> Teacher:
#     token = credentials.credentials
#     token_data = decode_token(token)
#     teacher = db.query(Teacher).filter(Teacher.id == token_data.teacher_id).first()
#     if teacher is None:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Teacher not found"
#         )
#     return teacher
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models.teacher import Teacher
from app.schemas.teacher import TokenData


# ================= PASSWORD =================

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# ================= SECURITY =================

security = HTTPBearer(auto_error=False)


# ================= JWT =================

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()

    # 🔥 FIX: ensure "sub" is STRING
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    expire = datetime.utcnow() + (
        expires_delta if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )

        teacher_id = payload.get("sub")
        email = payload.get("email")

        if teacher_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # 🔥 FIX: convert string → int safely
        try:
            teacher_id = int(teacher_id)
        except:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return TokenData(
            teacher_id=teacher_id,
            email=email
        )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


# ================= CURRENT USER =================

def get_current_teacher(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Teacher:

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = credentials.credentials
    token_data = decode_token(token)

    teacher = db.query(Teacher).filter(
        Teacher.id == token_data.teacher_id
    ).first()

    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Teacher not found"
        )

    return teacher