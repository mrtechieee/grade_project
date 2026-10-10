"""Rich presentation layer: White + Royal Blue dashboard theme."""
import time

from rich import box
from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.progress import BarColumn, Progress, TaskProgressColumn, TextColumn
from rich.table import Table
from rich.text import Text

import validators

ROYAL, DEEP, LIGHT = "#2563EB", "#1E3A8A", "#EFF6FF"
SUCCESS, WARNING, ERROR, SLATE = "#16A34A", "#F59E0B", "#DC2626", "#64748B"
GRADE_STYLE = {"A+": SUCCESS, "A": SUCCESS, "B": ROYAL, "C": WARNING, "D": WARNING, "F": ERROR}

console = Console()


def fmt(number):
    return str(int(number)) if float(number).is_integer() else f"{number:.2f}"


def _header(subtitle):
    body = Text.assemble(
        ("\nSTUDENT GRADE MANAGEMENT SYSTEM\n", f"bold {DEEP}"),
        (f"\n{subtitle}\n", SLATE),
        justify="center",
    )
    return Align.center(Panel(body, box=box.DOUBLE, border_style=ROYAL, padding=(0, 6)))


def show_welcome():
    console.clear()
    console.print()
    console.print(_header("Academic Performance Suite"))
    console.print()


def show_loading(label, done=None, duration=0.8, work=None):
    """Animated progress bar; runs `work` (real work) and returns its result."""
    result = None
    columns = (
        TextColumn(f"[{DEEP}]{{task.description}}"),
        BarColumn(bar_width=30, complete_style=ROYAL, finished_style=ROYAL),
        TaskProgressColumn(style=ROYAL),
    )
    with Progress(*columns, console=console) as progress:
        task = progress.add_task(label, total=100)
        for _ in range(10):
            time.sleep(duration / 10)
            progress.advance(task, 5)
        if work:
            result = work()
        progress.update(task, completed=100)
    if done:
        show_success(done)
    return result


def show_success(message):
    console.print(f"[bold {SUCCESS}]✓ {message}[/]\n")


def show_warning(title, message=""):
    body = f"[bold {WARNING}]⚠ {title}[/]" + (f"\n\n[{SLATE}]{message}[/]" if message else "")
    console.print(Panel(body, border_style=WARNING, expand=False, padding=(0, 2)))


def show_error(title, message=""):
    body = f"[bold {ERROR}]✗ {title}[/]" + (f"\n\n[{SLATE}]{message}[/]" if message else "")
    console.print(Panel(body, border_style=ERROR, expand=False, padding=(0, 2)))


def show_db_error():
    show_error("Unable to access student database.",
               "Please check the application folder and try again.")


def display_menu():
    console.print()
    console.print(_header("Academic Performance Dashboard"))
    items = ["1. Add Student", "2. View All Students", "3. Search Student",
             "4. Statistics", "5. Exit"]
    console.print(Align.center(Text("MAIN MENU", style=f"bold {ROYAL}")))
    console.print()
    for item in items:
        number, label = item.split(". ")
        console.print(Align.center(Text.assemble((f"{number}. ", f"bold {ROYAL}"), (label, "bold"))))
    console.print()


def ask(label, validator):
    """Prompt repeatedly until `validator` accepts the input."""
    while True:
        raw = console.input(f"[bold {ROYAL}]{label}[/] ")
        try:
            return validator(raw)
        except validators.ValidationError as exc:
            show_warning(exc.title, exc.message)


def get_choice():
    return console.input(f"[bold {ROYAL}]Select an option →[/] ").strip()


def display_students(records):
    table = Table(box=box.HEAVY_HEAD, header_style=f"bold white on {ROYAL}", border_style=ROYAL)
    table.add_column("Student", style="bold")
    for name in ("Total", "Average", "Grade", "Status"):
        table.add_column(name)
    for r in records:
        table.add_row(
            r["name"], fmt(r["total"]), f"{r['average']:.2f}",
            Text(r["grade"], style=f"bold {GRADE_STYLE[r['grade']]}"),
            Text(r["status"], style=f"bold {SUCCESS if r['status'] == 'PASS' else ERROR}"),
        )
    console.print(Align.center(table))
    console.print()


def _performance_bar(average, width=30):
    filled = round(width * average / 100)
    return Text.assemble(("█" * filled, ROYAL), ("░" * (width - filled), SLATE),
                         (f" {average:.2f}%", f"bold {DEEP}"))


def display_student_profile(record):
    grid = Table.grid(padding=(0, 4))
    grid.add_column()
    grid.add_column(justify="right")
    grid.add_row(Text("Name", style=SLATE), Text(record["name"], style=f"bold {DEEP}"))
    grid.add_row("", "")
    for subject, marks in record["subjects"].items():
        grid.add_row(subject, fmt(marks))
    grid.add_row("", "")
    grid.add_row("Total", Text(fmt(record["total"]), style="bold"))
    grid.add_row("Average", Text(f"{record['average']:.2f}", style="bold"))
    grid.add_row("Grade", Text(record["grade"], style=f"bold {GRADE_STYLE[record['grade']]}"))
    status_color = SUCCESS if record["status"] == "PASS" else ERROR
    grid.add_row("Status", Text(record["status"], style=f"bold {status_color}"))
    body = Group(grid, Text(), Text("Performance", style=SLATE), _performance_bar(record["average"]))
    console.print(Align.center(Panel(body, title=f"[bold {ROYAL}]STUDENT PROFILE[/]",
                                     border_style=ROYAL, padding=(1, 3), expand=False)))
    console.print()


def display_statistics(stats):
    grid = Table.grid(padding=(0, 6))
    grid.add_column()
    grid.add_column(justify="right")
    rows = [("Total Students", str(stats["total_students"])),
            ("Class Average", f"{stats['class_average']:.2f}"),
            ("Highest Average", f"{stats['highest'][1]:.2f}  ({stats['highest'][0]})"),
            ("Lowest Average", f"{stats['lowest'][1]:.2f}  ({stats['lowest'][0]})")]
    for label, value in rows:
        grid.add_row(label, Text(value, style=f"bold {DEEP}"))
    grid.add_row("", "")
    for grade, count in stats["grade_counts"].items():
        grid.add_row(f"{grade} Students", Text(str(count), style=f"bold {GRADE_STYLE[grade]}"))
    grid.add_row("", "")
    grid.add_row("Pass", Text(str(stats["pass_count"]), style=f"bold {SUCCESS}"))
    grid.add_row("Fail", Text(str(stats["fail_count"]), style=f"bold {ERROR}"))
    console.print(Align.center(Panel(grid, title=f"[bold {ROYAL}]CLASS STATISTICS[/]",
                                     border_style=ROYAL, padding=(1, 3), expand=False)))
    console.print()
