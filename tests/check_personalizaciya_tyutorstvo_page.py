import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "web" / "personalizaciya_tyutorstvo.html"


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


class PersonalizaciyaTyutorstvoPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""
        cls.parser = PageParser()
        cls.parser.feed(cls.html)

    def test_page_exists_with_required_sections(self):
        self.assertTrue(PAGE.is_file())
        required = {
            "hero", "problema", "personalizaciya", "pochemu-seychas",
            "ii-tyutor", "vozmozhnosti", "keysy", "rossiya", "primenenie",
            "cheklist", "kviz", "zaklyuchenie",
        }
        self.assertTrue(required.issubset(self.parser.ids))
        duplicates = [
            element_id
            for element_id, count in self.parser.id_counts.items()
            if count > 1
        ]
        self.assertEqual(duplicates, [], f"Duplicate ids: {duplicates}")

    def test_no_link_to_index(self):
        self.assertNotIn('href="../index.html"', self.html)
        self.assertNotIn("href=\"index.html\"", self.html)

    def test_problema_section_has_distribution_stats(self):
        for marker in ("30%", "40%", "слишком просто", "слишком сложно", "оптимальная"):
            self.assertIn(marker, self.html)

    def test_personalizaciya_section_has_five_principles(self):
        for marker in (
            "Содержание под его уровень",
            "Удобный темп",
            "Подходящий формат подачи",
            "Обратную связь в нужный момент",
            "Поддержку именно там",
        ):
            self.assertIn(marker, self.html)
        self.assertGreaterEqual(self.parser.details, 5)

    def test_bloom_section_has_corrected_effect_sizes(self):
        for marker in ("Bloom", "1984", "98%", "VanLehn", "Nickow", "Kraft"):
            self.assertIn(marker, self.html)
        self.assertNotIn("0,3–0,8 стандартных отклонений", self.html)

    def test_ii_tyutor_section_has_socratic_dialogue(self):
        for marker in ("Khanmigo", "2x + 5 = 13", "Убрать 5", "dialog-next"):
            self.assertIn(marker, self.html)

    def test_ii_tyutor_section_has_traditional_vs_ai_comparison(self):
        for marker in (
            "Традиционно",
            "С ИИ-тьютором",
            "Через несколько дней возвращается к теме",
        ):
            self.assertIn(marker, self.html)

    def test_vozmozhnosti_section_covers_capabilities_and_limits(self):
        for marker in (
            "Диагностика в реальном времени",
            "Эмоциональная поддержка",
            "152-ФЗ",
            "академическ",
        ):
            self.assertIn(marker, self.html)

    def test_keysy_section_has_six_corrected_cases(self):
        for marker in (
            "Squirrel AI",
            "Carnegie Learning MATHia",
            "CENTURY Tech",
            "Jill Watson",
            "Duolingo",
            "Khanmigo",
            "40 миллионов",
            "заявление компании",
            "Tier 2",
            "не подтверждается ни Khan Academy",
        ):
            self.assertIn(marker, self.html)
        self.assertNotIn("более 4 миллионов студентов", self.html)

    def test_rossiya_section_has_updated_platform_figures(self):
        for marker in (
            "Учи.ру",
            "Репетитор AI",
            "AI360",
            "ВКИ НГУ",
            "156 человек",
            "85% всех сдававших ЕГЭ",
        ):
            self.assertIn(marker, self.html)
        self.assertNotIn("220 000", self.html)

    def test_primenenie_section_has_three_levels_and_copy_buttons(self):
        for marker in ("Быстрый старт", "Продвинутый", "Системный", "data-copy", "Скопировать"):
            self.assertIn(marker, self.html)
        self.assertGreaterEqual(self.html.count('class="level-panel"'), 3)

    def test_cheklist_section_has_six_items(self):
        self.assertEqual(self.html.count('data-checklist-item="'), 6)
        self.assertIn("checklist-progress", self.html)

    def test_kviz_section_has_five_questions(self):
        self.assertEqual(self.html.count('class="quiz-question"'), 5)
        self.assertIn("quiz-score", self.html)

    def test_zaklyuchenie_has_five_theses_and_no_broken_practice_links(self):
        for marker in (
            "Массовое образование",
            "не роскошь, а необходимость",
            "не заменяется",
        ):
            self.assertIn(marker, self.html)
        self.assertNotIn('href="practika', self.html)

    def test_all_hero_nav_targets_exist(self):
        for anchor in ("problema", "ii-tyutor", "keysy", "primenenie", "kviz"):
            self.assertIn(f'id="{anchor}"', self.html)

    def test_no_stray_placeholder_markers(self):
        for marker in ("TODO", "TBD", "lorem ipsum", "заглушка"):
            self.assertNotIn(marker.lower(), self.html.lower())


if __name__ == "__main__":
    unittest.main()
