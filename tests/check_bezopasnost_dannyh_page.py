import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "bezopasnost_dannyh.html"
PREV_PAGE = ROOT / "web" / "ochistka_dannyh.html"
VIZ_PAGES = [
    ROOT / "web" / "shtraf_kalkulyator.html",
    ROOT / "web" / "sravnenie_servisov.html",
    ROOT / "web" / "algoritm_incidenta.html",
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


class BezopasnostDannyhPageTest(unittest.TestCase):
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
            "s9",
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
            "152-ФЗ",
            "Минпросвещени",
            "GigaChat",
            "ChatGPT",
            "Claude",
            "250 раз",
            "Алгоритм действий при инциденте",
            "YandexGPT",
        ):
            self.assertIn(marker, self.html)

    def test_title_promise_is_covered_beyond_the_law(self):
        # Заголовок лекции — "Управление качеством данных и цифровая
        # безопасность", а не только 152-ФЗ. Проверяем, что оба раздела
        # реально присутствуют, а не только упомянуты в названии.
        for marker in (
            "Управление качеством данных",
            "Точность",
            "Согласованность",
            "Цифровая безопасность шире одного закона",
            "Двухфакторная",
            "Фишинг",
            "Резервные копии",
        ):
            self.assertIn(marker, self.html)

    def test_no_invented_practice_references(self):
        # В тексте лекции 4.4 нет блока "Мост к практике" — не должно быть
        # придуманных карточек-анонсов практических занятий, как в лекции 4.1.
        for marker in ("Мост к практике", "Практика 1", "Практика 2", "практическое занятие"):
            self.assertNotIn(marker, self.html)

    def test_services_have_active_links(self):
        for url in (
            "https://developers.sber.ru",
            "https://openai.com/policies/privacy-policy",
            "https://www.anthropic.com/legal/privacy",
            "https://ya.ru/ai",
        ):
            self.assertIn(url, self.html)

    def test_visualizations_are_embedded_and_exist(self):
        expected = {
            "shtraf_kalkulyator.html",
            "sravnenie_servisov.html",
            "algoritm_incidenta.html",
        }
        embedded = {
            src for src in self.parser.iframe_srcs if not src.startswith("#")
        }
        self.assertTrue(expected.issubset(embedded))
        for viz_page in VIZ_PAGES:
            self.assertTrue(viz_page.is_file(), viz_page.name)

    def test_infographics_point_to_bezopasnost_dannyh_folder(self):
        png_srcs = [
            src for src in self.parser.img_srcs if src.endswith(".webp")
        ]
        self.assertGreaterEqual(len(png_srcs), 8)
        for src in png_srcs:
            self.assertTrue(
                src.startswith("../png/bezopasnost_dannyh/"),
                src,
            )

    def test_viz_pages_are_self_contained(self):
        # Внешние ссылки на политики конфиденциальности в тексте — это часть
        # содержания урока (правило проекта: ссылка рядом с упоминанием
        # сервиса), а не загрузка внешних библиотек — запрещаем только их.
        for viz_page in VIZ_PAGES:
            html = viz_page.read_text(encoding="utf-8")
            self.assertIn('lang="ru"', html, viz_page.name)
            for forbidden in ("<script src=", "<link ", "cdn.", "unpkg", "jsdelivr"):
                self.assertNotIn(forbidden, html, viz_page.name)

    def test_links_back_to_toc_and_previous_lecture(self):
        self.assertIn('href="../oglavlenie.html"', self.html)
        prev_html = PREV_PAGE.read_text(encoding="utf-8")
        self.assertIn("bezopasnost_dannyh.html", prev_html)
        self.assertIn("ochistka_dannyh.html", self.html)


if __name__ == "__main__":
    unittest.main()
