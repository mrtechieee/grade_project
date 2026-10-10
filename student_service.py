"""Business logic. Totals, averages and grades are derived, never stored."""
import database

GRADE_SCALE = ((90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D"), (0, "F"))
GRADE_ORDER = [grade for _, grade in GRADE_SCALE]


def calculate_total(marks):
    return sum(marks)


def calculate_average(total, count):
    return round(total / count, 2) if count else 0.0


def calculate_grade(average):
    return next(grade for minimum, grade in GRADE_SCALE if average >= minimum)


def _build_record(row):
    marks = list(row["subjects"].values())
    total = calculate_total(marks)
    average = calculate_average(total, len(marks))
    grade = calculate_grade(average)
    status = "FAIL" if grade == "F" else "PASS"
    return {**row, "total": total, "average": average, "grade": grade, "status": status}


def student_exists(name):
    return database.get_student(name) is not None


def create_student(name, subjects):
    database.add_student(name, subjects)
    return _build_record(database.get_student(name))


def list_students():
    return [_build_record(row) for row in database.get_students()]


def find_students(term):
    return [_build_record(row) for row in database.search_student(term)]


def get_statistics():
    """Return class-level statistics, or None when there are no students."""
    records = list_students()
    if not records:
        return None
    averages = [r["average"] for r in records]
    best = max(records, key=lambda r: r["average"])
    worst = min(records, key=lambda r: r["average"])
    passed = sum(r["status"] == "PASS" for r in records)
    return {
        "total_students": len(records),
        "class_average": round(sum(averages) / len(averages), 2),
        "highest": (best["name"], best["average"]),
        "lowest": (worst["name"], worst["average"]),
        "grade_counts": {g: sum(r["grade"] == g for r in records) for g in GRADE_ORDER},
        "pass_count": passed,
        "fail_count": len(records) - passed,
    }
