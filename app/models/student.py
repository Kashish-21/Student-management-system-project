# app/models/student.py
from app import db
from datetime import datetime

class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    admission_no = db.Column(db.String(20), unique=True, nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    blood_group = db.Column(db.String(5))
    aadhar_no = db.Column(db.String(12), unique=True)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(15))
    address = db.Column(db.Text)
    city = db.Column(db.String(50))
    state = db.Column(db.String(50))
    pincode = db.Column(db.String(10))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'))
    roll_no = db.Column(db.String(10))
    admission_date = db.Column(db.Date)
    academic_year = db.Column(db.String(10))
    previous_school = db.Column(db.Text)
    photo = db.Column(db.String(200))
    birth_certificate = db.Column(db.String(200))
    aadhar_card = db.Column(db.String(200))
    status = db.Column(db.String(20), default='Active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    class_ = db.relationship('Class', backref='students')
    section = db.relationship('Section', backref='students')
    attendances = db.relationship('Attendance', backref='student', lazy=True)