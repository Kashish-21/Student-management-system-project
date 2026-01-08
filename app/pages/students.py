# app/pages/students.py
import streamlit as st
import pandas as pd
import os
from datetime import datetime
from app.services.auth import check_auth
from app.utils.db import get_db_connection
from app.services.student_service import (
    get_all_students,
    get_student_by_id,
    create_student,  
    update_student,
    delete_student,
    import_students_from_excel,
    export_to_excel,
    export_to_pdf
)
from app.utils.db import get_db_connection

def check_students_table():
    """Check the structure of the students table."""
    conn = get_db_connection()
    try:
        # Get table info
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(students)")
        columns = cursor.fetchall()
        st.write("Current students table columns:")
        for col in columns:
            st.write(f"- {col[1]} ({col[2]})")
    except Exception as e:
        st.error(f"Error checking table structure: {str(e)}")
    finally:
        conn.close()

# Call this function to see the table structure
check_students_table()

def show():
    """Main function to display the students page."""
    check_auth()
    st.title("👥 Student Management")
    
    # Initialize session state
    if 'editing_student_id' not in st.session_state:
        st.session_state.editing_student_id = None
    if 'deleting_student_id' not in st.session_state:
        st.session_state.deleting_student_id = None
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["View Students", "Add Student", "Bulk Operations"])
    
    with tab1:
        view_students()
    
    with tab2:
        if st.session_state.editing_student_id:
            edit_student(st.session_state.editing_student_id)
        else:
            add_student()
    
    with tab3:
        bulk_operations()
    
    # Handle edit/delete actions
    if st.session_state.get('editing_student_id') or st.session_state.get('deleting_student_id'):
        st.session_state['editing_student_id'] = None
        st.session_state['deleting_student_id'] = None

def view_students():
    """Display a table of all students with edit/delete options."""
    st.header("All Students")
    
    # Add search and filter options
    search_col1, search_col2 = st.columns(2)
    
    with search_col1:
        search_term = st.text_input("Search by name or ID", "")
    
    with search_col2:
        class_filter = st.selectbox(
            "Filter by Class",
            ["All"] + list(get_all_classes()),
            index=0
        )
    
    # Get and filter students
    students = get_all_students()
    
    if search_term:
        search_term = search_term.lower()
        students = [
            s for s in students 
            if (search_term in s['first_name'].lower() or 
                search_term in s['last_name'].lower() or
                search_term in str(s['id']).lower() or
                search_term in (s.get('admission_number', '') or '').lower())
        ]
    
    if class_filter and class_filter != "All":
        students = [s for s in students if s.get('class') == class_filter]
    
    if not students:
        st.info("No students found matching the criteria.")
        return
    
    # Create a DataFrame for display
    df = pd.DataFrame([{
    'ID': s['id'],
    'Name': f"{s['first_name']} {s['last_name']}",
    'Admission No.': s.get('admission_no', ''),
    'Class': s.get('class_name', ''),  
    'Section': s.get('section', ''),
    'Roll No.': s.get('roll_number', ''),
    'Gender': s.get('gender', ''),
    'Status': s.get('status', 'Active')
} for s in students])
    
    # Display the table
    st.dataframe(
        df,
        column_config={
            'ID': st.column_config.NumberColumn('ID', width="small"),
            'Name': 'Name',
            'Admission No.': 'Admission No.',
            'Class': 'Class',
            'Section': 'Section',
            'Roll No.': 'Roll No.',
            'Gender': 'Gender',
            'Status': 'Status',
            'Actions': None
        },
        use_container_width=True
    )
    
    # Add export buttons
    st.download_button(
        "Export to Excel",
        export_to_excel(students),
        "students.xlsx",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    st.download_button(
        "Export to PDF",
        export_to_pdf(students),
        "students.pdf",
        "application/pdf"
    )

def add_student():
    """Form to add a new student."""
    st.header("Add New Student")
    
    with st.form("add_student_form"):
        st.subheader("Student Information")
        
        # Personal Information
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", key="student_first_name")
            last_name = st.text_input("Last Name *", key="student_last_name")
            admission_number = st.text_input("Admission Number *", key="student_admission_no")
            date_of_birth = st.date_input("Date of Birth *", key="student_dob")
            gender = st.selectbox(
                "Gender *",
                ["Male", "Female", "Other"],
                key="student_gender"
            )
            
        with col2:
            class_name = st.text_input("Class *", key="student_class")
            section = st.text_input("Section", key="student_section")
            roll_number = st.text_input("Roll Number", key="student_roll_no")
            admission_date = st.date_input("Admission Date", key="student_admission_date")
            status = st.selectbox(
                "Status",
                ["Active", "Inactive", "Graduated", "Transferred"],
                key="student_status"
            )
        
        # Contact Information
        st.subheader("Contact Information")
        contact_col1, contact_col2 = st.columns(2)
        
        with contact_col1:
            father_name = st.text_input("Father's Name", key="student_father_name")
            mother_name = st.text_input("Mother's Name", key="student_mother_name")
            email = st.text_input("Email", key="student_email")
            
        with contact_col2:
            phone = st.text_input("Phone Number", key="student_phone")
            address = st.text_area("Address", key="student_address")
        
        # Submit button
        submit_button = st.form_submit_button("Add Student")
        
        if submit_button:
            # Validate required fields
            required_fields = {
                "First Name": first_name,
                "Last Name": last_name,
                "Admission Number": admission_number,
                "Class": class_name,
                "Date of Birth": date_of_birth,
                "Gender": gender
            }
            
            missing_fields = [field for field, value in required_fields.items() if not value]
            
            if missing_fields:
                st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
            else:
                conn = get_db_connection()
                try:
                    conn.execute(
                        """
                        INSERT INTO students 
                        (first_name, last_name, admission_number, class, section, 
                         roll_number, date_of_birth, gender, admission_date, status,
                         father_name, mother_name, email, phone, address)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            first_name, last_name, admission_number, class_name, section,
                            roll_number, date_of_birth, gender, admission_date, status,
                            father_name, mother_name, email, phone, address
                        )
                    )
                    conn.commit()
                    st.success("Student added successfully!")
                except Exception as e:
                    st.error(f"Error adding student: {str(e)}")
                finally:
                    conn.close()

def edit_student(student_id):
    """Form to edit an existing student."""
    student = get_student_by_id(student_id)
    if not student:
        st.error("Student not found")
        return
    
    st.header(f"Edit Student: {student['first_name']} {student['last_name']}")
    
    with st.form(f"edit_student_{student_id}"):
        # Similar to add_student but with existing values
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name *", value=student.get('first_name', ''))
            last_name = st.text_input("Last Name *", value=student.get('last_name', ''))
            admission_number = st.text_input(
                "Admission Number *", 
                value=student.get('admission_number', '')
            )
            date_of_birth = st.date_input(
                "Date of Birth *", 
                value=datetime.strptime(student['date_of_birth'], '%Y-%m-%d') if student.get('date_of_birth') else None
            )
            gender = st.selectbox(
                "Gender *",
                ["Male", "Female", "Other"],
                index=["Male", "Female", "Other"].index(student.get('gender', 'Male'))
            )
            
        with col2:
            class_name = st.text_input("Class *", value=student.get('class', ''))
            section = st.text_input("Section", value=student.get('section', ''))
            roll_number = st.text_input("Roll Number", value=student.get('roll_number', ''))
            admission_date = st.date_input(
                "Admission Date",
                value=datetime.strptime(student['admission_date'], '%Y-%m-%d') if student.get('admission_date') else None
            )
            status = st.selectbox(
                "Status",
                ["Active", "Inactive", "Graduated", "Transferred"],
                index=["Active", "Inactive", "Graduated", "Transferred"].index(
                    student.get('status', 'Active')
                )
            )
        
        # Contact Information
        st.subheader("Contact Information")
        contact_col1, contact_col2 = st.columns(2)
        
        with contact_col1:
            father_name = st.text_input("Father's Name", value=student.get('father_name', ''))
            mother_name = st.text_input("Mother's Name", value=student.get('mother_name', ''))
            email = st.text_input("Email", value=student.get('email', ''))
            
        with contact_col2:
            phone = st.text_input("Phone Number", value=student.get('phone', ''))
            address = st.text_area("Address", value=student.get('address', ''))
        
        # Submit and Cancel buttons
        col1, col2 = st.columns([1, 5])
        with col1:
            if st.form_submit_button("Update Student"):
                # Similar validation as add_student
                required_fields = {
                    "First Name": first_name,
                    "Last Name": last_name,
                    "Admission Number": admission_number,
                    "Class": class_name,
                    "Date of Birth": date_of_birth,
                    "Gender": gender
                }
                
                missing_fields = [field for field, value in required_fields.items() if not value]
                
                if missing_fields:
                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
                else:
                    try:
                        update_student_service(
                            student_id,
                            first_name=first_name,
                            last_name=last_name,
                            admission_number=admission_number,
                            class_name=class_name,
                            section=section,
                            roll_number=roll_number,
                            date_of_birth=date_of_birth,
                            gender=gender,
                            admission_date=admission_date,
                            status=status,
                            father_name=father_name,
                            mother_name=mother_name,
                            email=email,
                            phone=phone,
                            address=address
                        )
                        st.success("Student updated successfully!")
                        st.session_state.editing_student_id = None
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error updating student: {str(e)}")
        
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.editing_student_id = None
                st.experimental_rerun()

def delete_student(student_id):
    """Delete a student after confirmation."""
    student = get_student_by_id(student_id)
    if not student:
        st.error("Student not found")
        return
    
    st.warning(f"Are you sure you want to delete {student['first_name']} {student['last_name']}?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Yes, Delete"):
            try:
                delete_student_service(student_id)
                st.success("Student deleted successfully!")
                st.session_state.deleting_student_id = None
                st.experimental_rerun()
            except Exception as e:
                st.error(f"Error deleting student: {str(e)}")
    
    with col2:
        if st.button("No, Cancel"):
            st.session_state.deleting_student_id = None
            st.experimental_rerun()

def bulk_operations():
    """Handle bulk import/export operations."""
    st.header("Bulk Operations")
    
    tab1, tab2 = st.tabs(["Import Students", "Export Students"])
    
    with tab1:
        st.subheader("Import Students from Excel")
        st.info("""
            Please prepare an Excel file with the following columns:
            - first_name (required)
            - last_name (required)
            - admission_number (required)
            - class (required)
            - section (optional)
            - roll_number (optional)
            - gender (optional)
            - date_of_birth (optional)
            - admission_date (optional)
            - status (optional)
            - father_name (optional)
            - mother_name (optional)
            - email (optional)
            - phone (optional)
            - address (optional)
        """)
        
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
        
        if uploaded_file is not None:
            try:
                # Read the Excel file
                df = pd.read_excel(uploaded_file)
                
                # Show a preview of the data
                st.subheader("Preview of the data to be imported")
                st.dataframe(df.head())
                
                if st.button("Import Students", key="import_btn"):
                    # Process the import
                    result = import_students_from_excel(uploaded_file)
                    
                    if result['errors']:
                        st.warning(f"Import completed with {len(result['errors'])} errors out of {result['total']} records.")
                        st.error("\n".join(result['errors']))
                    else:
                        st.success(f"Successfully imported {result['success']} out of {result['total']} students.")
                        st.balloons()
                        
            except Exception as e:
                st.error(f"Error processing the file: {str(e)}")
    
    with tab2:
        st.subheader("Export Students")
        st.info("Export all students to Excel or PDF format.")
        
        # Get all students
        students = get_all_students()
        
        if not students:
            st.warning("No students found to export.")
            return
            
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                "Export to Excel",
                export_to_excel(students),
                "students_export.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        with col2:
            st.download_button(
                "Export to PDF",
                export_to_pdf(students),
                "students_export.pdf",
                "application/pdf"
            )

def get_all_classes():
    """Get all unique class names from the database."""
    conn = get_db_connection()
    try:
        classes = conn.execute("""
            SELECT DISTINCT class_name 
            FROM students 
            WHERE class_name IS NOT NULL 
            ORDER BY class_name
        """).fetchall()
        return [c[0] for c in classes] if classes else []
    except Exception as e:
        st.error(f"Error fetching classes: {str(e)}")
        return []
    finally:
        conn.close()