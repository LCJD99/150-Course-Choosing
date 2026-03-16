"""
Admin API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from sqlalchemy.orm import Session
from database import get_db
from models import Course, CourseGrade, Student, ImportLog, SystemSetting, Enrollment
from schemas import SelectionOpenRequest, AdminMasterKeyRequest, CourseStatusRequest
from services.auth import hash_id_card, get_id_card_last4
import pandas as pd
from typing import List, Dict
from datetime import datetime
import hashlib


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/courses")
async def get_admin_courses(db: Session = Depends(get_db)):
    """Get all courses with enrollment statistics for admin view"""
    courses = db.query(Course).order_by(Course.day, Course.course_id).all()

    result = []
    for course in courses:
        enrolled_count = db.query(Enrollment).filter(
            Enrollment.course_id == course.id,
            Enrollment.status == "CONFIRMED"
        ).count()
        remaining = max(course.capacity - enrolled_count, 0)
        grades = db.query(CourseGrade.grade).filter(CourseGrade.course_id == course.id).all()
        grade_values = [grade for (grade,) in grades]

        result.append({
            "id": course.id,
            "course_id": course.course_id,
            "course_name": course.course_name,
            "teacher": course.teacher,
            "capacity": course.capacity,
            "day": course.day,
            "bundle_id": course.bundle_id,
            "is_active": course.is_active,
            "enrolled_count": enrolled_count,
            "remaining": remaining,
            "fill_percentage": int((enrolled_count / course.capacity) * 100) if course.capacity > 0 else 0,
            "grades": grade_values,
        })

    return result


@router.get("/stats")
async def get_admin_stats(db: Session = Depends(get_db)):
    """Get dashboard statistics for admin view"""
    courses = db.query(Course).all()
    students_count = db.query(Student).count()

    total_confirmed = db.query(Enrollment).filter(Enrollment.status == "CONFIRMED").count()
    completed_students = db.query(Enrollment.student_id).filter(
        Enrollment.status == "CONFIRMED"
    ).distinct().all()
    completed_students_count = len([row[0] for row in completed_students])

    day_stats = []
    for day in [1, 3, 4, 5]:
        day_count = db.query(Enrollment).filter(
            Enrollment.day == day,
            Enrollment.status == "CONFIRMED"
        ).count()
        denominator = students_count if students_count > 0 else 1
        day_stats.append({
            "day": day,
            "count": day_count,
            "percentage": min(int((day_count / denominator) * 100), 100),
        })

    top_courses = []
    for course in courses:
        enrolled = db.query(Enrollment).filter(
            Enrollment.course_id == course.id,
            Enrollment.status == "CONFIRMED"
        ).count()
        fill_rate = int((enrolled / course.capacity) * 100) if course.capacity > 0 else 0
        top_courses.append({
            "id": course.id,
            "course_name": course.course_name,
            "teacher": course.teacher,
            "day": course.day,
            "enrolled": enrolled,
            "capacity": course.capacity,
            "fill_rate": fill_rate,
        })

    top_courses.sort(key=lambda item: item["fill_rate"], reverse=True)

    return {
        "total_courses": len(courses),
        "total_students": students_count,
        "completed_selections": completed_students_count,
        "completion_rate": int((completed_students_count / students_count) * 100) if students_count > 0 else 0,
        "day_stats": day_stats,
        "top_courses": top_courses[:5],
        "total_confirmed": total_confirmed,
    }


@router.get("/students")
async def get_admin_students(
    grade: int | None = Query(default=None),
    class_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Get students list with optional grade/class filters"""
    query = db.query(Student)

    if grade is not None:
        query = query.filter(Student.grade == grade)
    if class_name:
        query = query.filter(Student.class_name == class_name.strip())

    students = query.order_by(Student.grade, Student.class_name, Student.name).all()
    return [
        {
            "id": student.id,
            "name": student.name,
            "class_name": student.class_name,
            "grade": student.grade,
            "id_card_last4": student.id_card_last4,
            "created_at": student.created_at.isoformat() if student.created_at else None,
        }
        for student in students
    ]


@router.get("/selected-students")
async def get_selected_students(
    grade: int | None = Query(default=None),
    class_name: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    """Get students who have confirmed selections with optional filters"""
    query = db.query(Student)

    if grade is not None:
        query = query.filter(Student.grade == grade)
    if class_name:
        query = query.filter(Student.class_name == class_name.strip())

    students = query.order_by(Student.grade, Student.class_name, Student.name).all()
    result = []
    for student in students:
        enrollments = db.query(Enrollment).filter(
            Enrollment.student_id == student.id,
            Enrollment.status == "CONFIRMED"
        ).all()

        if not enrollments:
            continue

        selections = {}
        for enrollment in enrollments:
            course = db.query(Course).filter(Course.id == enrollment.course_id).first()
            if course:
                selections[str(enrollment.day)] = {
                    "course_id": course.course_id,
                    "course_name": course.course_name,
                }

        result.append({
            "id": student.id,
            "name": student.name,
            "class_name": student.class_name,
            "grade": student.grade,
            "id_card_last4": student.id_card_last4,
            "selected_days": len(enrollments),
            "selections": selections,
        })

    return result


@router.delete("/selected-students/{student_id}/selections")
async def clear_student_selections(student_id: int, db: Session = Depends(get_db)):
    """Clear all confirmed selections for a student"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")

    deleted = db.query(Enrollment).filter(Enrollment.student_id == student_id).delete()
    db.commit()
    return {"message": "Selections cleared", "deleted": deleted}


@router.delete("/courses/{course_id}")
async def delete_course(course_id: int, db: Session = Depends(get_db)):
    """Delete course and related data"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    db.query(Enrollment).filter(Enrollment.course_id == course_id).delete()
    db.query(CourseGrade).filter(CourseGrade.course_id == course_id).delete()
    db.delete(course)
    db.commit()

    return {"message": "Course deleted successfully"}


@router.put("/courses/{course_id}/status")
async def set_course_status(
    course_id: int,
    request: CourseStatusRequest,
    db: Session = Depends(get_db)
):
    """Enable or disable a course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    course.is_active = request.is_active
    db.commit()

    return {
        "message": f"Course {'enabled' if request.is_active else 'disabled'} successfully",
        "course_id": course.id,
        "is_active": course.is_active,
    }


@router.get("/courses/{course_id}/students")
async def get_course_students(course_id: int, db: Session = Depends(get_db)):
    """Get students selected for a specific course"""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found",
        )

    enrollments = db.query(Enrollment).filter(
        Enrollment.course_id == course_id,
        Enrollment.status == "CONFIRMED"
    ).order_by(Enrollment.created_at.desc()).all()

    students = []
    for enrollment in enrollments:
        student = db.query(Student).filter(Student.id == enrollment.student_id).first()
        if not student:
            continue
        students.append({
            "id": student.id,
            "name": student.name,
            "class_name": student.class_name,
            "grade": student.grade,
            "id_card_last4": student.id_card_last4,
            "selected_day": enrollment.day,
            "selected_at": enrollment.created_at.isoformat() if enrollment.created_at else None,
        })

    return {
        "course": {
            "id": course.id,
            "course_id": course.course_id,
            "course_name": course.course_name,
            "teacher": course.teacher,
            "day": course.day,
        },
        "students": students,
        "total": len(students),
    }


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

        if 'bundle_id' not in df.columns:
            df['bundle_id'] = None

        bundle_rows: Dict[str, List[int]] = {}
        for index, row in df.iterrows():
            bundle_id_raw = row.get('bundle_id')
            if pd.isna(bundle_id_raw):
                continue
            bundle_id = str(bundle_id_raw).strip()
            if not bundle_id:
                continue
            bundle_rows.setdefault(bundle_id, []).append(index)

        bundle_errors = []
        for bundle_id, row_indexes in bundle_rows.items():
            if len(row_indexes) < 2:
                bundle_errors.append(
                    f"Bundle {bundle_id} must contain at least 2 courses"
                )
                continue

            bundle_days = [int(df.loc[i, 'day']) for i in row_indexes]
            if len(bundle_days) != len(set(bundle_days)):
                bundle_errors.append(f"Bundle {bundle_id} has duplicate day values")

            bundle_capacities = [int(df.loc[i, 'capacity']) for i in row_indexes]
            if len(set(bundle_capacities)) != 1:
                bundle_errors.append(f"Bundle {bundle_id} must have consistent capacity")

        if bundle_errors:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="; ".join(bundle_errors),
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
                    day=int(row['day']),
                    bundle_id=(
                        str(row['bundle_id']).strip()
                        if not pd.isna(row['bundle_id']) and str(row['bundle_id']).strip()
                        else None
                    ),
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
        
    except HTTPException:
        raise
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
        df = pd.read_csv(file.file, dtype=str).fillna("")
        
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
                student_name = str(row['name']).strip()
                class_name = str(row['class_name']).strip()
                id_card_raw = str(row['id_card']).strip()

                if not student_name:
                    raise ValueError("Name cannot be empty")
                if not class_name:
                    raise ValueError("Class name cannot be empty")
                if not id_card_raw:
                    raise ValueError("ID card cannot be empty")

                id_card_hash = hash_id_card(id_card_raw)
                id_card_last4 = get_id_card_last4(id_card_raw)
                
                existing_student = db.query(Student).filter(
                    Student.name == student_name,
                    Student.id_card_hash == id_card_hash
                ).first()
                
                if existing_student:
                    error_report.append(f"Row {index + 1}: Student {student_name} with ID card already exists")
                    continue
                
                new_student = Student(
                    name=student_name,
                    class_name=class_name,
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

    setting = db.query(SystemSetting).filter(SystemSetting.key == "course_selection_open").first()
    return {"open": setting.value.lower() == "true" if setting else False}


@router.put("/settings/admin-master-key")
async def set_admin_master_key(request: AdminMasterKeyRequest, db: Session = Depends(get_db)):
    """Set admin master key hash used for emergency student login"""
    master_key = request.key.strip()
    if not master_key.isdigit() or not (6 <= len(master_key) <= 20):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Master key must be digits only and 6-20 characters",
        )

    key_hash = hashlib.sha256(master_key.encode()).hexdigest()
    setting = db.query(SystemSetting).filter(SystemSetting.key == "admin_master_key_hash").first()
    if not setting:
        setting = SystemSetting(key="admin_master_key_hash", value=key_hash)
        db.add(setting)
    else:
        setting.value = key_hash

    db.commit()
    return {"message": "Admin master key updated"}


@router.get("/settings/admin-master-key")
async def get_admin_master_key_status(db: Session = Depends(get_db)):
    """Get admin master key configuration status"""
    setting = db.query(SystemSetting).filter(SystemSetting.key == "admin_master_key_hash").first()
    return {"configured": bool(setting and setting.value)}
