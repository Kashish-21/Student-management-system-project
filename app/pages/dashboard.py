# app/pages/1_📊_Dashboard.py
import streamlit as st
from app.services.auth import check_auth
from app.utils.db import get_db_connection

def show():
    check_auth()
    
    st.title("📊 Dashboard")
    
    # Get stats
    conn = get_db_connection()
    stats = {
        'total_students': conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        'total_teachers': conn.execute("SELECT COUNT(*) FROM teachers").fetchone()[0],
        'total_classes': len(set(conn.execute("SELECT DISTINCT class_name FROM students").fetchall())),
        'today_attendance': 0  # Will be implemented later
    }
    conn.close()
    
    # Display stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Students", stats['total_students'])
    with col2:
        st.metric("Total Teachers", stats['total_teachers'])
    with col3:
        st.metric("Classes", stats['total_classes'])
    with col4:
        st.metric("Today's Attendance", stats['today_attendance'])
    
    # Recent activities
    st.subheader("Recent Activities")
    st.info("No recent activities")