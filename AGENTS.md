# AGENTS.md

This file provides guidance to coding agents working with code in this repository.

## Ufa adaptation (read first)

This is a copy of `_Клуб Образование/Urok2_LLM`, adapted for the customer АНО ДПО «Институт цифровых компетенций» (ИЦК, Уфа), course «Использование LLM и Агентов в работе преподавателя» (19.10–12.11.2026, 55 ак. ч.). Audience: college (СПО) teachers in Ufa. Never edit the original folder — all changes happen here.

- Brand rules: `../../Бренд ИЦК/ДНК_и_стиль_ИЦК.md`. Palette: primary `#562d86`, UI accent `#6654d9`, logo gradient `#00abea → #0090cf → #2868ab → #464f9a → #533389`, text `#2c2d30`, surfaces `#f4f5fa`/`#e3e3e8`. Font: IBM Plex Sans.
- Two logos everywhere they appear together: customer first (`png/brand/logo_ick.png`), author second (`png/brand/logo_club_bulb.png`, the club bulb with a transparent background).
- **Only topics 1.1 and 1.3 are published.** The site (GitHub Pages) contains `index.html` (topic 1.1), `web/tema_1_3.html`, `web/praktika_1_3.html` and the demos and images they reference. All other club pages (`oglavlenie.html`, seminar, agents, цифровой след, очистка данных, тьюторство, безопасность 4.4) and their `png/` folders stay on disk only as examples for preparing lessons — they are listed in `.gitignore`; never link to them from published pages and never re-add them. Their old tests live in `tests/klub/` (not run, not published). `tests/check_tema_1_3_pages.py` fails if a published page references a file that is not tracked.
- When a new topic page is added, add it to `PAGES` in that test and make sure its demos/images are tracked.
- Teaching materials per topic (speech, конспект, recording, transcript, lecture review, past-stream sources) live outside the repo in `../Темы/<topic>/`, each with a README. Put new topic materials there, not in `Docs/`.
- Topic 1.3 (personal data, AI law 243-ФЗ): lecture `web/tema_1_3.html` and practice `web/praktika_1_3.html` use the ИЦК styling; plan and image prompts in `../Темы/Тема 1.3 Персональные данные и безопасность/План_страниц_и_промпты_картинок.md`, infographics (14 frames) go to `png/tema_1_3/`, trainers `web/profil_po_zaprosam.html`, `web/pd_ili_net.html`, `web/svetofor_trenazher.html`, `web/obezlichivatel.html`, `web/moshennik_ili_net.html`, test `tests/check_tema_1_3_pages.py`. Legal figures were checked against КоАП/УК on 19.10.2026 — re-verify before reusing.

## Project overview

Static educational website for an LLM/AI seminar (in Russian). There is no application framework, package manager, bundler, or build step — plain HTML5 with embedded CSS and vanilla JavaScript. Pages are self-contained and meant to be opened directly or served as static files.

## Commands

- Serve locally: `python3 -m http.server 8000` from the project root, then open `http://127.0.0.1:8000/`. Don't rely on `file://` — pages embed local iframes that require HTTP.
- Run tests: `python3 -m unittest discover -s tests -p "check_*.py" -v` from the project root.
- Run a single test file: `python3 -m unittest tests.check_seminar_page -v` (or `tests.check_education_tools_page`).
- No linter, formatter, or build step exists in this repo.

## Repository structure

- `index.html` — main/original long-form LLM seminar landing page (single self-contained file with embedded CSS/JS).
- `web/` — standalone interactive visualizations and secondary lesson pages (one HTML file each), plus `web/shared.css` for visual normalization of smaller interactive demos. Larger pages carry their own embedded CSS instead of using the shared stylesheet.
- `png/` — generated seminar infographics, including the agent-systems series under `png/zanyatie2_agentnye_sistemy/` (see its `README.md` for the image-to-topic mapping, sourced from `Docs/Zanyatie2_Agentnye_sistemy.txt`).
- `Практика_агенты/` — workshop materials analyzing teacher-submitted "agent idea" questionnaires; `Практика_агенты/Агенты_разбор/` contains one write-up per unique agent idea (see its `README.md` for the summary table and consolidation notes) plus subfolders of practice exercises (OpenCode-based).
- `Docs/` — planning/spec source material, mostly excluded from git (see Notable `.gitignore` behavior below).
- `tests/` — Python `unittest` structural checks for specific pages (see Testing below).

## Architecture and conventions

- **UI language is Russian.** All learner-facing content, comments in HTML, and copy should be written in Russian.
- **Design system** (used across main pages): light `#f4f5fa` background, white cards, ИЦК violet primary / logo-gradient cyan secondary accents, fixed horizontal nav bar, numbered badges stepping along the logo gradient, soft shadows, rounded cards. Follow the existing visual language in `index.html` rather than introducing new styling systems.
- **Page composition pattern:** large/main pages are single self-contained HTML files with embedded `<style>`/`<script>`. Smaller interactive demos in `web/` may link `web/shared.css` instead of duplicating styles.
- **Reuse over duplication:** embed existing interactive demos via `<iframe>` cards with a fullscreen overlay toggle; embed existing PNG infographics with a click-to-zoom lightbox. Avoid re-implementing a visualization that already exists as a standalone page/image.
- **Responsive typography:** use `clamp()` for font sizing and media queries for layout; pages are also viewed on a projector, so preserve readability at large sizes.
- **Navigation:** sections use stable `id` attributes so the fixed nav bar can track scroll position (typically via `IntersectionObserver`).
- **Path conventions:** pages under `web/` reference images as `../png/...` and reference sibling demo pages by basename. Filenames throughout the repo frequently contain Cyrillic characters and spaces — always quote paths in shell commands, and prefer obtaining exact filenames via `find`/`rg --files` rather than retyping them (macOS Unicode normalization can make visually identical filenames differ at the byte level).
- Avoid introducing new frameworks, bundlers, or unrelated restructuring — this is intentionally a zero-build static site.

## Testing

Tests in `tests/` are Python `unittest` cases that parse specific HTML pages (via `html.parser.HTMLParser`) and assert on structural invariants: required section `id`s, absence of duplicate IDs, presence of specific text markers/keywords, and correct cross-page links (e.g. that `index.html` and other pages link forward to newer continuation pages). When adding or restructuring a page covered by `tests/check_*.py`, check the corresponding test file for the exact IDs/markers/links it expects.

There is no browser-automation test suite checked in, but changes to interactive pages should still be verified in a real browser: check desktop and mobile viewport widths, the fixed nav, accordions, the image lightbox, the fullscreen iframe overlay, and the browser console for errors, after serving the site over HTTP.

## Notable `.gitignore` behavior

- `Docs/*` is ignored by default, but `Docs/superpowers/` is force-added — it holds design/spec records, and is unaffected by the broad ignore pattern (this works despite the ignore rule because the ignore matching is case-insensitive on the default macOS filesystem, so the exception must be added explicitly for that subpath).
- Several superseded visualizations under `web/` and one unused image under `png/` are intentionally gitignored — do not resurrect them without checking why they were retired.
- `.serena/`, `.superpowers/`, `.worktrees/`, and `.playwright-cli/` are tool-local directories and are gitignored.
