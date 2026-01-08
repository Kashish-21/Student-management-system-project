# app.py
import streamlit as st
import os
from dotenv import load_dotenv
from app.utils.db import init_db, get_db_connection
from app.services.auth import login, logout, is_authenticated
from app.pages.settings import show as show_settings

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if 'db_initialized' not in st.session_state:
    init_db()
    st.session_state.db_initialized = True

# Session state management
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.user = None

# Main app logic
def main():
    if not st.session_state.authenticated:
        login()
    else:
        show_sidebar()
        show_main_content()

def show_sidebar():
    with st.sidebar:
        st.title("🎓 SMS Pro")
        
        # Navigation
        page = st.radio(
            "Menu",
            ["Dashboard", "Students", "Teachers", "Academics", "Attendance", "Settings"],
            key="menu"
        )
        
        # User info
        st.markdown("---")
        st.markdown(f"### {st.session_state.user['full_name']}")
        st.caption(f"Role: {st.session_state.user['role'].title()}")
        
        if st.button("🚪 Logout"):
            logout()
            st.rerun()

def show_main_content():
    # Route to the selected page
    if st.session_state.menu == "Dashboard":
        from app.pages import dashboard
        dashboard.show()
    elif st.session_state.menu == "Students":
        from app.pages import students
        students.show()
    elif st.session_state.menu == "Teachers":
        from app.pages import teachers
        teachers.show()
    elif st.session_state.menu == "Academics":
        from app.pages import academics
        academics.show()
    elif st.session_state.menu == "Attendance":
        from app.pages import attendance
        attendance.show()
    else:  # Settings
        from app.pages import settings
        settings.show()

if __name__ == "__main__":
    main()