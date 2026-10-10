# Student Grade Management System

A Python CLI application for managing student academic records, built with **Rich** and backed by **SQLite** so data survives restarts.

## Live Demo (web version)
A browser version with a landing page and the full app lives in `docs/index.html` and is published with GitHub Pages: https://mrtechieee.github.io/student_grade_system/

> The web version saves records in the visitor's own browser. The Python CLI uses SQLite (`data/student_data.db`).

## Features
- Add students with multiple subjects and validated marks (0–100)
- Automatic total, average, grade and PASS/FAIL status
- View all students, case-insensitive search, class statistics dashboard
- Persistent local storage (`data/student_data.db`), fully offline
- Rich White + Royal Blue interface with short progress animations
- Graceful handling of invalid input and database errors

## Quickstart & Run

### Option 1: Unified Web Dashboard (Single Link)
```bash
pip install -r requirements.txt
python server.py
```
Open **[http://localhost:8000/](http://localhost:8000/)** in your browser.

### Option 2: Terminal CLI Application
```bash
python main.py
```
The `data/` folder and database are created automatically on first run. `sqlite3` ships with Python, so it is not in `requirements.txt`.

## Architecture
```
UI (ui.py, main.py)  →  Service (student_service.py)  →  Database (database.py)
                         validators.py (pure input checks)
```
SQLite is the single source of truth. Total, average and grade are **calculated from stored marks**, never stored.

## Database
`students(id, name UNIQUE NOCASE, created_at)` and `subjects(id, student_id → students ON DELETE CASCADE, subject_name, marks)`. Foreign keys are enabled per connection, every query is parameterized, and each connection commits on success, rolls back on failure and is always closed. Errors are logged to `data/error.log`.

## Grade Scale (from average)
| Average | Grade | Average | Grade |
|---|---|---|---|
| 90–100 | A+ | 60–69 | C |
| 80–89 | A | 50–59 | D |
| 70–79 | B | 0–49 | F (FAIL) |

## Project Structure
`main.py` menu flow · `ui.py` Rich presentation · `student_service.py` business logic · `database.py` SQLite layer · `validators.py` input validation · `docs/index.html` web version (landing page + app) · `data/` created at runtime (git-ignored).

## Persistence Test
1. Run `python main.py`, add *Rahul Kumar* (Python 85, Maths 90, DBMS 78), then Exit.
2. Run `python main.py` again → View, Search `rahul` and Statistics all include Rahul.
