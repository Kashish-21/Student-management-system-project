import streamlit as st
import sqlite3
import hashlib
from streamlit_option_menu import option_menu

# Initialize database
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    # Create users table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create default admin if not exists
    c.execute("SELECT * FROM users WHERE username = 'admin'")
    if not c.fetchone():
        hashed_password = hash_password('admin123')
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            ('admin', hashed_password, 'admin')
        )
    
    conn.commit()
    return conn

# Password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Authentication functions
def signup_user(conn, username, password, role):
    try:
        hashed_password = hash_password(password)
        c = conn.cursor()
        c.execute(
            "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, hashed_password, role)
        )
        conn.commit()
        return True, "User created successfully!"
    except sqlite3.IntegrityError:
        return False, "Username already exists"
    except Exception as e:
        return False, f"Error: {str(e)}"

def verify_user(conn, username, password):
    c = conn.cursor()
    c.execute(
        "SELECT * FROM users WHERE username = ?",
        (username,)
    )
    user = c.fetchone()
    
    if user and user[2] == hash_password(password):
        return True, {
            'user_id': user[0],
            'username': user[1],
            'role': user[3]
        }
    return False, "Invalid username or password"

# UI Components
def login_page(conn):
    st.title("🔑 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if not username or not password:
                st.error("Please enter both username and password")
            else:
                success, result = verify_user(conn, username, password)
                if success:
                    st.session_state.authenticated = True
                    st.session_state.user = result
                    st.rerun()
                else:
                    st.error(result)

def signup_page(conn):
    st.title("👤 Create New Account")
    
    # Check if admin is logged in
    is_admin = 'user' in st.session_state and st.session_state.user.get('role') == 'admin'
    
    with st.form("signup_form", clear_on_submit=True):
        st.subheader("Create New Account")
        
        # Form layout in two columns
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("Username", help="Must be unique, 3-20 characters, letters and numbers only")
        
        with col2:
            password = st.text_input("Password", type="password", 
                                   help="At least 8 characters, include numbers and special characters")
        
        # Second row
        col3, col4 = st.columns(2)
        
        with col3:
            confirm_password = st.text_input("Confirm Password", type="password")
        
        with col4:
            # Role selection
            if is_admin:
                role_options = ["teacher", "admin"]
                role_help = "Select the type of account to create"
            else:
                role_options = ["teacher"]
                role_help = "Teacher account (Only admins can create admin accounts)"
                
            role = st.selectbox(
                "Account Type",
                role_options,
                format_func=lambda x: x.capitalize(),
                index=0,
                help=role_help
            )
        
        # Form submission
        submitted = st.form_submit_button("Create Account", type="primary", use_container_width=True)
        
        if submitted:
            # Validation
            if not username or not password or not confirm_password:
                st.error("❌ Please fill in all fields")
                return
                
            if not username.isalnum() or len(username) < 3 or len(username) > 20:
                st.error("❌ Username must be 3-20 alphanumeric characters")
                return
                
            if len(password) < 8:
                st.error("❌ Password must be at least 8 characters long")
                return
                
            if password != confirm_password:
                st.error("❌ Passwords do not match")
                return
                
            # Check username uniqueness
            existing_user = conn.execute(
                "SELECT username FROM users WHERE username = ?", 
                (username,)
            ).fetchone()
            
            if existing_user:
                st.error("❌ Username already exists")
                return
            
            # Create user
            success, message = signup_user(conn, username, password, role)
            if success:
                st.success(f"✅ {message}")
                if not is_admin:
                    st.session_state.show_signup = False
                    st.rerun()
            else:
                st.error(f"❌ {message}")

# Main application
def main():
    st.set_page_config(
        page_title="Student Management System",
        page_icon="🎓",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'show_signup' not in st.session_state:
        st.session_state.show_signup = False
    
    # Initialize database
    conn = init_db()
    
    # Show login/signup if not authenticated
    if not st.session_state.authenticated:
        if st.session_state.show_signup:
            signup_page(conn)
            if st.button("Back to Login"):
                st.session_state.show_signup = False
                st.rerun()
        else:
            login_page(conn)
            if st.button("Create New Account"):
                st.session_state.show_signup = True
                st.rerun()
        return
    
    # User is authenticated, show main app
    user = st.session_state.user
    
    # Sidebar navigation
    with st.sidebar:
        st.title(f"🎓 {user['role'].capitalize()} Panel")
        
        # Menu options based on role
        if user['role'] == 'admin':
            menu_options = ["Dashboard", "Manage Students", "Attendance", "Reports", "User Management"]
            icons = ["speedometer", "people", "calendar-check", "file-earmark-bar-graph", "person-gear"]
        else:  # teacher
            menu_options = ["Dashboard", "Attendance", "Reports"]
            icons = ["speedometer", "calendar-check", "file-earmark-bar-graph"]
            
        menu = option_menu(
            menu_title=None,
            options=menu_options,
            icons=icons,
            default_index=0,
            styles={
                "container": {"padding": "0!important"},
                "nav-link": {
                    "font-size": "14px", 
                    "text-align": "left", 
                    "margin": "0px", 
                    "--hover-color": "#4CAF50"
                },
                "nav-link-selected": {"background-color": "#4CAF50"}
            }
        )
        
        st.markdown("---")
        st.markdown(f"### Welcome, {user['username']}")
        
        if st.button("🚪 Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content
    if menu == "Dashboard":
        st.title("📊 Dashboard")
        st.write(f"Welcome to the {user['role'].capitalize()} Dashboard")
        
    elif menu == "Manage Students" and user['role'] == 'admin':
        st.title("👥 Manage Students")
        st.write("Student management interface will be here")
        
    elif menu == "Attendance":
        st.title("📅 Attendance")
        st.write("Attendance management interface will be here")
        
    elif menu == "Reports":
        st.title("📊 Reports")
        st.write("Reports interface will be here")
        
    elif menu == "User Management" and user['role'] == 'admin':
        st.title("👥 User Management")
        
        # List all users
        st.subheader("All Users")
        users = conn.execute("SELECT user_id, username, role FROM users").fetchall()
        if users:
            user_data = [{"ID": user[0], "Username": user[1], "Role": user[2]} for user in users]
            st.table(user_data)
        else:
            st.info("No users found")
        
        # Add new user (admin only)
        with st.expander("➕ Add New User", expanded=True):
            with st.form("add_user_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_username = st.text_input("New Username", key="new_username")
                    new_password = st.text_input("New Password", type="password", key="new_password")
                with col2:
                    new_role = st.radio("Role", ["teacher", "admin"], horizontal=True, key="new_role")
                
                if st.form_submit_button("Add User", type="primary"):
                    if new_username and new_password:
                        success, message = signup_user(conn, new_username, new_password, new_role)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all fields")
    
    conn.close()

if __name__ == "__main__":
    main()