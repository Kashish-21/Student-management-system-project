# create_attendance_table.py
import sqlite3

def create_attendance_table():
    conn = sqlite3.connect('sms.db')
    cursor = conn.cursor()
    
    # Create attendance table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        status TEXT NOT NULL,  -- 'present', 'absent', 'late', 'excused'
        subject_id INTEGER,
        remarks TEXT,
        recorded_by INTEGER,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (subject_id) REFERENCES subjects (id),
        FOREIGN KEY (recorded_by) REFERENCES users (id)
    )
    ''')
    
    # Create an index for faster lookups
    cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_attendance_student_date 
    ON attendance (student_id, date)
    ''')
    
    conn.commit()
    conn.close()
    print("✅ Attendance table created successfully")

if __name__ == '__main__':
    create_attendance_table()