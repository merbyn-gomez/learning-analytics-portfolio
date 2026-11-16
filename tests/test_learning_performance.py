"""Regression checks for Learning Performance PBIR and synthetic KPI fixture.

Validates files and arithmetic, not rendering inside Power BI Desktop.
"""
import csv
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PBI = ROOT / "powerbi"
PAGE_ROOT = PBI / "LearningAnalytics.Report" / "definition" / "pages"
MEASURES = PBI / "LearningAnalytics.SemanticModel" / "definition" / "tables" / "_Measures.tmdl"


def load_csv(filename):
    with (PBI / "sample-data" / filename).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


class LearningPerformanceTests(unittest.TestCase):
    def test_report_has_two_pages_and_assessment_visuals(self):
        pages = json.loads((PAGE_ROOT / "pages.json").read_text(encoding="utf-8"))
        self.assertEqual(pages["pageOrder"], ["learning_overview", "learning_performance"])
        page = json.loads((PAGE_ROOT / "learning_performance" / "page.json").read_text(encoding="utf-8"))
        self.assertEqual(page["name"], "learning_performance")
        visuals = PAGE_ROOT / "learning_performance" / "visuals"
        expected = {
            "kpi_final_assessments", "kpi_passed", "kpi_final_pass",
            "kpi_final_avg", "pass_by_course", "score_by_region",
            "course_assessment_table", "performance_category_filter",
            "performance_region_filter", "performance_age_filter"
        }
        self.assertTrue(expected.issubset({f.parent.name for f in visuals.glob("*/visual.json")}))
        m = MEASURES.read_text(encoding="utf-8")
        for name in (
            "Final Assessments", "Passed Final Assessments",
            "Failed Final Assessments", "Average Final Score", "Final Pass Rate"
        ):
            self.assertIn(f"measure '{name}' =", m)
        for file in visuals.glob("*/visual.json"):
            self.assertEqual(json.loads(file.read_text(encoding="utf-8"))["name"],
                             file.parent.name)

    def test_synthetic_final_assessment_totals(self):
        enrollments = {x["enrollment_id"]: x for x in load_csv("enrollments.csv")}
        students = {x["student_id"]: x for x in load_csv("students.csv")}
        courses = load_csv("courses.csv")
        assessments = load_csv("assessments.csv")
        finals = [a for a in assessments
                  if enrollments[a["enrollment_id"]]["status"] == "completed"]
        passed = [a for a in finals if int(a["score"]) >= 70]
        failed = [a for a in finals if int(a["score"]) < 70]
        self.assertEqual(len(finals), 213)
        self.assertEqual(len(passed), 141)
        self.assertEqual(len(failed), 72)
        self.assertEqual(round(100 * len(passed) / len(finals), 1), 66.2)
        self.assertEqual(round(sum(int(a["score"]) for a in finals) / len(finals), 1), 77.0)
        by_course = {c["course_id"]: 0 for c in courses}
        by_region = {}
        for a in finals:
            e = enrollments[a["enrollment_id"]]
            by_course[e["course_id"]] += 1
            region = students[e["student_id"]]["region"]
            by_region[region] = by_region.get(region, 0) + 1
        self.assertEqual(sum(by_course.values()), 213)
        self.assertEqual(sum(by_region.values()), 213)
        self.assertEqual(len(by_region), 5)


if __name__ == "__main__":
    unittest.main()
