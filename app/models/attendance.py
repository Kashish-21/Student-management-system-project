# app/models/attendance.py
from app import db
from datetime import date

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.Enum('present', 'absent', 'late', 'half_day', name='attendance_status'), 
                      nullable=False, default='present')
    remarks = db.Column(db.Text)
    marked_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    
    # Relationships
    class_ = db.relationship('Class', backref='attendance_records')
    section = db.relationship('Section', backref='attendance_records')
    marked_by_user = db.relationship('User', backref='marked_attendances')