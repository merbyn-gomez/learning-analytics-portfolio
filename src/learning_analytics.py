"""Reproducible learning analytics demo using only the Python standard library.

All records are synthetic. Nothing here originates from a real LMS.
"""
from __future__ import annotations

import argparse
import csv
import html
import random
import sqlite3
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATABASE = ROOT / "data" / "learning_analytics.sqlite"
REPORTS = ROOT / "reports"
AS_OF = date(2026, 10, 31)
SEED = 2026

COURSES = [
    (1, "Data Literacy Fundamentals", "Data", 12),
    (2, "Python for Analytics", "Data", 24),
    (3, "SQL Essentials", "Data", 18),
    (4, "Digital Teaching Strategies", "Education", 14),
    (5, "Instructional Design Basics", "Education", 20),
    (6, "Learning Management Systems", "Education", 16),
]
REGIONS = ["Metropolitana", "Valparaiso", "Biobio", "Maule", "Antofagasta"]


def build_database(path: Path = DATABASE, seed: int = SEED) -> dict[str, int]:
    """Build a deterministic SQLite database of synthetic learning records."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    rng = random.Random(seed)
    counters = {"students": 0, "enrollments": 0, "activities": 0, "assessments": 0}

    with sqlite3.connect(path) as con:
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript((ROOT / "sql" / "schema.sql").read_text(encoding="utf-8"))
        con.executemany(
            "INSERT INTO courses VALUES (?, ?, ?, ?)", COURSES
        )
        students = [
            (i, rng.choice(REGIONS), rng.choice(["18-24", "25-34", "35-44", "45+"]))
            for i in range(1, 321)
        ]
        con.executemany("INSERT INTO students VALUES (?, ?, ?)", students)
        counters["students"] = len(students)

        enrollment_id = activity_id = assessment_id = 0
        for student_id, _, _ in students:
            course_ids = rng.sample(range(1, 7), k=rng.choice([1, 2, 2, 3]))
            for course_id in course_ids:
                enrollment_id += 1
                start = date(2026, 8, 1) + timedelta(days=rng.randint(0, 59))
                status = rng.choices(
                    ["completed", "in_progress", "withdrawn"], weights=[57, 31, 12]
                )[0]
                finish = min(start + timedelta(days=rng.randint(7, 30)), AS_OF)
                completed_on = finish.isoformat() if status == "completed" else None
                con.execute(
                    "INSERT INTO enrollments VALUES (?, ?, ?, ?, ?, ?)",
                    (enrollment_id, student_id, course_id, start.isoformat(),
                     completed_on, status),
                )
                last_day = finish if status == "completed" else AS_OF
                events = rng.randint(0, 3) if status == "withdrawn" else rng.randint(2, 10)
                for _ in range(events):
                    activity_id += 1
                    event_day = start + timedelta(
                        days=rng.randint(0, (last_day - start).days)
                    )
                    con.execute(
                        "INSERT INTO activities VALUES (?, ?, ?, ?)",
                        (activity_id, enrollment_id, event_day.isoformat(),
                         rng.randint(10, 100)),
                    )
                if status == "completed" or (
                    status == "in_progress" and rng.random() < 0.3
                ):
                    assessment_id += 1
                    score = rng.randint(55, 100) if status == "completed" else rng.randint(20, 89)
                    con.execute(
                        "INSERT INTO assessments VALUES (?, ?, ?)",
                        (assessment_id, enrollment_id, score),
                    )
        counters.update(
            enrollments=enrollment_id,
            activities=activity_id,
            assessments=assessment_id,
        )
        con.commit()
    return counters


def query_results(path: Path = DATABASE) -> dict[str, list[dict]]:
    """Execute version-controlled SQL queries against the generated database."""
    if not Path(path).exists():
        raise FileNotFoundError("Database missing. Run: python src/learning_analytics.py all")
    result = {}
    with sqlite3.connect(path) as con:
        con.row_factory = sqlite3.Row
        for query_file in sorted((ROOT / "sql" / "queries").glob("*.sql")):
            rows = con.execute(query_file.read_text(encoding="utf-8")).fetchall()
            result[query_file.stem] = [dict(row) for row in rows]
    return result


def write_dashboard(results: dict, output: Path) -> None:
    """Create a portable static HTML preview without third-party dependencies."""
    overview = results["01_overview"][0]
    course_rows = results["02_course_performance"]
    cards = [
        ("Enrollments", str(overview["total_enrollments"])),
        ("Unique learners", str(overview["unique_learners"])),
        ("Completed", str(overview["completed_enrollments"])),
        ("Completion rate", f'{overview["completion_pct"]}%'),
    ]
    card_html = "".join(
        f'<div class="card"><span>{html.escape(label)}</span><strong>{html.escape(value)}</strong></div>'
        for label, value in cards
    )
    chart_html = "".join(
        '<div class="course"><div class="course-header"><span>'
        + html.escape(str(row["course_name"]))
        + '</span><b>'
        + f'{row["completion_pct"]}%'
        + '</b></div><div class="track"><div class="bar" style="width:'
        + f'{max(0, min(100, float(row["completion_pct"] or 0)))}%'
        + '"></div></div></div>'
        for row in course_rows
    )
    output.write_text(
        '<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Learning Analytics | Demo Dashboard</title>'
        '<style>body{font-family:system-ui,Arial;background:#0b1724;color:#eef6ff;'
        'max-width:980px;margin:45px auto;padding:0 20px}h1{font-size:2.2rem;margin-bottom:6px}'
        '.muted{color:#a8bdcc}.cards{display:grid;grid-template-columns:'
        'repeat(auto-fit,minmax(160px,1fr));gap:14px;margin:30px 0}'
        '.card,.panel{background:#15283a;border:1px solid #29465c;'
        'border-radius:14px;padding:19px}.card span{display:block;color:#a8bdcc}'
        '.card strong{display:block;font-size:2rem;margin-top:8px}'
        '.course{margin:22px 0}.course-header{display:flex;justify-content:'
        'space-between;gap:12px;margin-bottom:8px}.track{background:#2a4050;'
        'border-radius:10px;height:14px;overflow:hidden}.bar{background:#31c4a4;'
        'height:100%;border-radius:10px}.note{font-size:.88rem;line-height:1.5;'
        'color:#a8bdcc;margin-top:25px}</style></head><body>'
        '<h1>Learning Analytics</h1><div class="muted">Synthetic LMS dataset · '
        'Snapshot: 31 October 2026</div><section class="cards">'
        + card_html
        + '</section><section class="panel"><h2>Course completion rates</h2>'
        + chart_html
        + '</section><p class="note">Demo portfolio project. All data is synthetic. '
        'Completion rate = completed enrollments / all enrollments, including '
        'withdrawals. This page is generated from SQLite and version-controlled SQL.'
        '</p></body></html>',
        encoding="utf-8",
    )


def export_reports(path: Path = DATABASE, directory: Path = REPORTS) -> dict:
    """Export query results to CSV and generate an HTML preview."""
    results = query_results(path)
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name, rows in results.items():
        with (directory / f"{name}.csv").open("w", newline="", encoding="utf-8") as file:
            if not rows:
                continue
            writer = csv.DictWriter(file, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
    write_dashboard(results, directory / "dashboard.html")
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic LMS learning analytics")
    parser.add_argument("command", nargs="?", default="all",
                        choices=["all", "build", "report"])
    args = parser.parse_args()
    if args.command in ("all", "build"):
        counts = build_database()
        print("Created synthetic database:", DATABASE)
        print("Records:", counts)
    if args.command in ("all", "report"):
        results = export_reports()
        print("Generated reports:", REPORTS)
        print("Overview:", results["01_overview"][0])


if __name__ == "__main__":
    main()
