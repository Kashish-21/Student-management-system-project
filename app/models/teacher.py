# app/models/teacher.py
from app import db
from datetime import datetime

class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True)
    employee_id = db.Column(db.String(20), unique=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    qualification = db.Column(db.String(100))
    experience = db.Column(db.Float)
    joining_date = db.Column(db.Date)
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    photo = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='teacher_profile', uselist=False)
    class_subjects = db.relationship('ClassSubject', backref='subject_teacher')