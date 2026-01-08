# app/services/attendance_service.py
import sqlite3
from datetime import datetime, timedelta
from app.utils.db import get_db_connection

def record_attendance(student_id, date, status, subject_id=None, remarks='', recorded_by=None):
    conn = get_db_connection()
    try:
        conn.execute('''
        INSERT INTO attendance (student_id, date, status, subject_id, remarks, recorded_by)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (student_id, date, status, subject_id, remarks, recorded_by))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"Error recording attendance: {e}")
        return False
    finally:
        conn.close()

def get_student_attendance(student_id, start_date=None, end_date=None):
    conn = get_db_connection()
    query = 'SELECT * FROM attendance WHERE student_id = ?'
    params = [student_id]
    
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    
    query += ' ORDER BY date DESC'
    attendance = conn.execute(query, tuple(params)).fetchall()
    conn.close()
    return attendance

def calculate_attendance_percentage(student_id, subject_id=None, start_date=None, end_date=None):
    conn = get_db_connection()
    query = '''
    SELECT 
        COUNT(CASE WHEN status = 'present' OR status = 'late' THEN 1 END) as present_days,
        COUNT(*) as total_days
    FROM attendance 
    WHERE student_id = ?
    '''
    params = [student_id]
    
    if subject_id:
        query += ' AND subject_id = ?'
        params.append(subject_id)
    if start_date:
        query += ' AND date >= ?'
        params.append(start_date)
    if end_date:
        query += ' AND date <= ?'
        params.append(end_date)
    
    result = conn.execute(query, tuple(params)).fetchone()
    conn.close()
    
    if not result or result['total_days'] == 0:
        return 0
    return (result['present_days'] / result['total_days']) * 100

def get_low_attendance_students(threshold=75, subject_id=None, days_back=30):
    conn = get_db_connection()
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
    
    query = '''
    SELECT 
        s.id as student_id,
        s.first_name || ' ' || s.last_name as student_name,
        COUNT(CASE WHEN a.status = 'present' OR a.status = 'late' THEN 1 END) as present_days,
        COUNT(*) as total_days,
        ROUND((COUNT(CASE WHEN a.status = 'present' OR a.status = 'late' THEN 1 END) * 100.0 / COUNT(*)), 2) as attendance_percentage
    FROM students s
    LEFT JOIN attendance a ON s.id = a.student_id
    WHERE a.date BETWEEN ? AND ?
    '''
    params = [start_date, end_date]
    
    if subject_id:
        query += ' AND a.subject_id = ?'
        params.append(subject_id)
    
    query += '''
    GROUP BY s.id, s.first_name, s.last_name
    HAVING attendance_percentage < ? OR attendance_percentage IS NULL
    ORDER BY attendance_percentage ASC
    '''
    params.append(threshold)
    
    students = conn.execute(query, tuple(params)).fetchall()
    conn.close()
    return students