"""Read Gothic text exports, align DE/PL and index a Markdown guide. Python 3.10+; stdlib only."""
from __future__ import annotations

import argparse
import base64
from collections import Counter, defaultdict
import csv
from difflib import SequenceMatcher
import hashlib
import io
import json
from pathlib import Path
import re
import sqlite3
import sys
import unicodedata

DEFAULT_CONFIG = Path(__file__).resolve().parents[1] / 'materialy/epilog.json'
KEY = ('ID', 'SYMBOL', 'USE', 'TRACE')
CONTEXT = ('SYMBOL', 'USE', 'TRACE')
KINDS = ('topic', 'npc', 'item', 'journal', 'dialogue', 'document', 'other')


def normalize(text):
    text = unicodedata.normalize('NFKD', text.casefold().replace('ł', 'l'))
    return ' '.join(''.join(c for c in text if not unicodedata.combining(c)).split())


def heading_name(text):
    text = re.sub(r'\s*\{#[^}]+\}\s*$', '', text)
    text = re.sub(r'\\([!_\-()])', r'\1', text)
    return re.sub(r'\s+\((?:achtung\b|beendet\b)[^()]*\)\s*$', '', text, flags=re.I).strip()


def read_export(path, column, encoding=None, delimiter=None):
    raw = path.read_bytes()
    encoding = encoding or ('utf-16' if raw.startswith((b'\xff\xfe', b'\xfe\xff')) else 'utf-8-sig')
    text = raw.decode(encoding, errors='strict')
    if not text.strip():
        raise ValueError(f'{path}: pusty eksport')
    delimiter = delimiter or ('\t' if '\t' in text.splitlines()[0] else ',')
    reader = csv.reader(io.StringIO(text, newline=''), delimiter=delimiter, strict=True)
    header = next(reader, [])
    if len(header) != len(set(header)) or not set((*KEY, 'NR', 'FILENR', column)) <= set(header):
        raise ValueError(f'{path}: brak wymaganych kolumn lub powtórzone nagłówki: {header}')
    rows = []
    while True:
        start = reader.line_num + 1
        values = next(reader, None)
        if values is None:
            break
        if not values:  # Truly empty physical lines are not records.
            continue
        if len(values) != len(header):
            raise ValueError(f'{path}:{start}: {len(values)} pól, oczekiwano {len(header)}')
        row = dict(zip(header, values))
        if any(not row[k].strip() for k in KEY):
            raise ValueError(f'{path}:{start}: pusty element klucza {KEY}')
        rows.append({'text': row[column], 'source': {
            'file': path.name, 'line': start, 'line_end': reader.line_num,
            'column': column, **{k: row[k] for k in ('NR', 'FILENR', *KEY)},
        }})
    return rows, {
        'path': str(path), 'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw),
        'encoding': encoding, 'delimiter': delimiter, 'column': column, 'records': len(rows),
        'columns': header,
    }


def key(row, fields=KEY):
    return tuple(row['source'][k] for k in fields)


def category(row):
    symbol, use, trace = (row['source'][k] for k in CONTEXT)
    if symbol.startswith('TOPIC_'):
        return 'topic'  # Includes service headings, not just quests.
    if use == 'C_NPC.NAME':
        return 'npc'
    if use == 'C_ITEM.NAME':
        return 'item'
    if use == 'B_LOGENTRY.ENTRY':
        return 'journal'
    if trace == 'SUBTITLE' or use in ('C_INFO.DESCRIPTION', 'INFO_ADDCHOICE.PAR1'):
        return 'dialogue'
    if use.startswith(('DOC_PRINTLINE.', 'DOC_PRINTLINES.')):
        return 'document'
    return 'other'


def text_issues(text, lang):
    issues = []
    if not text.strip():
        issues.append('empty')
    if '\ufffd' in text or any(ord(c) < 32 and c not in '\r\n\t' for c in text):
        issues.append('invalid_character')
    # Heuristics only: leave the original text intact, including foreign names.
    if re.search(r'[ÃÂ¹³œŒŸ¤¦¬]', text) or (lang == 'pl' and re.search(r'[ŕĺčţű]', text)):
        issues.append('suspected_encoding')
    if lang == 'pl' and re.search(r'[\u0400-\u04ff]', text):
        issues.append('cyrillic_in_pl')
    return issues


def align(de, pl):
    indexes = []
    contexts = []
    for rows in (de, pl):
        idx, ctx = defaultdict(list), defaultdict(list)
        for i, row in enumerate(rows):
            idx[key(row)].append(i)
            ctx[key(row, CONTEXT)].append(i)
        indexes.append(idx)
        contexts.append(ctx)
    used = [set(), set()]
    pairs = []

    def add(di, pi, status, candidates=None):
        left = de[di] if di is not None else None
        right = pl[pi] if pi is not None else None
        row = left or right
        pairs.append({'kind': category(row), 'status': status,
                      **{k.lower(): row['source'][k] for k in KEY},
                      'de': left, 'pl': right, 'candidates': candidates or [],
                      'issues': {lang: text_issues(r['text'], lang)
                                 for lang, r in [('de', left), ('pl', right)] if r}})
        if di is not None:
            used[0].add(di)
        if pi is not None:
            used[1].add(pi)

    for di, row in enumerate(de):
        matches = indexes[1].get(key(row), [])
        if len(indexes[0][key(row)]) == len(matches) == 1:
            add(di, matches[0], 'exact')
    for di, row in enumerate(de):
        if di in used[0]:
            continue
        ctx = key(row, CONTEXT)
        matches = contexts[1].get(ctx, [])
        # IDs can change across exports; never resolve duplicate contexts by row order.
        if len(contexts[0][ctx]) == len(matches) == 1 and matches[0] not in used[1]:
            add(di, matches[0], 'context_review')
    for side, rows in enumerate((de, pl)):
        for i, row in enumerate(rows):
            if i in used[side]:
                continue
            candidates = [((pl if side == 0 else de)[j])['source']
                          for j in contexts[1-side].get(key(row, CONTEXT), [])]
            status = 'ambiguous' if candidates else ('de_only' if side == 0 else 'pl_only')
            add(i if side == 0 else None, i if side == 1 else None, status, candidates)
    assert sum(p['de'] is not None for p in pairs) == len(de)
    assert sum(p['pl'] is not None for p in pairs) == len(pl)
    return pairs


def prepare_guide(text, quest_section='Quests', quest_level=3):
    lines = text.splitlines()
    images = {}
    cleaned = []
    for line in lines:
        match = re.fullmatch(r'\[([^]]+)\]:\s*<?data:image/(png|jpeg|gif|webp);base64,([A-Za-z0-9+/=\s]+)>?\s*', line)
        if match:
            label, extension, data = match.groups()
            # Use numbered filenames, never an untrusted Markdown label as a path.
            filename = f'image-{len(images)+1}.{extension}'
            images[filename] = base64.b64decode(re.sub(r'\s', '', data), validate=True)
            line = f'[{label}]: images/{filename}'
        cleaned.append(line)
    headings = []
    in_quests, section_level = False, 0
    for i, line in enumerate(cleaned):
        match = re.match(r'^(#{1,6})\s+(.+?)\s*$', line)
        if not match:
            continue
        level, title = len(match[1]), match[2]
        name = heading_name(title)
        if in_quests and level <= section_level:
            in_quests = False
        if normalize(name) == normalize(quest_section):
            in_quests, section_level = True, level
        headings.append({'number': len(headings)+1, 'title': title, 'name': name,
                         'level': level, 'start_line': i+1,
                         'quest': in_quests and level == quest_level})
    for i, section in enumerate(headings):
        # Each chunk ends at the next heading; line coordinates refer to the original.
        end = headings[i+1]['start_line']-1 if i+1 < len(headings) else len(cleaned)
        section['end_line'] = end
        section['text'] = '\n'.join(cleaned[section['start_line']-1:end]).rstrip()
    people = []
    for i, line in enumerate(cleaned, 1):
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in re.split(r'(?<!\\)\|', line.strip().strip('|'))]
        if len(cells) < 3:
            continue
        symbol = cells[2].replace('\\_', '_').strip('`').upper()
        if re.fullmatch(r'[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)+', symbol):
            people.append({'line': i, 'name': cells[0], 'symbol': symbol})
    return '\n'.join(cleaned)+'\n', images, headings, people


def guide_matches(sections, pairs):
    topics = [p for p in pairs if p['kind'] == 'topic' and p['de']]
    result = []
    for section in sections:
        if not section['quest']:
            continue
        query = normalize(section['name'])
        matches = [p for p in topics if normalize(p['de']['text']) == query]
        exact = (len(matches) == 1 and matches[0]['status'] == 'exact'
                 and not any(matches[0]['issues'].values()))
        if exact:
            candidates = matches
        else:
            scored = sorted(topics, key=lambda p: SequenceMatcher(None, query, normalize(p['de']['text'])).ratio(), reverse=True)
            candidates = [p for p in scored[:3]
                          if SequenceMatcher(None, query, normalize(p['de']['text'])).ratio() >= .55]
        result.append({'section': section, 'status': 'exact' if exact else 'review',
                       'candidates': candidates})
    return result


def name_conflicts(pairs):
    groups = defaultdict(list)
    for p in pairs:
        if p['kind'] in ('topic', 'npc', 'item') and p['de'] and p['pl']:
            groups[(p['kind'], p['de']['text'])].append(p)
    return [values for values in groups.values() if len({p['pl']['text'] for p in values}) > 1]


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', '<br>').replace('\r', '')


def source_ref(row):
    if not row:
        return '—'
    s = row['source']
    return f"{s['file']}:{s['line']} (NR {s['NR']}, {s['column']})"


def write_database(path, pairs, sections, sources, config_hash):
    # Build separately and replace only the derived database on successful completion.
    temporary = path.with_suffix('.tmp.sqlite3')
    with sqlite3.connect(temporary) as db:
        db.executescript('''
            DROP TABLE IF EXISTS texts; DROP TABLE IF EXISTS sections; DROP TABLE IF EXISTS metadata;
            CREATE TABLE texts (number INTEGER PRIMARY KEY, kind TEXT, status TEXT, symbol TEXT,
                                search_de TEXT, search_pl TEXT, search_key TEXT, has_issues INTEGER, data TEXT);
            CREATE INDEX by_kind ON texts(kind);
            CREATE INDEX by_symbol ON texts(symbol);
            CREATE TABLE sections (number INTEGER PRIMARY KEY, search_title TEXT, data TEXT);
            CREATE TABLE metadata (data TEXT);
        ''')
        for i, pair in enumerate(pairs, 1):
            pair['number'] = i
            db.execute('INSERT INTO texts VALUES (?,?,?,?,?,?,?,?,?)', (
                i, pair['kind'], pair['status'], pair['symbol'],
                normalize(pair['de']['text'] if pair['de'] else ''),
                normalize(pair['pl']['text'] if pair['pl'] else ''),
                normalize(' '.join(pair[k.lower()] for k in KEY)),
                int(any(pair['issues'].values())), json.dumps(pair, ensure_ascii=False)))
        db.executemany('INSERT INTO sections VALUES (?,?,?)',
                       [(s['number'], normalize(s['name']), json.dumps(s, ensure_ascii=False)) for s in sections])
        db.execute('INSERT INTO metadata VALUES (?)', (json.dumps({'sources': sources, 'config_sha256': config_hash}, ensure_ascii=False),))
    # sqlite3's context manager commits but does not close the handle on Windows.
    db.close()
    temporary.replace(path)


def build(config_path):
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding='utf-8-sig'))
    root = config_path.parent
    out = (root / config['output']).resolve()
    source_paths = [(root / config[lang]['path']).resolve() for lang in ('de', 'pl', 'guide')]
    if any(p == out or out in p.parents for p in source_paths):
        raise ValueError('Katalog wyników nie może zawierać oryginalnych źródeł.')
    rows, sources = {}, {}
    for lang, path in zip(('de', 'pl'), source_paths):
        spec = config[lang]
        rows[lang], sources[lang] = read_export(path, spec['column'], spec.get('encoding'), spec.get('delimiter'))
    pairs = align(rows['de'], rows['pl'])
    guide_spec = config['guide']
    raw = source_paths[2].read_bytes()
    guide_text = raw.decode(guide_spec.get('encoding', 'utf-8-sig'))
    clean, images, sections, people = prepare_guide(
        guide_text, guide_spec.get('quest_section', 'Quests'), guide_spec.get('quest_level', 3))
    sources['guide'] = {'path': str(source_paths[2]), 'sha256': hashlib.sha256(raw).hexdigest(),
                        'bytes': len(raw), 'credit': guide_spec.get('credit'),
                        'mod_version': guide_spec.get('mod_version')}
    quests = guide_matches(sections, pairs)
    conflicts = name_conflicts(pairs)
    npc_index = defaultdict(list)
    for p in pairs:
        if p['kind'] == 'npc':
            npc_index[p['symbol'].upper()].append(p)
    npc_matches = []
    for person in people:
        matches = npc_index[person['symbol']]
        ok = len(matches) == 1 and matches[0]['status'] == 'exact' and not any(matches[0]['issues'].values())
        npc_matches.append({**person, 'status': 'exact' if ok else 'review', 'candidates': matches})
    summary = {'name': config['name'], 'sources': sources, 'key': list(KEY),
               'statuses': dict(Counter(p['status'] for p in pairs)),
               'categories': dict(Counter(p['kind'] for p in pairs)),
               'ambiguous_name_groups': len(conflicts),
               'text_issues': {lang: dict(Counter(flag for p in pairs for flag in p['issues'].get(lang, []))) for lang in ('de', 'pl')},
               'duplicate_keys': {lang: { '+'.join(fields): sum(n>1 for n in Counter(key(r, fields) for r in rows[lang]).values())
                    for fields in [('ID',), CONTEXT, KEY]} for lang in ('de', 'pl')},
               'guide': {'sections': len(sections), 'quest_headings': len(quests),
                         'quest_statuses': dict(Counter(q['status'] for q in quests)),
                         'npc_references': len(people), 'npc_statuses': dict(Counter(n['status'] for n in npc_matches)),
                         'images': list(images)}}
    out.mkdir(parents=True, exist_ok=True)
    (out / 'images').mkdir(exist_ok=True)
    for name, data in images.items():
        (out / 'images' / name).write_bytes(data)
    (out / 'solucja.de.md').write_text(clean, encoding='utf-8')
    write_database(out / 'teksty.sqlite3', pairs, sections, sources, hashlib.sha256(config_path.read_bytes()).hexdigest())
    (out / 'raport.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    (out / 'mapowania-solucji.json').write_text(json.dumps({'quests': quests, 'people': npc_matches}, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    report = [f"# {config['name']} — raport importu", '',
              'Wygenerowano z eksportów tekstów. Zgodność kluczy nie potwierdza logiki gry ani zgodności wersji moda.', '',
              '| Źródło | Wpisy | Kolumna | SHA-256 |', '| --- | ---: | --- | --- |']
    for lang in ('de', 'pl'):
        s = sources[lang]
        report.append(f"| {Path(s['path']).name} | {s['records']} | {s['column']} | `{s['sha256']}` |")
    report += ['', 'Klucz: `ID + SYMBOL + USE + TRACE`. Dopasowanie `context_review` jest wyłącznie propozycją po jednoznacznym kontekście; ID są różne.', '',
               '## Połączenie tekstów', '', *[f'- {k}: **{v}**' for k, v in summary['statuses'].items()], '',
               '## Kategorie', '', *[f'- {k}: **{v}**' for k, v in summary['categories'].items()], '',
               '## Solucja', '', f"- Autor/data podane w źródle: {guide_spec.get('credit') or 'brak danych'}.",
               f"- Nagłówki zadań: **{len(quests)}**; zgodne nazwy: **{summary['guide']['quest_statuses'].get('exact', 0)}**; do sprawdzenia: **{summary['guide']['quest_statuses'].get('review', 0)}**.",
               f"- Odwołania do instancji NPC: **{len(people)}**; jednoznaczne: **{summary['guide']['npc_statuses'].get('exact', 0)}**.",
               f"- Obrazy wydzielone z base64: **{len(images)}**. Oryginał pozostał bez zmian.",
               '- [Mapowanie zadań](zadania.md) · [Mapowanie NPC](postacie.md) · [Solucja DE bez base64](solucja.de.md).', '',
               '## Teksty do sprawdzenia', '', 'Wykrywanie kodowania jest heurystyczne. Żaden tekst nie został automatycznie naprawiony.', '']
    for lang in ('de', 'pl'):
        report.append(f"- {lang.upper()}: `{json.dumps(summary['text_issues'][lang], ensure_ascii=False)}`")
    report += ['', 'Pełne dane, hashe, duplikaty kluczy i metadane: [raport.json](raport.json).',
               f"Identyczna nazwa DE z różnymi odpowiednikami PL: **{len(conflicts)}** grup. [Lista z instancjami](niejednoznaczne-nazwy.md). Różnice obejmują również wielkość liter.",
               'Wyszukiwanie `--issues` pokazuje podejrzane wpisy razem z kontekstem i źródłami.', '']
    (out / 'raport.md').write_text('\n'.join(report), encoding='utf-8')
    conflict_lines = ['# Jedna nazwa DE — różne nazwy PL', '',
                      'Nie zastępuj nazwy globalnie. Dobierz polski tekst po instancji i kontekście w solucji.', '',
                      '| Typ | DE | PL | Instancja | Źródło PL |', '| --- | --- | --- | --- | --- |']
    for group in conflicts:
        for p in group:
            conflict_lines.append('| '+' | '.join(cell(v) for v in [p['kind'], p['de']['text'], p['pl']['text'], p['symbol'], source_ref(p['pl'])])+' |')
    (out / 'niejednoznaczne-nazwy.md').write_text('\n'.join(conflict_lines)+'\n', encoding='utf-8')
    for filename, title, matches in [('zadania.md', 'Nagłówki zadań', quests), ('postacie.md', 'Postacie z solucji', npc_matches)]:
        table = [f'# {title} — DE → PL', '',
                 '`exact` oznacza zgodność nazwy nagłówka lub instancji NPC oraz jednoznaczne połączenie eksportów. `review` zawiera tylko propozycje; nie wolno traktować ich jako zatwierdzonych tłumaczeń.', '',
                 '| Wiersz solucji | Nazwa w solucji | Status | Polski odpowiednik / propozycje | Źródło PL |',
                 '| ---: | --- | --- | --- | --- |']
        for match in matches:
            section = match.get('section', {})
            candidates = match['candidates']
            names = '; '.join(f"{p['pl']['text'] if p['pl'] else 'BRAK PL'} [{p['symbol']}] (DE: {p['de']['text'] if p['de'] else '—'})" for p in candidates)
            refs = '; '.join(source_ref(p['pl']) for p in candidates)
            values = [section.get('start_line', match.get('line')), section.get('title', match.get('name')), match['status'], names or 'brak', refs or '—']
            table.append('| '+' | '.join(cell(v) for v in values)+' |')
        (out / filename).write_text('\n'.join(table)+'\n', encoding='utf-8')
    print(json.dumps({'output': str(out), 'statuses': summary['statuses'], 'guide': summary['guide'], 'text_issues': summary['text_issues']}, ensure_ascii=False, indent=2))
    return summary


def database(config_path):
    config_path = config_path.resolve()
    config = json.loads(config_path.read_text(encoding='utf-8-sig'))
    path = (config_path.parent / config['output'] / 'teksty.sqlite3').resolve()
    if not path.exists():
        raise ValueError(f'Brak indeksu {path}. Uruchom najpierw build.')
    db = sqlite3.connect(path.as_uri()+'?mode=ro', uri=True)
    metadata = json.loads(db.execute('SELECT data FROM metadata').fetchone()[0])
    if metadata['config_sha256'] != hashlib.sha256(config_path.read_bytes()).hexdigest():
        db.close()
        raise ValueError('Konfiguracja zmieniła się. Uruchom ponownie build.')
    sources = metadata['sources']
    for lang, source in sources.items():
        p = (config_path.parent / config[lang]['path']).resolve()
        if not p.exists() or hashlib.sha256(p.read_bytes()).hexdigest() != source['sha256']:
            db.close()
            raise ValueError(f'Źródło {p} zmieniło się lub jest niedostępne. Uruchom ponownie build.')
    return db


def search(db, query='', kind=None, symbol=None, language='both', issues=False, limit=10):
    where, params = [], []
    columns = {'de': 'search_de', 'pl': 'search_pl', 'both': "search_de || ' ' || search_pl || ' ' || search_key"}
    expression = columns[language]
    for token in normalize(query).split():
        where.append(f'instr({expression}, ?) > 0')
        params.append(token)
    for column, value in [('kind', kind), ('symbol', symbol.upper() if symbol else None)]:
        if value:
            where.append(f'{column} = ?')
            params.append(value)
    if issues:
        where.append('has_issues = 1')
    clause = ' AND '.join(where) or '1'
    total = db.execute(f'SELECT COUNT(*) FROM texts WHERE {clause}', params).fetchone()[0]
    sql = f'''SELECT data FROM texts WHERE {clause}
              ORDER BY (search_de = ? OR search_pl = ?) DESC,
                       CASE kind WHEN 'topic' THEN 0 WHEN 'npc' THEN 1 WHEN 'item' THEN 2 ELSE 3 END, number
              LIMIT ?'''
    records = [json.loads(row[0]) for row in db.execute(sql, [*params, normalize(query), normalize(query), limit])]
    return {'total': total, 'shown': len(records), 'records': records}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=DEFAULT_CONFIG, help='JSON moda; ścieżki w nim są względne do tego pliku')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('build', help='połącz eksporty i przygotuj indeks oraz raporty')
    lookup = commands.add_parser('search', help='wyszukaj DE/PL, instancje i identyfikatory')
    lookup.add_argument('query', nargs='?', default='')
    lookup.add_argument('--kind', choices=KINDS)
    lookup.add_argument('--symbol')
    lookup.add_argument('--language', choices=('de', 'pl', 'both'), default='both')
    lookup.add_argument('--issues', action='store_true')
    lookup.add_argument('--limit', type=int, default=10)
    lookup.add_argument('--json', action='store_true', help='pełne teksty i metadane w JSON')
    section = commands.add_parser('section', help='pobierz niemiecki fragment solucji po tytule lub numerze sekcji')
    section.add_argument('query')
    section.add_argument('--limit', type=int, default=3)
    args = parser.parse_args(argv)
    if getattr(args, 'limit', 1) <= 0:
        parser.error('--limit musi być dodatni')
    try:
        if args.command == 'build':
            build(args.config)
            return
        db = database(args.config)
        try:
            if args.command == 'search':
                result = search(db, args.query, args.kind, args.symbol, args.language, args.issues, args.limit)
                if args.json:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                else:
                    print(f"Wyniki: {result['shown']} z {result['total']}. Pełne teksty i metadane: --json.")
                    for p in result['records']:
                        print(f"\n[{p['number']}] {p['kind']} / {p['status']} / {p['symbol']} / ID {p['id']}")
                        for lang in ('de', 'pl'):
                            r = p[lang]
                            text = r['text'] if r else 'BRAK ODPOWIEDNIKA'
                            print(f"{lang.upper()}: {text[:500]}{'…' if len(text)>500 else ''}\n    {source_ref(r)}")
                        if any(p['issues'].values()):
                            print('Do sprawdzenia:', json.dumps(p['issues'], ensure_ascii=False))
            else:
                if args.query.isdecimal():
                    found = db.execute('SELECT data FROM sections WHERE number = ?', (int(args.query),)).fetchall()
                else:
                    found = db.execute('SELECT data FROM sections WHERE instr(search_title, ?) > 0 ORDER BY number LIMIT ?', (normalize(args.query), args.limit)).fetchall()
                print(f'Sekcje: {len(found)} (limit {args.limit}). Obrazy: katalog wyników/images/.')
                for row in found:
                    s = json.loads(row[0])
                    print(f"\n[sekcja {s['number']}; wiersze {s['start_line']}–{s['end_line']}]\n{s['text']}")
        finally:
            db.close()
    except (ValueError, OSError, csv.Error, sqlite3.Error) as exc:
        parser.exit(1, f'Błąd: {exc}\n')


if __name__ == '__main__':
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    main()
