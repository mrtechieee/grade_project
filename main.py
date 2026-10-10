"""Student Grade Management System: entry point and menu flow."""
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import database
import student_service as service
import ui
import validators


def startup():
    ui.show_welcome()
    ui.show_loading("Initializing system...", work=database.initialize_database)
    ui.show_loading("Loading student records...", work=service.list_students)
    ui.show_success("System ready")


def get_valid_student_name():
    while True:
        name = ui.ask("Student Name:", validators.validate_student_name)
        if service.student_exists(name):
            ui.show_warning("Student already exists.", "Please use a different name.")
            continue
        return name


def get_valid_subject_name(taken):
    while True:
        subject = ui.ask("Subject Name:", validators.validate_subject_name)
        if subject.lower() in taken:
            ui.show_warning("Duplicate subject.", f"'{subject}' was already entered for this student.")
            continue
        return subject


def add_student():
    ui.show_loading("Preparing Student Profile...", "Ready", duration=0.5)
    name = get_valid_student_name()
    count = ui.ask("Number of Subjects:", validators.validate_subject_count)
    subjects = {}
    for number in range(1, count + 1):
        ui.console.print(f"\n[bold {ui.DEEP}]Subject {number}[/]")
        subject = get_valid_subject_name({s.lower() for s in subjects})
        subjects[subject] = ui.ask("Marks:", validators.validate_marks)
    try:
        record = ui.show_loading(
            "Saving student record...", "Student added successfully!",
            work=lambda: service.create_student(name, subjects),
        )
    except database.DuplicateStudentError:
        ui.show_warning("Student already exists.", "Please use a different name.")
        return
    ui.display_student_profile(record)


def display_students():
    records = ui.show_loading("Loading records...", duration=0.6, work=service.list_students)
    if not records:
        ui.console.print(f"[{ui.SLATE}]No student records available.[/]\n")
        return
    ui.show_success("Records loaded")
    ui.display_students(records)


def search_student():
    term = ui.ask("Search student:", validators.validate_student_name)
    matches = ui.show_loading("Searching records...", duration=0.5,
                              work=lambda: service.find_students(term))
    if not matches:
        ui.show_error("Student not found.")
        return
    for record in matches:
        ui.display_student_profile(record)


def show_statistics():
    stats = ui.show_loading("Generating statistics...", "Statistics ready",
                            duration=0.7, work=service.get_statistics)
    if stats is None:
        ui.console.print(f"[{ui.SLATE}]No student records available.[/]\n")
        return
    ui.display_statistics(stats)


def exit_application():
    ui.show_loading("Closing application...", duration=0.7)
    ui.console.print(f"[bold {ui.DEEP}]Thank you for using\nStudent Grade Management System.[/]\n")
    ui.console.print(f"[bold {ui.ROYAL}]Goodbye![/]\n")
    sys.exit(0)


ACTIONS = {"1": add_student, "2": display_students, "3": search_student,
           "4": show_statistics, "5": exit_application}


def main():
    try:
        startup()
        while True:
            ui.display_menu()
            action = ACTIONS.get(ui.get_choice())
            if action is None:
                ui.show_warning("Invalid option.", "Please choose a number from 1 to 5.")
                continue
            try:
                action()
            except database.DatabaseError:
                ui.show_db_error()
    except database.DatabaseError:
        ui.show_db_error()
        sys.exit(1)
    except (KeyboardInterrupt, EOFError):
        ui.console.print(f"\n[{ui.SLATE}]Application closed.[/]")
        sys.exit(0)


if __name__ == "__main__":
    main()
