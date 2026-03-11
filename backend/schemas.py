"""
Pydantic schemas for API
"""
from pydantic import BaseModel
from typing import Optional


class StudentLogin(BaseModel):
    name: str
    id_card: str


class StudentResponse(BaseModel):
    id: int
    name: str
    class_name: str
    grade: int
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    student: StudentResponse
    course_selection_open: bool


class CourseResponse(BaseModel):
    id: int
    course_id: str
    course_name: str
    teacher: str
    capacity: int
    day: int
    remaining: int
    is_selected: bool = False
    bundle_id: Optional[str] = None
    bundle_size: Optional[int] = None
    is_bundle: bool = False
    
    class Config:
        from_attributes = True


class EnrollmentResponse(BaseModel):
    day: int
    course: CourseResponse
    
    class Config:
        from_attributes = True


class ProgressResponse(BaseModel):
    completed_days: int
    is_complete_4_days: bool


class CourseSelectionRequest(BaseModel):
    course_id: int


class SelectionOpenRequest(BaseModel):
    open: bool
