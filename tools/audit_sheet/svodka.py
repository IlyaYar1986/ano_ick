"""Сводка ответов «Практики 1.1: аудит задач» из таблицы «Ответы 1.1».

Форма только добавляет строки, поэтому для каждого участника берётся последняя.
Тестовые строки (номер или специальность начинаются с «ТЕСТ») пропускаются.

Запуск: python3 tools/audit_sheet/svodka.py
"""
import csv
import io
import json
import urllib.parse
import urllib.request
from collections import Counter, defaultdict

SHEET_ID = '1dMvvAqnJ7loxq7mn7ryuoYPXAtbnPIT5708gIRYTLgM'
SHEET_NAME = 'Ответы на форму (1)'
LABELS = {'ai': 'Отдать ИИ', 'help': 'Вместе', 'me': 'Только я'}


def load_rows():
    url = (f'https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet='
           + urllib.parse.quote(SHEET_NAME))
    with urllib.request.urlopen(url, timeout=30) as r:
        return list(csv.DictReader(io.StringIO(r.read().decode('utf-8'))))


def main():
    latest = {}
    for row in load_rows():  # строки идут по времени, последняя перезаписывает прежние
        pid = row.get('Участник', '')
        if not pid or pid.startswith('ТЕСТ') or row.get('Специальность', '').startswith('ТЕСТ'):
            continue
        latest[pid] = row

    stats = defaultdict(Counter)
    topics = {}
    custom = []
    for row in latest.values():
        try:
            data = json.loads(row.get('Данные') or '{}')
        except json.JSONDecodeError:
            continue
        for t in data.get('tasks', []):
            stats[t['text']][t['v']] += 1
            topics[t['text']] = t.get('topic', '')
        custom += data.get('custom', [])

    print(f'Участников: {len(latest)}\n')
    print('Специальности:')
    for who, n in Counter(r.get('Специальность') or '— не указана' for r in latest.values()).most_common():
        print(f'  {who}: {n}')

    print('\nЗадачи (по числу желающих работать с ИИ):')
    rows = sorted(stats.items(), key=lambda kv: -(kv[1]['ai'] + kv[1]['help']))
    for text, c in rows:
        topic = f' [тема {topics[text]}]' if topics.get(text) else ''
        print(f"  {text}{topic}: отдать ИИ {c['ai']}, вместе {c['help']}, только я {c['me']}")

    if custom:
        print('\nСвои задачи участников:')
        for t in custom:
            print(f'  • {t}')


if __name__ == '__main__':
    main()
