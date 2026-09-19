import streamlit as st
import pandas as pd
from datetime import date

import auth
import crud
import reports
from database import init_database, test_connection
from styles import inject_css, page_header, metric_card

PROGRAMMES = [
    "BCS - Bachelor of Computer Science",
    "BCSE - Bachelor of Computer Science and Engineering",
    "BISNE - Bachelor of Information Systems and Network Engineering",
    "BEd - Bachelor of Education",
]

SEMESTERS = ["Semester 1", "Semester 2"]

ASSESSMENT_TYPES = [
    "Assignment 1", "Assignment 2",
    "Test 1", "Test 2",
    "Practical 1", "Practical 2",
    "UE",
]

st.set_page_config(
    page_title="Student Management System",
    page_icon="🎓",
    layout="wide",
)
inject_css()


@st.cache_resource
def setup():
    init_database()
    return True


try:
    setup()
    DB_READY = True
except Exception as e:
    DB_READY = False
    DB_ERROR = str(e)


def show_login():
    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.3, 1])
    with col2:
        st.markdown('<div class="login-wrapper">', unsafe_allow_html=True)
        st.markdown('<div class="login-title">🎓 Student Management System</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Sign in to continue</div>', unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Staff Login", "Student Login"])

        with tab1:
            with st.form("staff_login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("Login", use_container_width=True)

                if submitted:
                    if auth.login(username, password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect username or password.")

        with tab2:
            with st.form("student_login_form"):
                reg_no = st.text_input("Registration No")
                student_password = st.text_input("Password", type="password", key="student_pw")
                student_submitted = st.form_submit_button("Login", use_container_width=True)

                if student_submitted:
                    if auth.login_student(reg_no, student_password):
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Incorrect registration number or password.")

        st.markdown("</div>", unsafe_allow_html=True)


def show_dashboard():
    page_header("OVERVIEW", "Dashboard")
    stats = crud.get_dashboard_stats()

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("Total Students", stats["students"]), unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Total Courses", stats["courses"]), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Mark Records", stats["marks"]), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.subheader("Recently Registered Students")
    students = crud.get_all_students()
    if students:
        df = pd.DataFrame(students)[["registration_no", "full_name", "programme", "date_registered"]]
        df.columns = ["Registration No", "Name", "Programme", "Date Registered"]
        st.dataframe(df.head(8), use_container_width=True, hide_index=True)
    else:
        st.info("No students registered yet.")


def show_students():
    page_header("MANAGEMENT", "Students")

    tab1, tab2 = st.tabs(["📋 Student List", "➕ Add Student"])

    with tab1:
        keyword = st.text_input("🔍 Search by name or registration number")
        rows = crud.search_students(keyword) if keyword else crud.get_all_students()

        if rows:
            df = pd.DataFrame(rows)
            display_df = df[["id", "registration_no", "full_name", "gender", "programme", "phone", "email"]]
            display_df.columns = ["ID", "Registration No", "Name", "Gender", "Programme", "Phone", "Email"]
            st.dataframe(display_df, use_container_width=True, hide_index=True)

            st.markdown("#### Edit or Delete Student")
            ids = [r["id"] for r in rows]
            labels = {r["id"]: f'{r["full_name"]} ({r["registration_no"]})' for r in rows}
            selected_id = st.selectbox("Select student", ids, format_func=lambda x: labels[x])
            student = crud.get_student_by_id(selected_id)

            with st.form("edit_student_form"):
                col1, col2 = st.columns(2)
                with col1:
                    reg_no = st.text_input("Registration No", value=student["registration_no"])
                    full_name = st.text_input("Full Name", value=student["full_name"])
                    gender = st.selectbox("Gender", ["Male", "Female"], index=0 if student["gender"] == "Male" else 1)
                    dob = st.date_input("Date of Birth", value=student["date_of_birth"] or date(2010, 1, 1))
                with col2:
                    current_programme = student["programme"] or PROGRAMMES[0]
                    prog_index = PROGRAMMES.index(current_programme) if current_programme in PROGRAMMES else 0
                    programme = st.selectbox("Programme", PROGRAMMES, index=prog_index)
                    phone = st.text_input("Phone", value=student["phone"] or "")
                    email = st.text_input("Email", value=student["email"] or "")
                    address = st.text_input("Address", value=student["address"] or "")

                c1, c2 = st.columns(2)
                with c1:
                    update_btn = st.form_submit_button("💾 Save Changes", use_container_width=True)
                with c2:
                    delete_btn = st.form_submit_button("🗑️ Delete Student", use_container_width=True)

                if update_btn:
                    crud.update_student(selected_id, reg_no, full_name, gender, dob,
                                         programme, phone, email, address)
                    st.success("Student updated.")
                    st.rerun()

                if delete_btn:
                    crud.delete_student(selected_id)
                    st.success("Student deleted.")
                    st.rerun()

            if st.button("🔑 Reset Student Password to Default (1234)"):
                crud.change_student_password(selected_id, "1234")
                st.success("Password reset to 1234.")

            st.markdown("#### Academic Summary")
            average, total_marks = crud.get_average_for_student(selected_id)
            att_total, att_present, att_pct = crud.get_attendance_summary_for_student(selected_id)

            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown(metric_card("Overall Average",
                                         f"{average}%" if average is not None else "N/A"),
                            unsafe_allow_html=True)
            with sc2:
                st.markdown(metric_card("Assessments Recorded", total_marks), unsafe_allow_html=True)
            with sc3:
                st.markdown(metric_card("Attendance",
                                         f"{att_pct}%" if att_pct is not None else "N/A"),
                            unsafe_allow_html=True)

            marks = crud.get_marks_for_student(selected_id)
            if marks:
                mdf = pd.DataFrame(marks)[["course_name", "semester", "assessment_type", "year", "score"]]
                mdf.columns = ["Course", "Semester", "Assessment", "Year", "Score"]
                st.dataframe(mdf, use_container_width=True, hide_index=True)
            else:
                st.caption("No marks recorded for this student yet.")

            avg_by_course = crud.get_average_by_course_for_student(selected_id)
            pdf_bytes = reports.generate_student_report_pdf(
                student, marks, average, total_marks, avg_by_course,
                att_total, att_present, att_pct
            )
            st.download_button(
                "📄 Download Student Report (PDF)",
                data=pdf_bytes,
                file_name=f"{student['registration_no']}_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
        else:
            st.info("No students match your search.")

    with tab2:
        with st.form("add_student_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            with col1:
                reg_no = st.text_input("Registration No *")
                full_name = st.text_input("Full Name *")
                gender = st.selectbox("Gender", ["Male", "Female"])
                dob = st.date_input("Date of Birth", value=date(2010, 1, 1))
            with col2:
                programme = st.selectbox("Programme", PROGRAMMES)
                phone = st.text_input("Phone")
                email = st.text_input("Email")
                address = st.text_input("Address")

            submitted = st.form_submit_button("➕ Add Student", use_container_width=True)
            if submitted:
                if not reg_no or not full_name:
                    st.error("Registration No and Name are required.")
                else:
                    try:
                        crud.add_student(reg_no, full_name, gender, dob, programme, phone, email, address)
                        st.success(f"Student '{full_name}' added. Default login password is 1234.")
                    except Exception as e:
                        st.error(f"Failed: {e}")


def show_courses():
    page_header("MANAGEMENT", "Courses")

    tab1, tab2 = st.tabs(["📚 Course List", "➕ Add Course"])

    with tab1:
        courses = crud.get_all_courses()
        if courses:
            df = pd.DataFrame(courses)
            df.columns = ["ID", "Code", "Course Name"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            ids = [c["id"] for c in courses]
            labels = {c["id"]: f'{c["course_name"]} ({c["course_code"]})' for c in courses}
            selected_id = st.selectbox("Select course to delete", ids, format_func=lambda x: labels[x])
            if st.button("🗑️ Delete This Course"):
                crud.delete_course(selected_id)
                st.success("Course deleted.")
                st.rerun()
        else:
            st.info("No courses added yet.")

    with tab2:
        with st.form("add_course_form", clear_on_submit=True):
            code = st.text_input("Course Code (e.g. CS101) *")
            name = st.text_input("Course Name *")
            submitted = st.form_submit_button("➕ Add Course", use_container_width=True)
            if submitted:
                if not code or not name:
                    st.error("Code and Name are required.")
                else:
                    try:
                        crud.add_course(code, name)
                        st.success(f"Course '{name}' added.")
                    except Exception as e:
                        st.error(f"Failed: {e}")


def show_marks():
    page_header("MANAGEMENT", "Student Marks")

    students = crud.get_all_students()
    courses = crud.get_all_courses()

    if not students or not courses:
        st.warning("Make sure you have at least one student and one course before recording marks.")
        return

    with st.form("add_mark_form", clear_on_submit=True):
        student_labels = {s["id"]: f'{s["full_name"]} ({s["registration_no"]})' for s in students}
        course_labels = {c["id"]: f'{c["course_name"]} ({c["course_code"]})' for c in courses}

        col1, col2 = st.columns(2)
        with col1:
            student_id = st.selectbox("Student", list(student_labels.keys()), format_func=lambda x: student_labels[x])
            course_id = st.selectbox("Course", list(course_labels.keys()), format_func=lambda x: course_labels[x])
            semester = st.selectbox("Semester", SEMESTERS)
        with col2:
            assessment_type = st.selectbox("Assessment Type", ASSESSMENT_TYPES)
            year = st.number_input("Year", min_value=2000, max_value=2100, value=date.today().year)
            score = st.number_input("Score", min_value=0.0, max_value=100.0, value=0.0, step=0.5, format="%.2f")

        submitted = st.form_submit_button("➕ Record Mark", use_container_width=True)
        if submitted:
            crud.add_mark(student_id, course_id, semester, assessment_type, year, score)
            st.success("Mark recorded.")

    st.markdown("---")
    st.subheader("View a Student's Marks")
    student_labels = {s["id"]: f'{s["full_name"]} ({s["registration_no"]})' for s in students}
    selected_id = st.selectbox("Select student", list(student_labels.keys()),
                                format_func=lambda x: student_labels[x], key="view_marks_select")

    average, total_marks = crud.get_average_for_student(selected_id)
    st.markdown(metric_card("Overall Average", f"{average}%" if average is not None else "N/A"),
                unsafe_allow_html=True)

    marks = crud.get_marks_for_student(selected_id)
    if marks:
        df = pd.DataFrame(marks)[["id", "course_name", "semester", "assessment_type", "year", "score"]]
        df.columns = ["ID", "Course", "Semester", "Assessment", "Year", "Score"]
        st.dataframe(df, use_container_width=True, hide_index=True)

        mark_ids = [m["id"] for m in marks]
        mark_id_to_delete = st.selectbox("Delete a mark record (select ID)", mark_ids, key="delete_mark_select")
        if st.button("🗑️ Delete This Record"):
            crud.delete_mark(mark_id_to_delete)
            st.success("Record deleted.")
            st.rerun()
    else:
        st.caption("No marks for this student yet.")


def show_attendance():
    page_header("MANAGEMENT", "Attendance")

    students = crud.get_all_students()
    courses = crud.get_all_courses()

    if not students or not courses:
        st.warning("Make sure you have at least one student and one course before marking attendance.")
        return

    tab1, tab2 = st.tabs(["✅ Mark Attendance", "📖 View Student Attendance"])

    with tab1:
        course_labels = {c["id"]: f'{c["course_name"]} ({c["course_code"]})' for c in courses}
        col1, col2 = st.columns(2)
        with col1:
            course_id = st.selectbox("Course", list(course_labels.keys()), format_func=lambda x: course_labels[x])
        with col2:
            attendance_date = st.date_input("Date", value=date.today())

        with st.form("attendance_form"):
            st.caption("Mark each student's status for this class session.")
            status_map = {}
            for s in students:
                status_map[s["id"]] = st.radio(
                    f'{s["full_name"]} ({s["registration_no"]})',
                    ["Present", "Absent"],
                    horizontal=True,
                    key=f'att_{s["id"]}',
                )

            submitted = st.form_submit_button("💾 Save Attendance", use_container_width=True)
            if submitted:
                for student_id, status in status_map.items():
                    crud.add_attendance(student_id, course_id, attendance_date, status)
                st.success("Attendance saved for all students.")

    with tab2:
        student_labels = {s["id"]: f'{s["full_name"]} ({s["registration_no"]})' for s in students}
        selected_id = st.selectbox("Select student", list(student_labels.keys()),
                                    format_func=lambda x: student_labels[x], key="view_att_select")

        total, present, pct = crud.get_attendance_summary_for_student(selected_id)
        st.markdown(metric_card("Attendance Rate", f"{pct}%" if pct is not None else "N/A"),
                    unsafe_allow_html=True)

        records = crud.get_attendance_for_student(selected_id)
        if records:
            df = pd.DataFrame(records)[["id", "course_name", "attendance_date", "status"]]
            df.columns = ["ID", "Course", "Date", "Status"]
            st.dataframe(df, use_container_width=True, hide_index=True)

            record_ids = [r["id"] for r in records]
            record_to_delete = st.selectbox("Delete a record (select ID)", record_ids, key="delete_att_select")
            if st.button("🗑️ Delete This Record"):
                crud.delete_attendance(record_to_delete)
                st.success("Record deleted.")
                st.rerun()
        else:
            st.caption("No attendance records for this student yet.")


def show_reports():
    page_header("REPORTS", "Reports & Exports")

    st.subheader("All Students (Excel)")
    students = crud.get_all_students()
    if students:
        excel_bytes = reports.generate_students_excel(students)
        st.download_button(
            "📊 Download All Students (Excel)",
            data=excel_bytes,
            file_name="students.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
    else:
        st.info("No students to export yet.")

    st.markdown("---")
    st.subheader("Individual Student Report (PDF)")
    if students:
        student_labels = {s["id"]: f'{s["full_name"]} ({s["registration_no"]})' for s in students}
        selected_id = st.selectbox("Select student", list(student_labels.keys()),
                                    format_func=lambda x: student_labels[x], key="report_student_select")
        student = crud.get_student_by_id(selected_id)
        marks = crud.get_marks_for_student(selected_id)
        average, total_marks = crud.get_average_for_student(selected_id)
        avg_by_course = crud.get_average_by_course_for_student(selected_id)
        att_total, att_present, att_pct = crud.get_attendance_summary_for_student(selected_id)

        pdf_bytes = reports.generate_student_report_pdf(
            student, marks, average, total_marks, avg_by_course,
            att_total, att_present, att_pct
        )
        st.download_button(
            "📄 Download Report (PDF)",
            data=pdf_bytes,
            file_name=f"{student['registration_no']}_report.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
    else:
        st.info("No students available.")


def show_users():
    page_header("MANAGEMENT (ADMIN)", "System Users")

    tab1, tab2 = st.tabs(["👤 User List", "➕ Add User"])

    with tab1:
        users = crud.get_all_users()
        for u in users:
            badge_class = "badge-admin" if u["role"] == "admin" else "badge-teacher"
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                st.markdown(
                    f'**{u["full_name"] or u["username"]}** &nbsp; '
                    f'<span class="{badge_class}">{u["role"].upper()}</span>',
                    unsafe_allow_html=True,
                )
                st.caption(f'Username: {u["username"]}')
            with col2:
                st.caption(str(u["date_created"]))
            with col3:
                if u["username"] != "admin":
                    if st.button("Delete", key=f'del_user_{u["id"]}'):
                        crud.delete_user(u["id"])
                        st.rerun()
            st.divider()

    with tab2:
        with st.form("add_user_form", clear_on_submit=True):
            full_name = st.text_input("Full Name")
            username = st.text_input("Username *")
            password = st.text_input("Password *", type="password")
            role = st.selectbox("Role", ["teacher", "admin"])
            submitted = st.form_submit_button("➕ Add User", use_container_width=True)
            if submitted:
                if not username or not password:
                    st.error("Username and Password are required.")
                else:
                    try:
                        crud.add_user(username, password, full_name, role)
                        st.success(f"User '{username}' added.")
                    except Exception as e:
                        st.error(f"Failed: {e}")


def show_student_home():
    page_header("MY ACCOUNT", "My Results")

    student_id = st.session_state["student_id"]
    student = crud.get_student_by_id(student_id)

    st.markdown("#### My Profile")
    pcol1, pcol2 = st.columns(2)
    with pcol1:
        st.markdown(f"**Full Name:** {student['full_name']}")
        st.markdown(f"**Registration No:** {student['registration_no']}")
        st.markdown(f"**Programme:** {student['programme'] or '-'}")
    with pcol2:
        st.markdown(f"**Gender:** {student['gender']}")
        st.markdown(f"**Phone:** {student['phone'] or '-'}")
        st.markdown(f"**Email:** {student['email'] or '-'}")

    st.markdown("#### Academic Summary")
    average, total_marks = crud.get_average_for_student(student_id)
    att_total, att_present, att_pct = crud.get_attendance_summary_for_student(student_id)

    sc1, sc2, sc3 = st.columns(3)
    with sc1:
        st.markdown(metric_card("Overall Average",
                                 f"{average}%" if average is not None else "N/A"),
                    unsafe_allow_html=True)
    with sc2:
        st.markdown(metric_card("Assessments Recorded", total_marks), unsafe_allow_html=True)
    with sc3:
        st.markdown(metric_card("Attendance",
                                 f"{att_pct}%" if att_pct is not None else "N/A"),
                    unsafe_allow_html=True)

    avg_by_course = crud.get_average_by_course_for_student(student_id)
    if avg_by_course:
        st.markdown("#### Average by Course")
        acdf = pd.DataFrame(avg_by_course)
        acdf["avg_score"] = acdf["avg_score"].astype(float).round(2)
        acdf = acdf[["course_name", "avg_score", "total"]]
        acdf.columns = ["Course", "Average Score", "Assessments"]
        st.dataframe(acdf, use_container_width=True, hide_index=True)

    marks = crud.get_marks_for_student(student_id)
    st.markdown("#### My Marks")
    if marks:
        mdf = pd.DataFrame(marks)[["course_name", "semester", "assessment_type", "year", "score"]]
        mdf.columns = ["Course", "Semester", "Assessment", "Year", "Score"]
        st.dataframe(mdf, use_container_width=True, hide_index=True)
    else:
        st.caption("No marks recorded yet.")

    pdf_bytes = reports.generate_student_report_pdf(
        student, marks, average, total_marks, avg_by_course,
        att_total, att_present, att_pct
    )
    st.download_button(
        "📄 Download My Report (PDF)",
        data=pdf_bytes,
        file_name=f"{student['registration_no']}_report.pdf",
        mime="application/pdf",
        use_container_width=True,
    )


def show_student_attendance_page():
    page_header("MY ACCOUNT", "My Attendance")

    student_id = st.session_state["student_id"]
    total, present, pct = crud.get_attendance_summary_for_student(student_id)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(metric_card("Attendance Rate", f"{pct}%" if pct is not None else "N/A"),
                    unsafe_allow_html=True)
    with c2:
        st.markdown(metric_card("Sessions Present", present), unsafe_allow_html=True)
    with c3:
        st.markdown(metric_card("Total Sessions", total), unsafe_allow_html=True)

    records = crud.get_attendance_for_student(student_id)
    if records:
        df = pd.DataFrame(records)[["course_name", "attendance_date", "status"]]
        df.columns = ["Course", "Date", "Status"]
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No attendance records yet.")


def show_student_change_password():
    page_header("MY ACCOUNT", "Change Password")

    student_id = st.session_state["student_id"]
    student = crud.get_student_by_id(student_id)

    with st.form("student_change_password_form", clear_on_submit=True):
        current_password = st.text_input("Current Password", type="password")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        submitted = st.form_submit_button("🔑 Update Password", use_container_width=True)

        if submitted:
            if not auth.verify_password(current_password, student["password"]):
                st.error("Current password is incorrect.")
            elif not new_password:
                st.error("New password cannot be empty.")
            elif new_password != confirm_password:
                st.error("New passwords do not match.")
            else:
                crud.change_student_password(student_id, new_password)
                st.success("Password updated successfully.")


def show_sidebar():
    with st.sidebar:
        st.markdown("## 🎓 SMS")
        st.markdown(f'**{st.session_state.get("full_name") or st.session_state.get("username")}**')
        role = st.session_state.get("role")
        badge_class = {
            "admin": "badge-admin",
            "teacher": "badge-teacher",
            "student": "badge-student",
        }.get(role, "badge-teacher")
        st.markdown(f'<span class="{badge_class}">{role.upper()}</span>', unsafe_allow_html=True)
        st.markdown("---")

        if role == "student":
            options = ["My Results", "My Attendance", "Change Password"]
            icons = {"My Results": "📊", "My Attendance": "✅", "Change Password": "🔑"}
        else:
            options = ["Dashboard", "Students", "Courses", "Marks", "Attendance", "Reports"]
            icons = {
                "Dashboard": "📊", "Students": "🧑‍🎓", "Courses": "📚",
                "Marks": "📝", "Attendance": "✅", "Reports": "📄",
            }
            if auth.is_admin():
                options.append("Users")
                icons["Users"] = "👥"

        labels = [f"{icons[o]}  {o}" for o in options]
        choice = st.radio("Menu", labels, label_visibility="collapsed")
        page = options[labels.index(choice)]

        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True):
            auth.logout()
            st.rerun()

        return page


def main():
    if not DB_READY:
        st.error(
            "Could not connect to the MySQL database.\n\n"
            f"Error: {DB_ERROR}\n\n"
            "Check your settings in config.py (host, user, password) "
            "and make sure the MySQL server is running."
        )
        return

    if not auth.is_logged_in():
        show_login()
        return

    page = show_sidebar()

    if auth.is_student():
        if page == "My Results":
            show_student_home()
        elif page == "My Attendance":
            show_student_attendance_page()
        elif page == "Change Password":
            show_student_change_password()
        return

    if page == "Dashboard":
        show_dashboard()
    elif page == "Students":
        show_students()
    elif page == "Courses":
        show_courses()
    elif page == "Marks":
        show_marks()
    elif page == "Attendance":
        show_attendance()
    elif page == "Reports":
        show_reports()
    elif page == "Users":
        auth.require_login()
        if auth.is_admin():
            show_users()
        else:
            st.error("You don't have permission to access this page.")


if __name__ == "__main__":
    main()