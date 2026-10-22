import re
import subprocess
import unicodedata
import unittest
import urllib.parse
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LECTURE = ROOT / "web" / "tema_1_3.html"
PRACTICE = ROOT / "web" / "praktika_1_3.html"
INDEX = ROOT / "index.html"
VIZ_PAGES = ["shtraf_kalkulyator.html", "sravnenie_servisov.html", "algoritm_incidenta.html",
             "profil_po_zaprosam.html", "pd_ili_net.html", "svetofor_trenazher.html",
             "obezlichivatel.html", "moshennik_ili_net.html"]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.hrefs = []
        self.iframe_srcs = []
        self.img_srcs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "id" in values:
            self.ids.append(values["id"])
        if tag == "a" and "href" in values:
            self.hrefs.append(values["href"])
        if tag == "iframe" and "src" in values:
            self.iframe_srcs.append(values["src"])
        if tag == "img" and "src" in values:
            self.img_srcs.append(values["src"])


def parse(path):
    html = path.read_text(encoding="utf-8")
    parser = PageParser()
    parser.feed(html)
    return html, parser


class LecturePageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html, cls.parser = parse(LECTURE)

    def test_required_sections(self):
        required = {"hero", "s1", "s2", "s3", "s4", "s5", "s6", "s7", "s8", "checklist", "quiz", "final"}
        self.assertTrue(required.issubset(set(self.parser.ids)))

    def test_no_duplicate_ids(self):
        dups = {i for i in self.parser.ids if self.parser.ids.count(i) > 1}
        self.assertEqual(dups, set())

    def test_embeds_existing_demos(self):
        for page in VIZ_PAGES:
            self.assertIn(page, self.parser.iframe_srcs)
            self.assertTrue((ROOT / "web" / page).is_file(), page)

    def test_two_logos(self):
        self.assertIn("../png/brand/logo_ick.webp", self.parser.img_srcs)
        self.assertIn("../png/brand/logo_club_bulb.webp", self.parser.img_srcs)

    def test_infographics_are_light(self):
        """Картинки — WebP с мобильной версией; рядом PNG для кнопки «Скачать»."""
        images = [src for src in self.parser.img_srcs if src.startswith("../png/tema_1_3/")]
        for src in images:
            self.assertTrue(src.endswith(".webp"), src)
            full = (ROOT / "web" / src).resolve()
            self.assertLess(full.stat().st_size, 400_000, src)
            self.assertTrue(full.with_name(full.stem + "_960.webp").is_file(), src)
            self.assertTrue(full.with_suffix(".png").is_file(), src)
        self.assertEqual(self.html.count("srcset="), len(images))

    def test_infographics_have_placeholders(self):
        images = [src for src in self.parser.img_srcs if src.startswith("../png/tema_1_3/")]
        self.assertEqual(len(images), 10)
        self.assertEqual(self.html.count('class="img-missing-caption"'), 10)
        for src in images:
            self.assertTrue((ROOT / "web" / src).resolve().is_file(), src)

    def test_key_markers(self):
        for marker in ["243-ФЗ", "152-ФЗ", "13.11", "272.1", "1 июля 2025", "Колледж", "10–15 тыс. ₽", "кодовом слове"]:
            self.assertIn(marker, self.html, marker)

    def test_links_to_practice_and_course(self):
        self.assertIn("praktika_1_3.html", self.parser.hrefs)
        self.assertIn("../index.html", self.parser.hrefs)


class PracticePageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html, cls.parser = parse(PRACTICE)

    def test_required_sections(self):
        self.assertTrue({"hero", "s1", "s2", "s3", "s4", "s5"}.issubset(set(self.parser.ids)))

    def test_no_duplicate_ids(self):
        dups = {i for i in self.parser.ids if self.parser.ids.count(i) > 1}
        self.assertEqual(dups, set())

    def test_seven_cases(self):
        for n in range(1, 8):
            self.assertIn(f"case{n}", self.parser.ids)
        self.assertEqual(self.html.count('class="case-live"'), 4)

    def test_corrected_facts(self):
        self.assertIn("ВКонтакте", self.html)
        self.assertNotIn("Instagram", self.html)
        self.assertIn("общий аккаунт", self.html)
        self.assertNotIn("500 000 рублей или лишение", self.html)

    def test_policy_builder_and_checklist(self):
        self.assertEqual(self.html.count('["', self.html.index("POLICY_QUESTIONS"), self.html.index("const policyRoot")), 10)
        for marker in ["policy-build", "policy-prompt", "sc-list", "ick-praktika-1-3-policy", "не придумывай номера законов"]:
            self.assertIn(marker, self.html, marker)

    def test_practice_infographics_and_tools(self):
        images = [src for src in self.parser.img_srcs if src.startswith("../png/tema_1_3/")]
        self.assertEqual(len(images), 4)
        for src in images:
            self.assertTrue((ROOT / "web" / src).resolve().is_file(), src)
        self.assertIn("obezlichivatel.html", self.parser.iframe_srcs)
        self.assertIn("lightbox", self.parser.ids)

    def test_link_back_to_lecture(self):
        self.assertIn("tema_1_3.html", self.parser.hrefs)


class PublishedSiteTest(unittest.TestCase):
    """На сайт выкладываются только темы 1.1 и 1.3: всё, на что они ссылаются, должно быть в git, а клубных ссылок быть не должно."""

    PAGES = ["index.html", "web/tema_1_3.html", "web/praktika_1_3.html"]
    REF = re.compile(r"""(?:src|href|data-fs-src)\s*=\s*["']([^"'#?]+)|open(?:Lb|Fs)\(\s*['"]([^'"]+)""")
    SRCSET = re.compile(r"""srcset\s*=\s*["']([^"']+)""")

    @classmethod
    def setUpClass(cls):
        out = subprocess.run(["git", "ls-files", "-z"], cwd=ROOT, capture_output=True, text=True).stdout
        cls.tracked = {unicodedata.normalize("NFC", p) for p in out.split("\0") if p}

    def test_no_club_links(self):
        html = INDEX.read_text(encoding="utf-8")
        for page in ["oglavlenie.html", "seminar_25_45.html", "agentnye_sistemy.html", "instrumenty_mcp_skills.html", "ответы-участников.html"]:
            self.assertNotIn(page, html, page)

    def test_all_references_are_published(self):
        if not self.tracked:
            self.skipTest("нет git")
        seen, queue, missing = set(), list(self.PAGES), []
        while queue:
            path = queue.pop()
            if path in seen:
                continue
            seen.add(path)
            if unicodedata.normalize("NFC", path) not in self.tracked:
                missing.append(path)
                continue
            if not path.endswith((".html", ".css")):
                continue
            text = (ROOT / path).read_text(encoding="utf-8")
            base = Path(path).parent
            refs = [next(g for g in m.groups() if g) for m in self.REF.finditer(text)]
            for m in self.SRCSET.finditer(text):
                refs += [part.strip().split()[0] for part in m.group(1).split(",")]
            # лайтбокс скачивает PNG вместо WebP
            refs += [r[:-5] + ".png" for r in refs if r.endswith(".webp") and "/png/" in "/" + r and not r.endswith("_960.webp") and "brand/" not in r]
            for ref in refs:
                if re.match(r"^(https?:|mailto:|data:|javascript:|//|\$\{)", ref):
                    continue
                target = (ROOT / base / urllib.parse.unquote(ref)).resolve()
                try:
                    queue.append(str(target.relative_to(ROOT.resolve())))
                except ValueError:
                    continue
        self.assertEqual(missing, [])


class IndexLinksTest(unittest.TestCase):
    def test_index_links_to_tema_1_3(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertIn('href="web/tema_1_3.html"', html)
        self.assertIn('href="web/praktika_1_3.html"', html)


if __name__ == "__main__":
    unittest.main()
