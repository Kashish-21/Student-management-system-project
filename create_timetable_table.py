from app.utils.db import get_db_connection

def create_timetable_table():
    conn = get_db_connection()
    try:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS timetable (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            day TEXT NOT NULL,
            class_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            room TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (class_id) REFERENCES classes (id),
            FOREIGN KEY (subject_id) REFERENCES subjects (id)
        );
        """)
        conn.commit()
        print("✅ Timetable table created successfully")
    except Exception as e:
        print(f"❌ Error creating timetable table: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    create_timetable_table()