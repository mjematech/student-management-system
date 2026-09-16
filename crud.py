from database import get_connection
from auth import hash_password
from mysql.connector.errors import IntegrityError


def add_user(username, plain_password, full_name, role):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (username, password, full_name, role)
        VALUES (%s, %s, %s, %s)
    """, (username, hash_password(plain_password), full_name, role))
    conn.commit()
    cursor.close()
    conn.close()


def get_all_users():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, username, full_name, role, date_created FROM users ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def delete_user(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
    conn.commit()
    cursor.close()
    conn.close()


def change_password(user_id, new_plain_password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET password = %s WHERE id = %s",
        (hash_password(new_plain_password), user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()


def add_student(registration_no, full_name, gender, dob, programme,
                 phone, email, address):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO students
            (registration_no, full_name, gender, date_of_birth,
             programme, phone, email, address)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (registration_no, full_name, gender, dob, programme,
          phone, email, address))
    conn.commit()
    cursor.close()
    conn.close()


def get_all_students():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def search_students(keyword):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    like = f"%{keyword}%"
    cursor.execute("""
        SELECT * FROM students
        WHERE full_name LIKE %s OR registration_no LIKE %s
        ORDER BY id DESC
    """, (like, like))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_student_by_id(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students WHERE id = %s", (student_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    return row


def update_student(student_id, registration_no, full_name, gender, dob,
                    programme, phone, email, address):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE students SET
            registration_no=%s, full_name=%s, gender=%s, date_of_birth=%s,
            programme=%s, phone=%s, email=%s, address=%s
        WHERE id=%s
    """, (registration_no, full_name, gender, dob, programme,
          phone, email, address, student_id))
    conn.commit()
    cursor.close()
    conn.close()


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE id = %s", (student_id,))
    conn.commit()
    cursor.close()
    conn.close()


def add_course(course_code, course_name):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO courses (course_code, course_name) VALUES (%s, %s)",
        (course_code, course_name)
    )
    conn.commit()
    cursor.close()
    conn.close()


def get_all_courses():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM courses ORDER BY id DESC")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def delete_course(course_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM courses WHERE id = %s", (course_id,))
    conn.commit()
    cursor.close()
    conn.close()


def add_mark(student_id, course_id, semester, assessment_type, year, score):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO marks (student_id, course_id, semester, assessment_type, year, score)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (student_id, course_id, semester, assessment_type, year, score))
    conn.commit()
    cursor.close()
    conn.close()


def get_marks_for_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT m.id, c.course_name, m.semester, m.assessment_type, m.year, m.score
        FROM marks m
        JOIN courses c ON m.course_id = c.id
        WHERE m.student_id = %s
        ORDER BY m.year DESC, m.semester, m.assessment_type
    """, (student_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def delete_mark(mark_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM marks WHERE id = %s", (mark_id,))
    conn.commit()
    cursor.close()
    conn.close()


def get_average_for_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT AVG(score) AS avg_score, COUNT(*) AS total FROM marks WHERE student_id = %s",
        (student_id,)
    )
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row and row["avg_score"] is not None:
        return round(float(row["avg_score"]), 2), row["total"]
    return None, 0


def get_average_by_course_for_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.course_name, AVG(m.score) AS avg_score, COUNT(*) AS total
        FROM marks m
        JOIN courses c ON m.course_id = c.id
        WHERE m.student_id = %s
        GROUP BY c.course_name
        ORDER BY c.course_name
    """, (student_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def add_attendance(student_id, course_id, attendance_date, status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO attendance (student_id, course_id, attendance_date, status)
            VALUES (%s, %s, %s, %s)
        """, (student_id, course_id, attendance_date, status))
    except IntegrityError:
        cursor.execute("""
            UPDATE attendance SET status = %s
            WHERE student_id = %s AND course_id = %s AND attendance_date = %s
        """, (status, student_id, course_id, attendance_date))
    conn.commit()
    cursor.close()
    conn.close()


def get_attendance_for_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, c.course_name, a.attendance_date, a.status
        FROM attendance a
        JOIN courses c ON a.course_id = c.id
        WHERE a.student_id = %s
        ORDER BY a.attendance_date DESC
    """, (student_id,))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


def get_attendance_summary_for_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) AS present_count
        FROM attendance
        WHERE student_id = %s
    """, (student_id,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    total = row["total"] or 0
    present = row["present_count"] or 0
    percentage = round((present / total) * 100, 1) if total > 0 else None
    return total, present, percentage


def delete_attendance(attendance_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM attendance WHERE id = %s", (attendance_id,))
    conn.commit()
    cursor.close()
    conn.close()


def get_dashboard_stats():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT COUNT(*) AS total FROM students")
    total_students = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM courses")
    total_courses = cursor.fetchone()["total"]
    cursor.execute("SELECT COUNT(*) AS total FROM marks")
    total_marks = cursor.fetchone()["total"]
    cursor.close()
    conn.close()
    return {
        "students": total_students,
        "courses": total_courses,
        "marks": total_marks,
    }