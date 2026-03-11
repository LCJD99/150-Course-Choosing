"""
Student API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database import get_db
from models import Student, Course, CourseGrade, Enrollment, SystemSetting
from schemas import StudentLogin, StudentResponse, Token, CourseResponse, EnrollmentResponse, ProgressResponse, CourseSelectionRequest
from services.auth import hash_id_card, get_id_card_last4, create_access_token, verify_token
from typing import List, Optional


router = APIRouter(prefix="/api/student", tags=["student"])
security = HTTPBearer()


def get_current_student(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)) -> Student:
    """Get current student from token"""
    token = credentials.credentials
    payload = verify_token(token)
    student_id = payload.get("sub")
    if student_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    student = db.query(Student).filter(Student.id == student_id).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Student not found",
        )
    return student


def is_course_selection_open(db: Session) -> bool:
    """Check if course selection is open"""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "course_selection_open").first()
    if setting is None:
        return False
    return setting.value.lower() == "true"


@router.post("/login", response_model=Token)
async def student_login(login_data: StudentLogin, db: Session = Depends(get_db)):
    """Student login with name and ID card"""
    id_card_hash = hash_id_card(login_data.id_card)
    student = db.query(Student).filter(
        Student.name == login_data.name,
        Student.id_card_hash == id_card_hash
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid name or ID card",
        )
    
    access_token = create_access_token(data={"sub": str(student.id)})
    course_selection_open = is_course_selection_open(db)
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        student=StudentResponse.model_validate(student),
        course_selection_open=course_selection_open
    )


@router.get("/courses", response_model=List[CourseResponse])
async def get_courses(
    day: int,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get available courses for a specific day"""
    
    if day not in [1, 3, 4, 5]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid day. Only 1, 3, 4, 5 are allowed",
        )
    
    courses = db.query(Course).filter(
        Course.day == day,
        Course.is_active == True
    ).join(CourseGrade).filter(
        CourseGrade.grade == student.grade
    ).all()
    
    result = []
    for course in courses:
        enrolled_count = db.query(Enrollment).filter(
            Enrollment.course_id == course.id,
            Enrollment.status == "CONFIRMED"
        ).count()
        remaining = course.capacity - enrolled_count
        
        existing_enrollment = db.query(Enrollment).filter(
            Enrollment.student_id == student.id,
            Enrollment.day == day
        ).first()
        
        is_selected = existing_enrollment and existing_enrollment.course_id == course.id
        
        course_data = CourseResponse(
            id=course.id,
            course_id=course.course_id,
            course_name=course.course_name,
            teacher=course.teacher,
            capacity=course.capacity,
            day=course.day,
            remaining=remaining,
            is_selected=is_selected
        )
        result.append(course_data)
    
    return result


@router.get("/selections", response_model=List[EnrollmentResponse])
async def get_selections(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's current selections for all days"""
    
    enrollments = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.status == "CONFIRMED"
    ).all()
    
    result = []
    for enrollment in enrollments:
        course = db.query(Course).filter(Course.id == enrollment.course_id).first()
        enrolled_count = db.query(Enrollment).filter(
            Enrollment.course_id == course.id,
            Enrollment.status == "CONFIRMED"
        ).count()
        remaining = course.capacity - enrolled_count
        
        course_data = CourseResponse(
            id=course.id,
            course_id=course.course_id,
            course_name=course.course_name,
            teacher=course.teacher,
            capacity=course.capacity,
            day=course.day,
            remaining=remaining,
            is_selected=True
        )
        
        enrollment_data = EnrollmentResponse(
            day=enrollment.day,
            course=course_data
        )
        result.append(enrollment_data)
    
    return result


@router.get("/progress", response_model=ProgressResponse)
async def get_progress(
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's selection progress"""
    
    completed_count = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.status == "CONFIRMED"
    ).count()
    
    return ProgressResponse(
        completed_days=completed_count,
        is_complete_4_days=completed_count >= 4
    )


@router.put("/selections/{day}")
async def update_selection(
    day: int,
    request: CourseSelectionRequest,
    student: Student = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Select or replace a course for a specific day"""
    if not is_course_selection_open(db):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Course selection is closed",
        )
    
    if day not in [1, 3, 4, 5]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid day. Only 1, 3, 4, 5 are allowed",
        )
    
    course = db.query(Course).filter(Course.id == request.course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )
    
    if course.day != day:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Course day does not match requested day",
        )
    
    course_grade = db.query(CourseGrade).filter(
        CourseGrade.course_id == course.id,
        CourseGrade.grade == student.grade
    ).first()
    if not course_grade:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Course not available for your grade",
        )
    
    enrolled_count = db.query(Enrollment).filter(
        Enrollment.course_id == course.id,
        Enrollment.status == "CONFIRMED"
    ).count()
    
    if enrolled_count >= course.capacity:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Course is full",
        )
    
    existing_enrollment = db.query(Enrollment).filter(
        Enrollment.student_id == student.id,
        Enrollment.day == day
    ).first()
    
    if existing_enrollment:
        existing_enrollment.course_id = course.id
        existing_enrollment.status = "CONFIRMED"
    else:
        new_enrollment = Enrollment(
            student_id=student.id,
            day=day,
            course_id=course.id,
            status="CONFIRMED"
        )
        db.add(new_enrollment)
    
    db.commit()
    return {"message": "Course selected successfully"}
