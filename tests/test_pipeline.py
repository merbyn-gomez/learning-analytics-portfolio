"""Integration tests for the synthetic learning analytics pipeline."""
import csv
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from learning_analytics import build_database, export_reports, query_results


class LearningAnalyticsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.db = self.directory / "demo.sqlite"

    def test_reproducible_counts_and_constraints(self):
        counts1 = build_database(self.db)
        counts2 = build_database(self.db)
        self.assertEqual(counts1, counts2)
        self.assertEqual(counts1["students"], 320)
        self.assertGreater(counts1["enrollments"], 320)
        with sqlite3.connect(self.db) as con:
            self.assertEqual(con.execute("PRAGMA foreign_key_check").fetchall(), [])
            invalid = con.execute(
                "SELECT COUNT(*) FROM enrollments "
                "WHERE status = 'completed' AND completed_on IS NULL"
            ).fetchone()[0]
            self.assertEqual(invalid, 0)

    def test_kpis_have_consistent_denominators(self):
        build_database(self.db)
        results = query_results(self.db)
        overview = results["01_overview"][0]
        self.assertEqual(
            sum(row["enrollments"] for row in results["02_course_performance"]),
            overview["total_enrollments"],
        )
        self.assertEqual(
            sum(row["completed"] for row in results["02_course_performance"]),
            overview["completed_enrollments"],
        )
        self.assertTrue(0 <= overview["completion_pct"] <= 100)
        for row in results["04_assessments"]:
            self.assertTrue(0 <= row["pass_pct"] <= 100)

    def test_export_creates_openable_dashboard_and_csv(self):
        build_database(self.db)
        out = self.directory / "reports"
        results = export_reports(self.db, out)
        self.assertEqual(len(list(out.glob("*.csv"))), len(results))
        dashboard = (out / "dashboard.html").read_text(encoding="utf-8")
        self.assertIn("Learning Analytics", dashboard)
        self.assertIn("All data is synthetic", dashboard)
        with (out / "02_course_performance.csv").open(
            newline="", encoding="utf-8"
        ) as file:
            self.assertEqual(len(list(csv.DictReader(file))), 6)


if __name__ == "__main__":
    unittest.main()
