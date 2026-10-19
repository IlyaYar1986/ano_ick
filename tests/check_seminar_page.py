import re
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "seminar_25_45.html"
INDEX = ROOT / "index.html"


class ResourceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.id_counts = {}
        self.resources = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.add(values["id"])
            self.id_counts[values["id"]] = self.id_counts.get(values["id"], 0) + 1
        if tag in {"iframe", "img"} and values.get("src"):
            self.resources.append(values["src"])


class SeminarPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
        cls.parser = ResourceParser()
        cls.parser.feed(cls.html)

    def test_page_exists(self):
        self.assertTrue(PAGE.is_file(), "web/seminar_25_45.html must exist")

    def test_page_has_two_timed_parts_and_required_sections(self):
        self.assertIn("<title>От смысла к действию", self.html)
        self.assertIn("25 минут", self.html)
        self.assertIn("45 минут", self.html)
        expected_ids = {
            "hero",
            "part1",
            "gpt",
            "tokens",
            "embeddings",
            "image-bridge",
            "part2",
            "attention",
            "training",
            "sampling",
            "reasoning",
            "agents",
            "memory",
            "teacher-agent",
        }
        self.assertTrue(expected_ids.issubset(self.parser.ids))
        duplicates = [
            element_id
            for element_id, count in self.parser.id_counts.items()
            if count > 1
        ]
        self.assertEqual([], duplicates, f"Duplicate IDs: {duplicates}")
        for time_range in (
            "0–3 мин",
            "3–7 мин",
            "7–12 мин",
            "12–20 мин",
            "20–25 мин",
            "0–5 мин",
            "5–14 мин",
            "14–20 мин",
            "20–25 мин",
            "25–32 мин",
            "32–39 мин",
            "39–45 мин",
        ):
            self.assertIn(time_range, self.html)

    def test_local_iframes_and_images_resolve(self):
        local_resources = [
            source
            for source in self.parser.resources
            if not re.match(r"^(?:https?:)?//|^data:", source)
        ]
        self.assertGreaterEqual(len(local_resources), 10)
        missing = [
            source
            for source in local_resources
            if not (PAGE.parent / source).resolve().is_file()
        ]
        self.assertEqual([], missing, f"Missing resources: {missing}")

    def test_sampling_controls_and_pedagogical_bridge_are_present(self):
        for label in ("Temperature", "Top-K", "Top-P", "Min-P"):
            self.assertIn(label, self.html)
        self.assertIn("пространстве смыслов", self.html)
        self.assertIn("следующий полезный вопрос", self.html)
        self.assertIn("формирующее оценивание", self.html)

    def test_page_is_theory_only(self):
        forbidden = (
            'id="practice"',
            "<form",
            "выполните практическое задание",
            "поле для ответа",
        )
        for marker in forbidden:
            self.assertNotIn(marker, self.html.lower())

    def test_main_landing_links_to_two_part_seminar(self):
        index_html = INDEX.read_text(encoding="utf-8")
        self.assertIn('href="web/seminar_25_45.html"', index_html)


if __name__ == "__main__":
    unittest.main()
