import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "instrumenty_mcp_skills.html"
AGENTS_PAGE = ROOT / "web" / "agentnye_sistemy.html"
INDEX = ROOT / "index.html"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.id_counts = {}
        self.details = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            value = values["id"]
            self.ids.add(value)
            self.id_counts[value] = self.id_counts.get(value, 0) + 1
        if tag == "details":
            self.details += 1


class EducationToolsPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
        cls.parser = PageParser()
        cls.parser.feed(cls.html)

    def test_page_exists_with_required_sections(self):
        self.assertTrue(PAGE.is_file())
        required = {
            "hero",
            "mcp",
            "skill",
            "tools",
            "mcp-catalog",
            "skills",
            "kits",
            "safety",
        }
        self.assertTrue(required.issubset(self.parser.ids))
        duplicates = [
            element_id
            for element_id, count in self.parser.id_counts.items()
            if count > 1
        ]
        self.assertEqual([], duplicates)

    def test_beginner_and_advanced_material_are_present(self):
        for marker in (
            "tools",
            "resources",
            "prompts",
            "SKILL.md",
            "FastMCP",
            "lesson-designer",
        ):
            self.assertIn(marker, self.html)
        self.assertGreaterEqual(self.parser.details, 4)

    def test_catalogs_and_safety_guidance_are_present(self):
        for marker in (
            "NotebookLM",
            "Google Colab",
            "GitHub MCP",
            "code-review-teacher",
        ):
            self.assertIn(marker, self.html)
        for marker in ("только чтение", "персональн", "подтвержден"):
            self.assertIn(marker, self.html.lower())

    def test_existing_pages_link_to_the_continuation(self):
        agents_html = AGENTS_PAGE.read_text(encoding="utf-8")
        index_html = INDEX.read_text(encoding="utf-8")
        self.assertIn('href="instrumenty_mcp_skills.html"', agents_html)
        self.assertIn('href="web/instrumenty_mcp_skills.html"', index_html)


if __name__ == "__main__":
    unittest.main()
