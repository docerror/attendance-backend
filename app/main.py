# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from contextlib import asynccontextmanager
# import logging

# from app.config import settings
# from app.database import engine, Base
# from app.routers import students, teachers, attendance, reports

# # Configure logging
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
# )
# logger = logging.getLogger(__name__)


# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     # Startup
#     logger.info("Starting up Presence API...")
#     Base.metadata.create_all(bind=engine)
#     logger.info("Database tables created")
#     yield
#     # Shutdown
#     logger.info("Shutting down Presence API...")


# app = FastAPI(
#     title="Presence API",
#     description="Smart Attendance System with Face Recognition",
#     version="1.0.0",
#     lifespan=lifespan
# )

# # CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Configure appropriately for production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )
# Base.metadata.create_all(bind=engine)
# # Include routers
# app.include_router(students.router, prefix="/api/v1")
# app.include_router(teachers.router, prefix="/api/v1")
# app.include_router(attendance.router, prefix="/api/v1")
# app.include_router(reports.router, prefix="/api/v1")


# @app.get("/")
# async def root():
#     return {
#         "app": settings.app_name,
#         "version": "1.0.0",
#         "status": "running"
#     }


# @app.get("/health")
# async def health_check():
#     return {"status": "healthy"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import engine, Base

# ✅ ADD THESE IMPORTS (CRITICAL FIX)
from app.models import student, teacher, attendance  # 👈 THIS LINE FIXES EVERYTHING

from app.routers import students, teachers, attendance, reports

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Presence API...")

    # ✅ CREATE TABLES AFTER MODELS LOADED
    Base.metadata.create_all(bind=engine)

    logger.info("Database tables created")
    yield

    logger.info("Shutting down Presence API...")


app = FastAPI(
    title="Presence API",
    description="Smart Attendance System with Face Recognition",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ❌ REMOVE THIS (duplicate)
# Base.metadata.create_all(bind=engine)

# Routers
app.include_router(students.router, prefix="/api/v1")
app.include_router(teachers.router, prefix="/api/v1")
app.include_router(attendance.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}