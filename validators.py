"""Input validation. Pure functions: no printing, no database access."""
import math

MAX_SUBJECTS = 10


class ValidationError(ValueError):
    """Raised for invalid user input; carries a friendly title and message."""

    def __init__(self, title, message=""):
        super().__init__(title)
        self.title = title
        self.message = message


def _clean_text(raw):
    return " ".join(raw.split())


def validate_student_name(raw):
    name = _clean_text(raw)
    if not name:
        raise ValidationError("Student name cannot be empty.", "Please enter a name.")
    return name


def validate_subject_name(raw):
    name = _clean_text(raw)
    if not name:
        raise ValidationError("Subject name cannot be empty.", "Please enter a subject name.")
    return name


def validate_subject_count(raw):
    try:
        count = int(raw.strip())
    except ValueError:
        raise ValidationError("Invalid Input", "Please enter a whole number.") from None
    if not 1 <= count <= MAX_SUBJECTS:
        raise ValidationError(
            "Invalid Number of Subjects", f"Enter a number between 1 and {MAX_SUBJECTS}."
        )
    return count


def validate_marks(raw):
    try:
        marks = float(raw.strip())
    except ValueError:
        raise ValidationError("Invalid Input", "Please enter a valid number.") from None
    if not math.isfinite(marks) or not 0 <= marks <= 100:
        raise ValidationError(
            "Invalid Marks", "Marks must be between 0 and 100.\nPlease try again."
        )
    return marks
