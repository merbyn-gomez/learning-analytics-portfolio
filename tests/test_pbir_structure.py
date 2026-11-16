"""Guard against regressions that make Power BI display an empty report."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "powerbi" / "LearningAnalytics.Report"
DEFINITION = REPORT / "definition"


class TestPowerBIReportStructure(unittest.TestCase):
    def test_required_theme_and_resource(self):
        report = json.loads((DEFINITION / "report.json").read_text(encoding="utf-8"))
        theme_name = report["themeCollection"]["baseTheme"]["name"]
        package_items = [
            item for package in report["resourcePackages"]
            for item in package.get("items", [])
        ]
        self.assertTrue(
            any(item["name"] == theme_name for item in package_items),
            "The report theme must be registered as a resource.",
        )
        self.assertTrue(
            (REPORT / "StaticResources" / "SharedResources" / "BaseThemes"
             / (theme_name + ".json")).is_file(),
            "The registered base theme file must exist.",
        )

    def test_page_and_visual_references(self):
        pages = json.loads((DEFINITION / "pages" / "pages.json").read_text(
            encoding="utf-8"))
        self.assertTrue(pages["pageOrder"], "At least one report page is required.")
        for page_name in pages["pageOrder"]:
            page_dir = DEFINITION / "pages" / page_name
            page = json.loads((page_dir / "page.json").read_text(encoding="utf-8"))
            self.assertEqual(page["name"], page_name)
            visual_paths = list((page_dir / "visuals").glob("*/visual.json"))
            self.assertTrue(visual_paths, "The page must contain visuals.")
            for path in visual_paths:
                visual = json.loads(path.read_text(encoding="utf-8"))
                self.assertEqual(path.parent.name, visual["name"])
                self.assertIn("visualType", visual["visual"])


if __name__ == "__main__":
    unittest.main()
