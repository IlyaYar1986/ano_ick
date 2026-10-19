/**
 * Приём ответов из «Практики 1.1: аудит задач» (index.html, блок 10)
 * в Google Таблицу. Одна строка — один браузер-участник: повторная
 * отправка того же браузера обновляет его строку, а не добавляет новую.
 * Лист «Сводка» пересчитывается после каждой отправки.
 */

const SHEET_ANSWERS = 'Ответы';
const SHEET_SUMMARY = 'Сводка';
const HEADER = ['Участник', 'Первая отправка', 'Обновлено', 'Специальность',
  'Отдать ИИ', 'Вместе', 'Только я', 'Задачи «Отдать ИИ»', 'Задачи «Вместе»',
  'Задачи «Только я»', 'Свои задачи', 'id браузера', 'json'];
const LABELS = { ai: 'Отдать ИИ', help: 'Вместе', me: 'Только я' };

function doPost(e) {
  const lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    const data = JSON.parse(e.postData.contents);
    const id = String(data.id || '').slice(0, 64);
    if (!/^[0-9a-f-]{36}$/i.test(id)) return reply({ ok: false, error: 'bad id' });

    const tasks = (Array.isArray(data.tasks) ? data.tasks : []).slice(0, 80).map(t => ({
      text: clip(t.text, 160), topic: clip(t.topic, 8), group: clip(t.group, 60),
      v: LABELS[t.v] ? t.v : '',
    })).filter(t => t.text && t.v);
    const custom = (Array.isArray(data.custom) ? data.custom : []).slice(0, 30).map(s => clip(s, 160));
    const who = clip(data.who, 120);

    const ss = SpreadsheetApp.getActiveSpreadsheet();
    const sh = ss.getSheetByName(SHEET_ANSWERS) || ss.insertSheet(SHEET_ANSWERS);
    if (sh.getLastRow() === 0) {
      sh.appendRow(HEADER);
      sh.setFrozenRows(1);
      sh.getRange(1, 1, 1, HEADER.length).setFontWeight('bold');
    }

    const now = new Date();
    const list = v => tasks.filter(t => t.v === v).map(t => t.text).join('\n');
    const count = v => tasks.filter(t => t.v === v).length;
    const ids = sh.getLastRow() > 1 ? sh.getRange(2, 12, sh.getLastRow() - 1, 1).getValues().map(r => r[0]) : [];
    const idx = ids.indexOf(id);
    const rowNum = idx >= 0 ? idx + 2 : sh.getLastRow() + 1;
    const first = idx >= 0 ? sh.getRange(rowNum, 2).getValue() : now;

    const row = [`Участник ${rowNum - 1}`, first, now, safe(who),
      count('ai'), count('help'), count('me'),
      safe(list('ai')), safe(list('help')), safe(list('me')), safe(custom.join('\n')),
      id, JSON.stringify({ who, tasks, custom })];
    sh.getRange(rowNum, 1, 1, row.length).setValues([row]);

    rebuildSummary(ss, sh);
    return reply({ ok: true });
  } catch (err) {
    return reply({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}

/* Сводка: по каждой задаче — сколько участников выбрали каждый вариант. */
function rebuildSummary(ss, sh) {
  const sum = ss.getSheetByName(SHEET_SUMMARY) || ss.insertSheet(SHEET_SUMMARY);
  const last = sh.getLastRow();
  const stats = {};
  if (last > 1) {
    sh.getRange(2, 13, last - 1, 1).getValues().forEach(([json]) => {
      let d; try { d = JSON.parse(json); } catch (e) { return; }
      d.tasks.forEach(t => {
        const k = t.text;
        stats[k] = stats[k] || { group: t.group, topic: t.topic, ai: 0, help: 0, me: 0 };
        stats[k][t.v]++;
      });
    });
  }
  const rows = Object.entries(stats)
    .map(([text, s]) => [s.group, safe(text), s.topic ? `тема ${s.topic}` : '', s.ai, s.help, s.me, s.ai + s.help])
    .sort((a, b) => b[6] - a[6] || b[3] - a[3]);
  sum.clear();
  const head = ['Группа', 'Задача', 'Тема курса', 'Отдать ИИ', 'Вместе', 'Только я', 'Хотят с ИИ (всего)'];
  sum.getRange(1, 1, 1, head.length).setValues([head]).setFontWeight('bold');
  sum.setFrozenRows(1);
  if (rows.length) sum.getRange(2, 1, rows.length, head.length).setValues(rows);
  sum.getRange(rows.length + 3, 1).setValue(`Участников: ${Math.max(last - 1, 0)}`).setFontWeight('bold');
}

function doGet() {
  return reply({ ok: true, info: 'Приём ответов аудита задач работает' });
}

function clip(s, n) { return String(s == null ? '' : s).trim().slice(0, n); }
/* Защита от формул: строка, начинающаяся с =, +, -, @, станет текстом */
function safe(s) { return /^[=+\-@]/.test(s) ? "'" + s : s; }
function reply(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}
