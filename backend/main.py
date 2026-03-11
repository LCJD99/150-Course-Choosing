"""
Course Selection System - Main Application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import sqlite3
from pathlib import Path
from database import Base, engine
import models  # noqa: F401
from api.student import router as student_router
from api.admin import router as admin_router


DB_PATH = Path(__file__).parent / "data" / "course_selection.db"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Course Selection System",
    description="150团中学兴趣班选课系统",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(student_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    return {"message": "Course Selection System API", "status": "running"}
