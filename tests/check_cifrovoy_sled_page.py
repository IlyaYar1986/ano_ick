import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "cifrovoy_sled.html"
VIZ_PAGES = [
    ROOT / "web" / "sled_simulyator.html",
    ROOT / "web" / "dva_studenta.html",
    ROOT / "web" / "qr_voronka.html",
    ROOT / "web" / "galereya_patternov.html",
    ROOT / "web" / "etika_sortirovka.html",
]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.id_counts = {}
        self.iframe_srcs = []
        self.img_srcs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            value = values["id"]
            self.ids.add(value)
            self.id_counts[value] = self.id_counts.get(value, 0) + 1
        if tag == "iframe" and "src" in values:
            self.iframe_srcs.append(values["src"])
        if tag == "img" and "src" in values:
            self.img_srcs.append(values["src"])


class CifrovoySledPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
        cls.parser = PageParser()
        cls.parser.feed(cls.html)

    def test_page_exists_with_required_sections(self):
        self.assertTrue(PAGE.is_file())
        required = {
            "hero",
            "s1",
            "s2",
            "s3",
            "s4",
            "s5",
            "s6",
            "s7",
            "s8",
            "checklist",
            "quiz",
            "final",
        }
        self.assertTrue(required.issubset(self.parser.ids))
        duplicates = [
            element_id
            for element_id, count in self.parser.id_counts.items()
            if count > 1
        ]
        self.assertEqual([], duplicates)

    def test_lecture_markers_are_present(self):
        for marker in (
            "Цифровой",
            "Пассивный",
            "паттерн",
            "152-ФЗ",
            "обезличить",
            "прокрастинатор",
            "Wayground",
        ):
            self.assertIn(marker, self.html)
        gallery = (ROOT / "web" / "galereya_patternov.html").read_text(
            encoding="utf-8"
        )
        for marker in ("Прокрастинатор", "Тихоня-отличник", "Понедельничный"):
            self.assertIn(marker, gallery)

    def test_cookie_history_callout_is_present(self):
        for marker in ("cookie", "Лу Монтулли", "Гензел", "хлебных крошек", "Легенда"):
            self.assertIn(marker, self.html)

    def test_services_have_active_links_and_no_unavailable_ones(self):
        for url in (
            "https://giga.chat/",
            "https://chat.deepseek.com/",
            "https://forms.yandex.ru/",
            "https://stepik.org/",
        ):
            self.assertIn(url, self.html)
        self.assertNotIn("ChatGPT", self.html)

    def test_visualizations_are_embedded_and_exist(self):
        expected = {
            "sled_simulyator.html",
            "dva_studenta.html",
            "qr_voronka.html",
            "galereya_patternov.html",
            "etika_sortirovka.html",
        }
        embedded = {
            src for src in self.parser.iframe_srcs if not src.startswith("#")
        }
        self.assertTrue(expected.issubset(embedded))
        for viz_page in VIZ_PAGES:
            self.assertTrue(viz_page.is_file(), viz_page.name)

    def test_infographics_point_to_cifrovoy_sled_folder(self):
        png_srcs = [
            src for src in self.parser.img_srcs if src.endswith(".webp")
        ]
        self.assertGreaterEqual(len(png_srcs), 8)
        for src in png_srcs:
            self.assertTrue(
                src.startswith("../png/cifrovoy_sled/"),
                src,
            )

    def test_viz_pages_are_self_contained(self):
        for viz_page in VIZ_PAGES:
            html = viz_page.read_text(encoding="utf-8")
            self.assertIn('lang="ru"', html, viz_page.name)
            for forbidden in ("http://", "https://", "cdn.", "unpkg", "jsdelivr"):
                self.assertNotIn(forbidden, html, viz_page.name)


if __name__ == "__main__":
    unittest.main()
