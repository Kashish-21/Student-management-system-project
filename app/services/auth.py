# app/services/auth.py
import streamlit as st
import hashlib
from datetime import datetime
from app.utils.db import get_db_connection

def login():
    st.title("🔐 Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.form_submit_button("Login"):
            conn = get_db_connection()
            user = conn.execute(
                "SELECT * FROM users WHERE username = ? AND is_active = 1",
                (username,)
            ).fetchone()
            
            if user and check_password(user['password'], password):
                st.session_state.authenticated = True
                st.session_state.user = {
                    'id': user[0],
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user['full_name'],
                    'role': user['role']
                }
                # Update last login
                conn.execute(
                    "UPDATE users SET last_login = ? WHERE id = ?",
                    (datetime.now(), user[0])
                )
                conn.commit()
                conn.close()
                st.experimental_rerun()  # Changed from st.rerun()
            else:
                st.error("Invalid username or password")
                conn.close()
                
def logout():
    st.session_state.authenticated = False
    st.session_state.user = None

def is_authenticated():
    return st.session_state.get('authenticated', False)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed_password, user_password):
    return hashed_password == hashlib.sha256(user_password.encode()).hexdigest()

def check_auth():
    if not is_authenticated():
        st.warning("Please log in to access this page.")
        login()
        st.stop()

def get_current_user():
    """Get the current logged-in user's information."""
    if not is_authenticated():
        return None
    return st.session_state.user