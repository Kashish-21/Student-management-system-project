# app/services/student_service.py
import os
import sqlite3
import pandas as pd
from datetime import datetime
import io
from app.utils.db import get_db_connection
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads/students'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'doc', 'docx'}

def get_all_students(filters=None):
    """Get all students with optional filtering."""
    conn = get_db_connection()
    query = "SELECT * FROM students WHERE 1=1"
    params = []
    
    if filters:
        if filters.get('search'):
            search = f"%{filters['search']}%"
            query += " AND (first_name LIKE ? OR last_name LIKE ? OR admission_no LIKE ?)"
            params.extend([search, search, search])
        
        if filters.get('class_name'):
            query += " AND class_name = ?"
            params.append(filters['class_name'])
    
    try:
        students = conn.execute(query, params).fetchall()
        return [dict(student) for student in students]
    except Exception as e:
        print(f"Error fetching students: {e}")
        return []
    finally:
        conn.close()

def get_student_by_id(student_id):
    """Get a single student by ID."""
    conn = get_db_connection()
    student = conn.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
    conn.close()
    return dict(student) if student else None

def create_student(data, files=None):
    """Create a new student record."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO students (
                first_name, last_name, admission_no, class_name, section,
                roll_no, date_of_birth, gender, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['first_name'], 
            data.get('last_name', ''), 
            data.get('admission_no', ''),
            data.get('class', ''), 
            data.get('section', ''),
            data.get('roll_no', ''),  # Changed from roll_number to roll_no
            data.get('date_of_birth', ''), 
            data.get('gender', 'Other').capitalize(), 
            data.get('status', 'Active')
        ))
        student_id = cursor.lastrowid
        conn.commit()
        return student_id
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error creating student: {str(e)}")
    finally:
        conn.close()

def update_student(student_id, data, files=None):
    """Update an existing student record."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE students 
            SET first_name = ?, last_name = ?, admission_no = ?,
                class_name = ?, section = ?, roll_no = ?, date_of_birth = ?,
                gender = ?, status = ?
            WHERE id = ?
        """, (
            data['first_name'], 
            data.get('last_name', ''),
            data.get('admission_no', ''),
            data.get('class', ''), 
            data.get('section', ''), 
            data.get('roll_no', ''),  # Changed from roll_number to roll_no
            data.get('date_of_birth', ''), 
            data.get('gender', 'Other').capitalize(), 
            data.get('status', 'Active'),
            student_id
        ))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error updating student: {str(e)}")
    finally:
        conn.close()
        
def delete_student(student_id):
    """Delete a student record."""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error deleting student: {str(e)}")
    finally:
        conn.close()

def allowed_file(filename):
    """Check if the file type is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def export_to_excel(students):
    """Export students data to Excel format."""
    try:
        # Convert students data to DataFrame
        df = pd.DataFrame(students)
        
        # Create a BytesIO buffer to store the Excel file
        output = io.BytesIO()
        
        # Create Excel writer
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Students')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Students']
            for idx, col in enumerate(df.columns):
                max_length = max((
                    df[col].astype(str).map(len).max(),
                    len(str(col))
                )) + 2
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 30)
        
        # Get the value of the BytesIO buffer
        excel_data = output.getvalue()
        output.close()
        
        return excel_data
    except Exception as e:
        raise Exception(f"Error exporting to Excel: {str(e)}")

def export_to_pdf(students):
    """Export students data to PDF format using reportlab."""
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        
        # Create a BytesIO buffer to store the PDF
        output = io.BytesIO()
        
        # Create PDF document
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'Title',
            parent=styles['Heading1'],
            alignment=1,  # Center alignment
            spaceAfter=20
        )
        elements.append(Paragraph("Students List", title_style))
        
        # Convert students data to a list of lists for the table
        if not students:
            elements.append(Paragraph("No student data available.", styles['Normal']))
        else:
            # Get headers from the first student's keys
            headers = list(students[0].keys())
            data = [headers]
            
            # Add student data
            for student in students:
                row = [str(student.get(header, '')) for header in headers]
                data.append(row)
            
            # Create table
            table = Table(data)
            
            # Add style to table
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ])
            
            table.setStyle(style)
            elements.append(table)
        
        # Build PDF
        doc.build(elements)
        
        # Get the value of the BytesIO buffer
        pdf_data = output.getvalue()
        output.close()
        
        return pdf_data
    except Exception as e:
        raise Exception(f"Error exporting to PDF: {str(e)}")

# Keep the existing import_students_from_excel function
def import_students_from_excel(file):
    """Import students from an Excel file with flexible column name matching."""
    try:
        # Read the Excel file
        df = pd.read_excel(file)
        
        # Convert all column names to lowercase for case-insensitive matching
        df.columns = [str(col).strip().lower() for col in df.columns]
        
        # Map possible column name variations to standard column names
        column_mapping = {
            # Student ID variations
            'student id': 'admission_no',
            'studentid': 'admission_no',
            'id': 'admission_no',
            'student no': 'admission_no',
            'student_no': 'admission_no',
            'admission number': 'admission_no',
            
            # Name variations
            'student name': 'first_name',
            'student_name': 'first_name',
            'name': 'first_name',
            'student': 'first_name',
            'first name': 'first_name',
            'firstname': 'first_name',
            
            # Last name variations
            'last name': 'last_name',
            'lastname': 'last_name',
            'surname': 'last_name',
            
            # Class variations
            'class': 'class_name',
            'class name': 'class_name',
            'grade': 'class_name',
            'standard': 'class_name',
            
            # Section variations
            'section': 'section',
            'group': 'section',
            'division': 'section',
            
            # Gender variations
            'gender': 'gender',
            'sex': 'gender',
            
            # Roll number variations
            'roll no': 'roll_no',
            'roll_no': 'roll_no',
            'roll number': 'roll_no',
            'roll': 'roll_no',
            'roll no.': 'roll_no',
            
            # Date of birth variations
            'date of birth': 'date_of_birth',
            'dob': 'date_of_birth',
            'birth date': 'date_of_birth',
            'birthdate': 'date_of_birth'
        }
        
        # Apply the column mapping
        df = df.rename(columns=lambda x: column_mapping.get(x.lower().strip(), x.lower().strip()))
        
        # Ensure required columns exist
        required_columns = ['first_name', 'class_name']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            raise ValueError(f"Missing required columns: {', '.join(missing_columns)}. "
                           f"Available columns: {', '.join(df.columns)}")
        
        # Initialize counters
        success_count = 0
        errors = []
        
        # Process each row
        for index, row in df.iterrows():
            try:
                # Convert all values to strings and strip whitespace
                row = row.fillna('').astype(str).apply(lambda x: x.strip() if x else '')
                
                # Prepare student data with only the columns that exist in the database
                student_data = {
                    'first_name': row.get('first_name', ''),
                    'last_name': row.get('last_name', ''),
                    'admission_no': row.get('admission_no', ''),
                    'class': row.get('class_name', ''),  # Changed from class_name to class
                    'section': row.get('section', ''),
                    'roll_no': row.get('roll_no', ''),
                    'gender': row.get('gender', 'Other').capitalize() or 'Other',
                    'date_of_birth': row.get('date_of_birth', ''),
                    'status': 'Active'
                }
                
                # Create the student
                create_student(student_data)
                success_count += 1
                
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
                continue
        
        return {
            'total': len(df),
            'success': success_count,
            'errors': errors
        }
        
    except Exception as e:
        raise Exception(f"Error processing the file: {str(e)}")