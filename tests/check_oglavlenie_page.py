import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "oglavlenie.html"

RETIRED = {
    "web/omonimy.html",
    "web/word_embeddings.html",
    "web/training_embeddings.html",
    "web/механизм Attension.html",
    "web/процесс SFT и LoRA.html",
    "web/процесс RLHF.html",
}


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "a" and "href" in values:
            self.hrefs.append(values["href"])


class OglavleniePageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
        cls.parser = LinkParser()
        cls.parser.feed(cls.html)
        cls.page_links = [
            unquote(href)
            for href in cls.parser.hrefs
            if href.endswith(".html")
        ]

    def test_page_exists(self):
        self.assertTrue(PAGE.is_file())

    def test_all_linked_pages_exist(self):
        self.assertGreater(len(self.page_links), 20)
        for href in self.page_links:
            self.assertTrue((ROOT / href).is_file(), href)

    def test_all_main_lessons_are_linked(self):
        expected = {
            "index.html",
            "web/seminar_25_45.html",
            "web/agentnye_sistemy.html",
            "web/instrumenty_mcp_skills.html",
            "web/personalizaciya_tyutorstvo.html",
            "web/cifrovoy_sled.html",
            "web/ochistka_dannyh.html",
            "web/bezopasnost_dannyh.html",
        }
        self.assertTrue(expected.issubset(set(self.page_links)))

    def test_new_lecture_demos_are_linked(self):
        expected = {
            "web/sled_simulyator.html",
            "web/dva_studenta.html",
            "web/qr_voronka.html",
            "web/galereya_patternov.html",
            "web/etika_sortirovka.html",
            "web/gryaznye_dannye.html",
            "web/trenazher_ochistki.html",
            "web/ii_vizualizator.html",
            "web/shtraf_kalkulyator.html",
            "web/sravnenie_servisov.html",
            "web/algoritm_incidenta.html",
        }
        self.assertTrue(expected.issubset(set(self.page_links)))

    def test_retired_pages_are_not_linked(self):
        for href in self.page_links:
            self.assertNotIn(href, RETIRED)

    def test_lesson_pages_link_back_to_toc(self):
        root_pages = {ROOT / "index.html"}
        web_pages = {
            ROOT / "web" / name
            for name in (
                "seminar_25_45.html",
                "agentnye_sistemy.html",
                "instrumenty_mcp_skills.html",
                "personalizaciya_tyutorstvo.html",
                "cifrovoy_sled.html",
                "ochistka_dannyh.html",
                "bezopasnost_dannyh.html",
                "ответы-участников.html",
            )
        }
        for page in root_pages:
            html = page.read_text(encoding="utf-8")
            self.assertIn('href="oglavlenie.html"', html, page.name)
            self.assertIn("Оглавление", html, page.name)
        for page in web_pages:
            html = page.read_text(encoding="utf-8")
            self.assertIn('href="../oglavlenie.html"', html, page.name)
            self.assertIn("Оглавление", html, page.name)


if __name__ == "__main__":
    unittest.main()
