import bcrypt
import streamlit as st
from database import get_connection


def hash_password(plain_password):
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def get_student_by_registration_no(registration_no):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE registration_no = %s", (registration_no,))
    student = cursor.fetchone()
    cursor.close()
    conn.close()
    return student


def login(username, password):
    user = get_user_by_username(username)
    if user and verify_password(password, user["password"]):
        st.session_state["logged_in"] = True
        st.session_state["user_id"] = user["id"]
        st.session_state["username"] = user["username"]
        st.session_state["full_name"] = user["full_name"]
        st.session_state["role"] = user["role"]
        return True
    return False


def login_student(registration_no, password):
    student = get_student_by_registration_no(registration_no)
    if student and student["password"] and verify_password(password, student["password"]):
        st.session_state["logged_in"] = True
        st.session_state["student_id"] = student["id"]
        st.session_state["username"] = student["registration_no"]
        st.session_state["full_name"] = student["full_name"]
        st.session_state["role"] = "student"
        return True
    return False


def logout():
    for key in ["logged_in", "user_id", "student_id", "username", "full_name", "role"]:
        st.session_state.pop(key, None)


def is_logged_in():
    return st.session_state.get("logged_in", False)


def is_admin():
    return st.session_state.get("role") == "admin"


def is_student():
    return st.session_state.get("role") == "student"


def require_login():
    if not is_logged_in():
        st.warning("Please log in first to access this page.")
        st.stop()