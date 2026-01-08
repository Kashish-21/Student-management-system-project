# app/pages/settings.py
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import os
import shutil
from app.services.auth import check_auth

def show():
    check_auth()
    st.title("⚙️ System Settings")
    
    # Only allow admin access
    if st.session_state.user.get('role') != 'admin':
        st.error("⚠️ Only administrators can access system settings")
        return
    
    # Create tabs for different settings sections
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 System Overview", 
        "📝 User Activity Logs", 
        "⚙️ System Configuration",
        "💾 Backup & Restore"
    ])
    
    with tab1:
        show_system_overview()
    
    with tab2:
        show_activity_logs()
    
    with tab3:
        show_system_config()
    
    with tab4:
        show_backup_restore()

def show_system_overview():
    st.header("System Overview")
    conn = get_db_connection()
    
    # Get system statistics
    stats = {
        'Total Students': conn.execute("SELECT COUNT(*) FROM students").fetchone()[0],
        'Total Teachers': conn.execute("SELECT COUNT(*) FROM users WHERE role = 'teacher'").fetchone()[0],
        'Total Classes': conn.execute("SELECT COUNT(*) FROM classes").fetchone()[0],
        'Total Subjects': conn.execute("SELECT COUNT(*) FROM subjects").fetchone()[0],
    }
    
    # Display stats in columns
    cols = st.columns(4)
    for i, (key, value) in enumerate(stats.items()):
        with cols[i]:
            st.metric(key, value)
    
    # Attendance summary
    st.subheader("📅 Attendance Summary")
    today = datetime.now().strftime('%Y-%m-%d')
    attendance = conn.execute('''
        SELECT 
            COUNT(CASE WHEN status = 'present' OR status = 'late' THEN 1 END) as present,
            COUNT(*) as total
        FROM attendance 
        WHERE date = ?
    ''', (today,)).fetchone()
    
    if attendance['total'] > 0:
        attendance_rate = (attendance['present'] / attendance['total']) * 100
        st.metric("Today's Attendance Rate", f"{attendance_rate:.1f}%")
    else:
        st.info("No attendance records for today")
    
    # Performance summary
    st.subheader("📈 Performance Summary")
    st.info("Performance metrics will be displayed here")
    # Add performance metrics as needed
    
    conn.close()

def show_activity_logs():
    st.header("User Activity Logs")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", datetime.now() - timedelta(days=7))
    with col2:
        end_date = st.date_input("End Date", datetime.now())
    
    # Log levels
    log_levels = st.multiselect(
        "Filter by Log Level",
        ['INFO', 'WARNING', 'ERROR', 'AUDIT'],
        ['INFO', 'WARNING', 'ERROR']
    )
    
    if st.button("Load Logs"):
        # This is a placeholder - in a real app, you would query actual logs
        st.info("Log viewing functionality will be implemented here")
        # Example of how you might display logs
        logs = [
            {"timestamp": "2024-01-04 10:30:00", "level": "INFO", "user": "admin", "action": "User logged in"},
            {"timestamp": "2024-01-04 10:35:00", "level": "AUDIT", "user": "admin", "action": "Updated student record #123"},
        ]
        st.dataframe(pd.DataFrame(logs))

def show_system_config():
    st.header("System Configuration")
    
    with st.form("system_config_form"):
        st.subheader("Email Settings")
        smtp_server = st.text_input("SMTP Server", "smtp.example.com")
        smtp_port = st.number_input("SMTP Port", min_value=1, max_value=65535, value=587, step=1)
        smtp_username = st.text_input("SMTP Username", "noreply@example.com")
        smtp_password = st.text_input("SMTP Password", type="password")
        
        st.subheader("System Behavior")
        session_timeout = st.number_input("Session Timeout (minutes)", 15, 1440, 30)
        enable_registration = st.checkbox("Enable New User Registration", value=True)
        maintenance_mode = st.checkbox("Maintenance Mode", value=False)
        
        if st.form_submit_button("Save Configuration"):
            # In a real app, you would save these settings to a configuration file or database
            st.success("Configuration saved successfully!")

def show_backup_restore():
    st.header("Backup & Restore")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Create Backup")
        backup_name = st.text_input("Backup Name", f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        if st.button("Create Backup"):
            try:
                # Create backup directory if it doesn't exist
                if not os.path.exists('backups'):
                    os.makedirs('backups')
                
                # Create backup
                backup_path = os.path.join('backups', f"{backup_name}.db")
                shutil.copy2('sms.db', backup_path)
                
                # Log the backup
                with open('backups/backup_log.txt', 'a') as f:
                    f.write(f"{datetime.now()}: Backup created - {backup_name}\n")
                
                st.success(f"Backup created successfully at {backup_path}")
            except Exception as e:
                st.error(f"Error creating backup: {str(e)}")
    
    with col2:
        st.subheader("Restore Backup")
        
        # List available backups
        if not os.path.exists('backups'):
            st.warning("No backups found")
            return
            
        backups = [f for f in os.listdir('backups') if f.endswith('.db')]
        if not backups:
            st.warning("No backup files found")
            return
            
        selected_backup = st.selectbox("Select backup to restore", backups)
        
        if st.button("Restore Selected Backup", type="primary"):
            if st.checkbox("I understand this will overwrite the current database", key="confirm_restore"):
                try:
                    # Create a backup of current database before restoring
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    shutil.copy2('sms.db', f'sms_backup_before_restore_{timestamp}.db')
                    
                    # Restore the selected backup
                    shutil.copy2(os.path.join('backups', selected_backup), 'sms.db')
                    
                    # Log the restore
                    with open('backups/backup_log.txt', 'a') as f:
                        f.write(f"{datetime.now()}: Database restored from {selected_backup}\n")
                    
                    st.success("Database restored successfully! Please restart the application.")
                except Exception as e:
                    st.error(f"Error restoring backup: {str(e)}")
            else:
                st.warning("Please confirm you understand this will overwrite the current database")

def get_db_connection():
    conn = sqlite3.connect('sms.db')
    conn.row_factory = sqlite3.Row
    return conn