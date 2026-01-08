import streamlit as st
from datetime import datetime
from app.utils.db import get_db_connection
from app.services.auth import check_auth

def show():
    """Main function to display the attendance page."""
    check_auth()
    st.title("📊 Attendance Management")
    
    # Initialize session state
    if 'selected_class' not in st.session_state:
        st.session_state.selected_class = None
    if 'selected_section' not in st.session_state:
        st.session_state.selected_section = None
    
    # Get unique classes and sections
    conn = get_db_connection()
    try:
        # Get unique classes
        classes = conn.execute("""
            SELECT DISTINCT class_name 
            FROM students 
            WHERE status = 'Active'
            ORDER BY class_name
        """).fetchall()
        class_list = [c['class_name'] for c in classes]
        
        # Class selection
        selected_class = st.selectbox(
            "Select Class",
            [""] + class_list,
            key="class_select"
        )
        
        # Section selection
        if selected_class:
            sections = conn.execute("""
                SELECT DISTINCT section 
                FROM students 
                WHERE class_name = ? AND status = 'Active'
                ORDER BY section
            """, (selected_class,)).fetchall()
            section_list = [s['section'] for s in sections]
            
            selected_section = st.selectbox(
                "Select Section",
                [""] + section_list,
                key="section_select"
            )
            
            if selected_section:
                # Get students for the selected class and section
                students = conn.execute("""
                    SELECT id, first_name, last_name, roll_no 
                    FROM students 
                    WHERE class_name = ? AND section = ? AND status = 'Active'
                    ORDER BY roll_no, first_name
                """, (selected_class, selected_section)).fetchall()
                
                # Convert Row objects to dictionaries
                students = [dict(row) for row in students]
                
                if not students:
                    st.warning("No active students found for the selected class and section.")
                    return
                
                # Display attendance form
                st.subheader(f"Mark Attendance - {selected_class} {selected_section}")
                attendance_date = st.date_input("Date", datetime.now())
                status_options = ['present', 'absent', 'late', 'excused']
                
                # Create attendance form
                with st.form("attendance_form"):
                    st.write("### Student Attendance")
                    attendance_data = []
                    
                    # Create two columns for better layout
                    col1, col2 = st.columns(2)
                    
                    for i, student in enumerate(students):
                        # Alternate between columns
                        col = col1 if i % 2 == 0 else col2
                        
                        with col:
                            student_name = f"{student['first_name']} {student['last_name']}"
                            if student.get('roll_no'):
                                student_name = f"{student['roll_no']}. {student_name}"
                                
                            status = st.selectbox(
                                student_name,
                                status_options,
                                index=0,  # Default to 'present'
                                key=f"status_{student['id']}"
                            )
                            
                            attendance_data.append({
                                'student_id': student['id'],
                                'status': status
                            })
                    
                    # Add a divider and submit button
                    st.markdown("---")
                    remarks = st.text_area("Remarks (Optional)", key="attendance_remarks")
                    
                    if st.form_submit_button("Submit Attendance"):
                        success_count = 0
                        try:
                            for record in attendance_data:
                                conn.execute("""
                                    INSERT INTO attendance 
                                    (student_id, date, status, remarks, created_at)
                                    VALUES (?, ?, ?, ?, ?)
                                """, (
                                    record['student_id'],
                                    attendance_date,
                                    record['status'],
                                    remarks,
                                    datetime.now()
                                ))
                                success_count += 1
                            
                            conn.commit()
                            st.success(f"✅ Attendance recorded for {success_count} students!")
                        except Exception as e:
                            conn.rollback()
                            st.error(f"❌ Error saving attendance: {str(e)}")
                
                # Display today's attendance
                st.subheader("Today's Attendance")
                today = datetime.now().strftime('%Y-%m-%d')
                attendance = conn.execute("""
                    SELECT s.first_name, s.last_name, s.roll_no, a.status, a.remarks
                    FROM attendance a
                    JOIN students s ON a.student_id = s.id
                    WHERE DATE(a.date) = ? 
                    AND s.class_name = ? 
                    AND s.section = ?
                    ORDER BY s.roll_no, s.first_name
                """, (today, selected_class, selected_section)).fetchall()
                
                if attendance:
                    attendance_list = []
                    for att in attendance:
                        attendance_list.append({
                            'Roll No': att['roll_no'] or '',
                            'Name': f"{att['first_name']} {att['last_name']}",
                            'Status': att['status'].capitalize(),
                            'Remarks': att['remarks'] or ''
                        })
                    
                    st.table(attendance_list)
                else:
                    st.info("No attendance recorded for today.")
                    
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
    finally:
        conn.close()

# This allows the page to be run directly for testing
if __name__ == "__main__":
    show()