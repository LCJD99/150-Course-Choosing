"""
Admin API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from database import get_db
from models import Course, CourseGrade, Student, ImportLog
from schemas import SelectionOpenRequest
from services.auth import hash_id_card, get_id_card_last4
import pandas as pd
from typing import List, Dict
from datetime import datetime


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/import/courses")
async def import_courses(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import courses from CSV file"""
    try:
        df = pd.read_csv(file.file)
        
        required_columns = ['course_id', 'course_name', 'teacher', 'capacity', 'day']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required column: {col}",
                )
        
        success_count = 0
        error_report = []
        
        for index, row in df.iterrows():
            try:
                if row['capacity'] <= 0:
                    raise ValueError("Capacity must be positive")
                
                if row['day'] not in [1, 3, 4, 5]:
                    raise ValueError("Day must be 1, 3, 4, or 5")
                
                existing_course = db.query(Course).filter(Course.course_id == row['course_id']).first()
                if existing_course:
                    error_report.append(f"Row {index + 1}: Course ID {row['course_id']} already exists")
                    continue
                
                new_course = Course(
                    course_id=str(row['course_id']),
                    course_name=str(row['course_name']),
                    teacher=str(row['teacher']),
                    capacity=int(row['capacity']),
                    day=int(row['day'])
                )
                db.add(new_course)
                success_count += 1
                
            except Exception as e:
                error_report.append(f"Row {index + 1}: {str(e)}")
        
        db.commit()
        
        log = ImportLog(
            import_type="courses",
            total_rows=len(df),
            success_rows=success_count,
            failed_rows=len(df) - success_count,
            error_report="\n".join(error_report) if error_report else None
        )
        db.add(log)
        db.commit()
        
        return {
            "total_rows": len(df),
            "success_rows": success_count,
            "failed_rows": len(df) - success_count,
            "errors": error_report
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}",
        )


@router.post("/import/course-grades")
async def import_course_grades(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import course grades from CSV file"""
    try:
        df = pd.read_csv(file.file)
        
        required_columns = ['course_id', 'grade']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required column: {col}",
                )
        
        success_count = 0
        error_report = []
        
        for index, row in df.iterrows():
            try:
                course = db.query(Course).filter(Course.course_id == str(row['course_id'])).first()
                if not course:
                    raise ValueError(f"Course {row['course_id']} not found")
                
                existing_grade = db.query(CourseGrade).filter(
                    CourseGrade.course_id == course.id,
                    CourseGrade.grade == int(row['grade'])
                ).first()
                
                if existing_grade:
                    error_report.append(f"Row {index + 1}: Course {row['course_id']} for grade {row['grade']} already exists")
                    continue
                
                new_course_grade = CourseGrade(
                    course_id=course.id,
                    grade=int(row['grade'])
                )
                db.add(new_course_grade)
                success_count += 1
                
            except Exception as e:
                error_report.append(f"Row {index + 1}: {str(e)}")
        
        db.commit()
        
        log = ImportLog(
            import_type="course_grades",
            total_rows=len(df),
            success_rows=success_count,
            failed_rows=len(df) - success_count,
            error_report="\n".join(error_report) if error_report else None
        )
        db.add(log)
        db.commit()
        
        return {
            "total_rows": len(df),
            "success_rows": success_count,
            "failed_rows": len(df) - success_count,
            "errors": error_report
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}",
        )


@router.post("/import/students")
async def import_students(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import students from CSV file"""
    try:
        df = pd.read_csv(file.file)
        
        required_columns = ['name', 'class_name', 'grade', 'id_card']
        for col in required_columns:
            if col not in df.columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required column: {col}",
                )
        
        success_count = 0
        error_report = []
        
        for index, row in df.iterrows():
            try:
                id_card_hash = hash_id_card(str(row['id_card']))
                id_card_last4 = get_id_card_last4(str(row['id_card']))
                
                existing_student = db.query(Student).filter(
                    Student.name == str(row['name']),
                    Student.id_card_hash == id_card_hash
                ).first()
                
                if existing_student:
                    error_report.append(f"Row {index + 1}: Student {row['name']} with ID card already exists")
                    continue
                
                new_student = Student(
                    name=str(row['name']),
                    class_name=str(row['class_name']),
                    grade=int(row['grade']),
                    id_card_hash=id_card_hash,
                    id_card_last4=id_card_last4
                )
                db.add(new_student)
                success_count += 1
                
            except Exception as e:
                error_report.append(f"Row {index + 1}: {str(e)}")
        
        db.commit()
        
        log = ImportLog(
            import_type="students",
            total_rows=len(df),
            success_rows=success_count,
            failed_rows=len(df) - success_count,
            error_report="\n".join(error_report) if error_report else None
        )
        db.add(log)
        db.commit()
        
        return {
            "total_rows": len(df),
            "success_rows": success_count,
            "failed_rows": len(df) - success_count,
            "errors": error_report
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}",
        )


@router.put("/settings/selection-open")
async def set_selection_open(request: SelectionOpenRequest, db: Session = Depends(get_db)):
    """Enable or disable course selection"""
    from models import SystemSetting
    
    setting = db.query(SystemSetting).filter(SystemSetting.key == "course_selection_open").first()
    if not setting:
        setting = SystemSetting(key="course_selection_open", value=str(request.open).lower())
        db.add(setting)
    else:
        setting.value = str(request.open).lower()
    
    db.commit()
    return {"message": f"Course selection {'opened' if request.open else 'closed'}"}


@router.get("/settings/selection-open")
async def get_selection_open(db: Session = Depends(get_db)):
    """Get current course selection status"""
    from models import SystemSetting
    
    setting = db.query(SystemSetting).filter(SystemSetting.key == "course_selection_open").first()
    return {"open": setting.value.lower() == "true" if setting else False}
