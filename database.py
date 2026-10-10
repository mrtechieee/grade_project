"""SQLite persistence layer. All SQL lives here and is fully parameterized."""
import logging
import sqlite3
from contextlib import contextmanager
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "student_data.db"

logger = logging.getLogger("student_grade_management")


class DatabaseError(Exception):
    """The database could not be read or written."""


class DuplicateStudentError(Exception):
    """A student with this name already exists."""


@contextmanager
def get_connection():
    """Open a connection, commit on success, roll back on failure, always close."""
    connection = None
    try:
        connection = sqlite3.connect(DB_PATH)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        yield connection
        connection.commit()
    except sqlite3.Error as exc:
        if connection:
            connection.rollback()
        logger.exception("Database operation failed")
        raise DatabaseError(str(exc)) from exc
    finally:
        if connection:
            connection.close()


def initialize_database():
    """Create the data folder, database file and tables if they do not exist."""
    try:
        DATA_DIR.mkdir(exist_ok=True)
        logging.basicConfig(
            filename=DATA_DIR / "error.log", level=logging.ERROR,
            format="%(asctime)s %(levelname)s %(message)s",
        )
    except OSError as exc:
        raise DatabaseError(str(exc)) from exc
    with get_connection() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS subjects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id INTEGER NOT NULL,
                subject_name TEXT NOT NULL COLLATE NOCASE,
                marks REAL NOT NULL,
                UNIQUE (student_id, subject_name),
                FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
            );
            """
        )


def add_subject(student_id, subject_name, marks, conn):
    conn.execute(
        "INSERT INTO subjects (student_id, subject_name, marks) VALUES (?, ?, ?)",
        (student_id, subject_name, marks),
    )


def add_student(name, subjects):
    """Insert a student and all subjects in one transaction; returns the new id."""
    with get_connection() as conn:
        try:
            cursor = conn.execute("INSERT INTO students (name) VALUES (?)", (name,))
        except sqlite3.IntegrityError as exc:
            raise DuplicateStudentError(name) from exc
        for subject_name, marks in subjects.items():
            add_subject(cursor.lastrowid, subject_name, marks, conn)
        return cursor.lastrowid


def get_subjects(student_id):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT subject_name, marks FROM subjects WHERE student_id = ? ORDER BY id",
            (student_id,),
        ).fetchall()
    return {row["subject_name"]: row["marks"] for row in rows}


def _attach_subjects(conn, students):
    result = []
    for student in students:
        rows = conn.execute(
            "SELECT subject_name, marks FROM subjects WHERE student_id = ? ORDER BY id",
            (student["id"],),
        ).fetchall()
        result.append({
            "id": student["id"],
            "name": student["name"],
            "subjects": {r["subject_name"]: r["marks"] for r in rows},
        })
    return result


def get_students():
    with get_connection() as conn:
        students = conn.execute("SELECT id, name FROM students ORDER BY id").fetchall()
        return _attach_subjects(conn, students)


def get_student(name):
    """Exact (case-insensitive) lookup; returns None when not found."""
    with get_connection() as conn:
        students = conn.execute(
            "SELECT id, name FROM students WHERE name = ?", (name,)
        ).fetchall()
        found = _attach_subjects(conn, students)
    return found[0] if found else None


def search_student(term):
    """Case-insensitive partial match on the student name."""
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    with get_connection() as conn:
        students = conn.execute(
            "SELECT id, name FROM students WHERE name LIKE ? ESCAPE '\\' ORDER BY name",
            (f"%{escaped}%",),
        ).fetchall()
        return _attach_subjects(conn, students)


def update_student(student_id, name, subjects):
    """Rename a student and replace their subjects atomically."""
    with get_connection() as conn:
        try:
            conn.execute("UPDATE students SET name = ? WHERE id = ?", (name, student_id))
        except sqlite3.IntegrityError as exc:
            raise DuplicateStudentError(name) from exc
        conn.execute("DELETE FROM subjects WHERE student_id = ?", (student_id,))
        for subject_name, marks in subjects.items():
            add_subject(student_id, subject_name, marks, conn)


def delete_student(student_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM students WHERE id = ?", (student_id,))
