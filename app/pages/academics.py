# app/pages/academics.py
import streamlit as st
from app.services.auth import get_current_user, check_auth
from app.utils.db import get_db_connection

def show():
    """Display the academics management page."""
    check_auth()
    user = get_current_user()
    
    st.title("📚 Academic Management")
    st.write(f"Welcome, {user['full_name']}!")
    
    # Add a tab layout for different academic management sections
    tab1, tab2, tab3 = st.tabs(["Classes", "Subjects", "Timetable"])
    
    with tab1:
        view_classes()
    
    with tab2:
        view_subjects()
    
    with tab3:
        view_timetable()

def view_classes():
    """Display and manage classes."""
    st.header("Classes")
    
    conn = get_db_connection()
    classes = conn.execute(
        "SELECT DISTINCT class_name FROM students ORDER BY class_name"
    ).fetchall()
    conn.close()
    
    if not classes:
        st.info("No classes found in the database.")
        return
    
    # Display classes in a table
    class_data = [{"Class": cls[0]} for cls in classes]
    st.table(class_data)
    
    # Add new class
    with st.expander("Add New Class"):
        with st.form("add_class_form"):
            new_class = st.text_input("Class Name", key="new_class_name")
            if st.form_submit_button("Add Class"):
                if new_class:
                    conn = get_db_connection()
                    try:
                        conn.execute(
                            "INSERT INTO classes (name) VALUES (?)",
                            (new_class,)
                        )
                        conn.commit()
                        st.success(f"Class '{new_class}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding class: {str(e)}")
                    finally:
                        conn.close()

def view_subjects():
    """Display and manage subjects."""
    st.header("Subjects")
    
    conn = get_db_connection()
    subjects = conn.execute(
        "SELECT * FROM subjects ORDER BY name"
    ).fetchall()
    conn.close()
    
    if subjects:
        subject_data = [{"ID": subj[0], "Name": subj[1], "Code": subj[2] or "N/A"} 
                       for subj in subjects]
        st.table(subject_data)
    else:
        st.info("No subjects found in the database.")
    
    # Add new subject
    with st.expander("Add New Subject"):
        with st.form("add_subject_form"):
            col1, col2 = st.columns(2)
            with col1:
                subject_name = st.text_input("Subject Name", key="new_subject_name")
            with col2:
                subject_code = st.text_input("Subject Code (Optional)", key="new_subject_code")
            
            if st.form_submit_button("Add Subject"):
                if subject_name:
                    conn = get_db_connection()
                    try:
                        conn.execute(
                            "INSERT INTO subjects (name, code) VALUES (?, ?)",
                            (subject_name, subject_code or None)
                        )
                        conn.commit()
                        st.success(f"Subject '{subject_name}' added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding subject: {str(e)}")
                    finally:
                        conn.close()

def view_timetable():
    """View and manage class timetables."""
    st.header("📅 Class Timetable")
    
    # Get all classes and subjects for dropdowns
    conn = get_db_connection()
    classes = conn.execute("SELECT id, name FROM classes ORDER BY name").fetchall()
    subjects = conn.execute("SELECT id, name FROM subjects ORDER BY name").fetchall()
    conn.close()
    
    # Create tabs for different days
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    tabs = st.tabs(days)
    
    for i, day in enumerate(days):
        with tabs[i]:
            st.subheader(f"{day} Timetable")
            
            # Get existing timetable for the day
            conn = get_db_connection()
            timetable = conn.execute("""
                SELECT t.id, c.name as class_name, s.name as subject_name, 
                       t.start_time, t.end_time, t.room
                FROM timetable t
                JOIN classes c ON t.class_id = c.id
                JOIN subjects s ON t.subject_id = s.id
                WHERE t.day = ?
                ORDER BY t.start_time
            """, (day,)).fetchall()
            conn.close()
            
            # Display existing timetable
            if timetable:
                st.write("### Current Schedule")
                timetable_data = []
                for entry in timetable:
                    timetable_data.append({
                        "Class": entry['class_name'],
                        "Subject": entry['subject_name'],
                        "Time": f"{entry['start_time']} - {entry['end_time']}",
                        "Room": entry['room'] or "-"
                    })
                st.table(timetable_data)
            
            # Add new timetable entry
            with st.expander(f"Add New Entry for {day}"):
                with st.form(f"add_timetable_{day}"):
                    # First row: Class and Subject
                    row1 = st.columns(2)
                    with row1[0]:
                        class_id = st.selectbox(
                            "Class",
                            options=[c['id'] for c in classes],
                            format_func=lambda x: next((c['name'] for c in classes if c['id'] == x), ""),
                            key=f"class_{day}"
                        )
                    with row1[1]:
                        subject_id = st.selectbox(
                            "Subject",
                            options=[s['id'] for s in subjects],
                            format_func=lambda x: next((s['name'] for s in subjects if s['id'] == x), ""),
                            key=f"subject_{day}"
                        )
                    
                    # Second row: Time inputs and Room
                    row2 = st.columns(3)
                    with row2[0]:
                        st.write("Start Time")
                        start_time = st.time_input("", key=f"start_{day}")
                    with row2[1]:
                        st.write("End Time")
                        end_time = st.time_input("", key=f"end_{day}")
                    with row2[2]:
                        room = st.text_input("Room", key=f"room_{day}")
                    
                    if st.form_submit_button("Add to Timetable"):
                        if start_time >= end_time:
                            st.error("End time must be after start time")
                        else:
                            conn = get_db_connection()
                            try:
                                conn.execute("""
                                    INSERT INTO timetable 
                                    (day, class_id, subject_id, start_time, end_time, room)
                                    VALUES (?, ?, ?, ?, ?, ?)
                                """, (
                                    day, 
                                    class_id, 
                                    subject_id, 
                                    start_time.strftime("%H:%M"), 
                                    end_time.strftime("%H:%M"),
                                    room or None
                                ))
                                conn.commit()
                                st.success("Timetable entry added successfully!")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error adding timetable entry: {str(e)}")
                            finally:
                                conn.close()