# reset_db.py
import os
import sqlite3
from app.utils.db import init_db

def reset_database():
    # Remove existing database file if it exists
    if os.path.exists('sms.db'):
        try:
            os.remove('sms.db')
            print("✅ Removed existing database file")
        except Exception as e:
            print(f"❌ Error removing database: {e}")
            return False
    
    # Initialize new database
    try:
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Starting database reset...")
    if reset_database():
        print("✨ Database reset completed successfully!")
    else:
        print("❌ Database reset failed")