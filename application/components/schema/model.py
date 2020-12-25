from sqlalchemy import (
    Column, String, Integer, BigInteger, Date, Boolean,\
    FLOAT, Text, SmallInteger, ForeignKey, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from application.database import db
from application.database.model import CommonModel


class Cookie(CommonModel):
    __tablename__ = 'cookie'
    student_code = db.Column(String(30))
    password = db.Column(String(100), nullable=False)
    cookie = db.Column(String())
    
class Student(CommonModel):
    __tablename__ = 'student'
    student_code = db.Column(String(30))
    password = db.Column(String(100), nullable=False)
    student_name = db.Column(String(30))
    faculty = db.Column(String(30))
    faculty_class = db.Column(String(10))
    Subjects = db.relationship("Subjects", order_by="Subjects.id", cascade="all, delete-orphan")


class Subjects(CommonModel):
    __tablename__ = 'subjects'
    id_subjects = db.Column(String(30))
    subjects_name = db.Column(String(100), nullable=False)
    secturers = db.Column(String(50), nullable=False)
    student_total = db.Column(Integer())
    Schedules = db.relationship("Schedule", order_by="Schedule.id", cascade="all, delete-orphan")
    Student_id = db.Column(UUID(as_uuid=True), db.ForeignKey("student.id"))
    Students = db.relationship("Student")


class Schedule(CommonModel):
    __tablename__ = 'schedule'
    id_schedule = db.Column(UUID(as_uuid=True))
    start_time = db.Column(BigInteger())
    end_time = db.Column(BigInteger())
    address = db.Column(BigInteger())
    Study_Shift = db.Column(String(20))
    # id_study_day
    # Study_days = db.relationship('Study_day',back_populates = "study_day")
    Study_days = db.relationship("Study_day", order_by="Study_day.id", cascade="all, delete-orphan")
    Study_classs = db.relationship("Study_class", order_by="Study_class.id", cascade="all, delete-orphan")
    #========================
    Subjects_id = db.Column(UUID(as_uuid=True), db.ForeignKey("subjects.id"))
    Subjects = db.relationship("Subjects")


class Study_day(CommonModel):
    __tablename__ = 'study_day'
    id_study_day = db.Column(UUID(as_uuid=True))
    Schedule_id = db.Column(UUID(as_uuid=True), db.ForeignKey("schedule.id"))
    Schedule = db.relationship("Schedule")

    
class Study_class(CommonModel):
    __tablename__ = 'study_class'
    id_study_class = db.Column(UUID(as_uuid=True))
    class_name = db.Column(String(20))
    Schedule_id = db.Column(UUID(as_uuid=True), db.ForeignKey("schedule.id"))
    Schedule = db.relationship("Schedule")




    




    


