# app/pages/teachers.py
import streamlit as st
from app.services.auth import get_current_user, check_auth
from app.utils.db import get_db_connection

def show():
    """Display the teachers management page."""
    check_auth()
    user = get_current_user()
    
    st.title("👨‍🏫 Teacher Management")
    st.write(f"Welcome, {user['full_name']}!")
    
    # Add a tab layout for different teacher management sections
    tab1, tab2 = st.tabs(["View Teachers", "Add Teacher"])
    
    with tab1:
        view_teachers()
    
    with tab2:
        add_teacher()

def view_teachers():
    """Display a list of all teachers."""
    st.header("All Teachers")
    
    conn = get_db_connection()
    teachers = conn.execute(
        "SELECT * FROM teachers ORDER BY first_name, last_name"
    ).fetchall()
    conn.close()
    
    if not teachers:
        st.info("No teachers found in the database.")
        return
    
    # Display teachers in a table
    teacher_data = []
    for teacher in teachers:
        teacher_data.append({
            "ID": teacher["id"],
            "Name": f"{teacher['first_name']} {teacher['last_name']}",
            "Employee ID": teacher["employee_id"],
            "Subject": teacher["subject"] if "subject" in teacher and teacher["subject"] else "N/A",
            "Class Teacher": teacher["class_teacher_of"] if "class_teacher_of" in teacher and teacher["class_teacher_of"] else "N/A",
            "Status": teacher["status"] if "status" in teacher else "Active"
        })
    
    st.table(teacher_data)

def add_teacher():
    """Form to add a new teacher."""
    st.header("Add New Teacher")
    
    with st.form("add_teacher_form"):
        st.subheader("Add New Teacher")
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", key="teacher_first_name")
            employee_id = st.text_input("Employee ID *", key="teacher_employee_id")
            email = st.text_input("Email *", key="teacher_email")
            
        with col2:
            last_name = st.text_input("Last Name *", key="teacher_last_name")
            subject = st.text_input("Subject", key="teacher_subject")
            class_teacher = st.text_input("Class Teacher Of", key="teacher_class_teacher")
            phone = st.text_input("Phone Number", key="teacher_phone")
            status = st.selectbox(
                "Status",
                ["Active", "Inactive"],
                key="teacher_status"
            )
        
        # Submit button must be inside the form
        submit_button = st.form_submit_button("Add Teacher")
        
        if submit_button:
            if not all([first_name, last_name, employee_id, email]):
                st.error("Please fill in all required fields (marked with *)")
            else:
                conn = get_db_connection()
                try:
                    conn.execute(
                        """
                        INSERT INTO teachers 
                        (first_name, last_name, employee_id, email, subject, 
                         class_teacher_of, phone, status)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (first_name, last_name, employee_id, email, subject, 
                         class_teacher, phone, status)
                    )
                    conn.commit()
                    st.success("Teacher added successfully!")
                except Exception as e:
                    st.error(f"Error adding teacher: {str(e)}")
                finally:
                    conn.close()