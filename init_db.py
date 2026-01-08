import os
import sqlite3
from datetime import datetime

def get_db_connection():
    conn = sqlite3.connect('sms.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Delete existing database if it exists
    if os.path.exists('sms.db'):
        os.remove('sms.db')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'teacher', 'student')) NOT NULL,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    # Insert default admin user
    import hashlib
    hashed_password = hashlib.sha256('admin123'.encode()).hexdigest()
    c.execute(
        """
        INSERT INTO users (username, password, email, full_name, role, is_active)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        ('admin', hashed_password, 'admin@example.com', 'Admin User', 'admin', 1)
    )
    
    # Create other tables
    c.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            admission_no TEXT UNIQUE NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            date_of_birth DATE,
            gender TEXT,
            class_name TEXT,
            section TEXT,
            roll_no TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS teachers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            employee_id TEXT UNIQUE,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            subject TEXT,
            class_teacher_of TEXT,
            status TEXT DEFAULT 'Active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
