"""
Database models for the course selection system
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    class_name = Column(String(50), nullable=False)
    grade = Column(Integer, nullable=False)
    id_card_hash = Column(String(64), nullable=False)
    id_card_last4 = Column(String(4), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('name', 'id_card_hash', name='uq_student_name_id_card'),
    )

    enrollments = relationship("Enrollment", back_populates="student")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(String(20), unique=True, nullable=False, index=True)
    course_name = Column(String(100), nullable=False)
    teacher = Column(String(50), nullable=False)
    capacity = Column(Integer, nullable=False)
    day = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint('day IN (1,3,4,5)', name='ck_course_day_valid'),
    )

    grades = relationship("CourseGrade", back_populates="course")
    enrollments = relationship("Enrollment", back_populates="course")


class CourseGrade(Base):
    __tablename__ = "course_grades"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    grade = Column(Integer, nullable=False)

    __table_args__ = (
        UniqueConstraint('course_id', 'grade', name='uq_course_grade'),
    )

    course = relationship("Course", back_populates="grades")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    day = Column(Integer, nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    status = Column(String(20), default='CONFIRMED', nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        UniqueConstraint('student_id', 'day', name='uq_enrollment_student_day'),
        CheckConstraint('day IN (1,3,4,5)', name='ck_enrollment_day_valid'),
    )

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class SystemSetting(Base):
    __tablename__ = "system_settings"

    key = Column(String(50), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class ImportLog(Base):
    __tablename__ = "import_logs"

    id = Column(Integer, primary_key=True, index=True)
    import_type = Column(String(50), nullable=False)
    total_rows = Column(Integer, nullable=False)
    success_rows = Column(Integer, nullable=False)
    failed_rows = Column(Integer, nullable=False)
    error_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
