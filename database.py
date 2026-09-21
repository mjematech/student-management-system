import bcrypt
import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG

DEFAULT_STUDENT_PASSWORD = "1234"


def get_connection(with_database=True):
    config = DB_CONFIG.copy()
    if not with_database:
        config.pop("database", None)
    return mysql.connector.connect(**config)


def init_database():
    conn = get_connection(with_database=False)
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    cursor.close()
    conn.close()

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            full_name VARCHAR(150),
            role ENUM('admin', 'teacher') NOT NULL DEFAULT 'teacher',
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            registration_no VARCHAR(50) UNIQUE NOT NULL,
            full_name VARCHAR(150) NOT NULL,
            gender ENUM('Male', 'Female') NOT NULL,
            date_of_birth DATE,
            programme VARCHAR(150),
            phone VARCHAR(20),
            email VARCHAR(100),
            address VARCHAR(255),
            password VARCHAR(255),
            date_registered TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            course_code VARCHAR(20) UNIQUE NOT NULL,
            course_name VARCHAR(150) NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            semester VARCHAR(20) NOT NULL,
            assessment_type VARCHAR(30) NOT NULL,
            year INT NOT NULL,
            score DECIMAL(5,2) NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT NOT NULL,
            course_id INT NOT NULL,
            attendance_date DATE NOT NULL,
            status ENUM('Present', 'Absent') NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE CASCADE,
            UNIQUE KEY unique_attendance (student_id, course_id, attendance_date)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) NOT NULL,
            role VARCHAR(20) NOT NULL,
            action VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    cursor.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_schema = %s AND table_name = 'students' AND column_name = 'password'
    """, (DB_CONFIG["database"],))
    if not cursor.fetchone():
        cursor.execute("ALTER TABLE students ADD COLUMN password VARCHAR(255)")
        conn.commit()

    cursor.execute("SELECT id FROM students WHERE password IS NULL")
    students_missing_password = cursor.fetchall()
    if students_missing_password:
        default_hashed = bcrypt.hashpw(
            DEFAULT_STUDENT_PASSWORD.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")
        for (student_id,) in students_missing_password:
            cursor.execute(
                "UPDATE students SET password = %s WHERE id = %s",
                (default_hashed, student_id)
            )
        conn.commit()

    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        default_password = "admin123"
        hashed = bcrypt.hashpw(default_password.encode("utf-8"), bcrypt.gensalt())
        cursor.execute("""
            INSERT INTO users (username, password, full_name, role)
            VALUES (%s, %s, %s, %s)
        """, ("admin", hashed.decode("utf-8"), "System Administrator", "admin"))
        conn.commit()

    cursor.close()
    conn.close()


def test_connection():
    try:
        conn = get_connection()
        conn.close()
        return True, "Database connection successful."
    except Error as e:
        return False, str(e)