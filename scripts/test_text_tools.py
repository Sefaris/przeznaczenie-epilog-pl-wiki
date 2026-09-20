"""Regression tests for joins, source preservation and guide indexing; no real exports needed."""
import contextlib
import csv
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from text_tools import align, build, database, guide_matches, heading_name, name_conflicts, normalize, prepare_guide, read_export, search


def row(text, symbol='TOPIC_TEST', ident='1', use='LOG_CREATETOPIC.PAR0', line=2):
    return {'text': text, 'source': {'file': 'source.csv', 'line': line, 'line_end': line,
            'column': 'TEXT', 'NR': str(line-1), 'FILENR': '83', 'ID': ident,
            'SYMBOL': symbol, 'USE': use, 'TRACE': use}}


def export(path, rows, lang='DE', encoding='utf-8-sig'):
    with path.open('w', encoding=encoding, newline='') as stream:
        writer = csv.writer(stream, delimiter='\t')
        writer.writerow(['NR', 'FILENR', 'ID', 'SYMBOL', 'USE', 'TRACE', lang, 'BACKUP'])
        for i, r in enumerate(rows, 1):
            s = r['source']
            writer.writerow([i, s['FILENR'], s['ID'], s['SYMBOL'], s['USE'], s['TRACE'], r['text'], 'Nie używaj kopii'])


class ExportTests(unittest.TestCase):
    def test_multiline_quotes_tabs_and_source_coordinates(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.csv'
            texts = ['Zażółć "gęślą"\tjaźń\nDrugi wiersz', 'Następny wpis']
            export(path, [row(t) for t in texts], 'PL')
            records, metadata = read_export(path, 'PL')
            self.assertEqual([r['text'] for r in records], texts)
            self.assertEqual(records[0]['source']['line'], 2)
            self.assertEqual(records[0]['source']['line_end'], 3)
            self.assertEqual(records[1]['source']['line'], 4)
            self.assertEqual(metadata['records'], 2)

    def test_utf16_bom_and_explicit_legacy_encoding(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.csv'
            for encoding in ['utf-16', 'cp1250']:
                export(path, [row('Zbłąkane dusze')], 'PL', encoding)
                rows, _ = read_export(path, 'PL', encoding=None if encoding == 'utf-16' else encoding)
                self.assertEqual(rows[0]['text'], 'Zbłąkane dusze')

    def test_invalid_exports_fail_instead_of_losing_fields(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / 'input.csv'
            export(path, [row('Text')])
            valid = path.read_text(encoding='utf-8-sig')
            for bad in ['', valid.replace('DE\tBACKUP', 'DE\tDE'), valid+'one\tfield\n']:
                path.write_text(bad, encoding='utf-8')
                with self.assertRaises(ValueError):
                    read_export(path, 'DE')


class AlignmentTests(unittest.TestCase):
    def test_reordering_and_repeated_numeric_id_do_not_mix_texts(self):
        de = [row('First', use='USE_ONE'), row('Second', use='USE_TWO')]
        pl = [row('Drugi', use='USE_TWO'), row('Pierwszy', use='USE_ONE')]
        pairs = align(de, pl)
        self.assertEqual([(p['de']['text'], p['pl']['text']) for p in pairs], [('First', 'Pierwszy'), ('Second', 'Drugi')])
        self.assertEqual([p['status'] for p in pairs], ['exact', 'exact'])

    def test_different_id_is_only_a_review_candidate(self):
        pair, = align([row('First', ident='1')], [row('Pierwszy', ident='999')])
        self.assertEqual(pair['status'], 'context_review')

    def test_duplicate_keys_remain_unpaired_and_all_records_survive(self):
        pairs = align([row('First'), row('Another')], [row('Pierwszy')])
        self.assertEqual(len(pairs), 3)
        self.assertTrue(all(p['status'] == 'ambiguous' for p in pairs))
        self.assertTrue(all(not (p['de'] and p['pl']) for p in pairs))

    def test_missing_counterpart_and_suspect_text_are_visible(self):
        pairs = align([row('Alone', symbol='TOPIC_ALONE')], [row('Zb³¹kane', symbol='TOPIC_OTHER')])
        self.assertEqual([p['status'] for p in pairs], ['de_only', 'pl_only'])
        self.assertIn('suspected_encoding', pairs[1]['issues']['pl'])
        self.assertEqual(pairs[1]['pl']['text'], 'Zb³¹kane')

    def test_same_german_name_does_not_collapse_distinct_items(self):
        de = [row('Kurzschwert', symbol=s, use='C_ITEM.NAME') for s in ['ITMW_A', 'ITMW_B']]
        pl = [row(t, symbol=s, use='C_ITEM.NAME') for t, s in [('Krótki miecz', 'ITMW_A'), ('Gladius', 'ITMW_B')]]
        group, = name_conflicts(align(de, pl))
        self.assertEqual({p['pl']['text'] for p in group}, {'Krótki miecz', 'Gladius'})


class GuideTests(unittest.TestCase):
    def test_images_are_extracted_without_moving_source_lines(self):
        text = '# Quests\n### Test {#test}\n![Mapa][image1]\n\n[image1]: <data:image/png;base64,aGVsbG8=>\n'
        clean, images, sections, _ = prepare_guide(text)
        self.assertEqual(images, {'image-1.png': b'hello'})
        self.assertNotIn('base64', clean)
        self.assertEqual(len(text.splitlines()), len(clean.splitlines()))
        self.assertEqual(sections[1]['start_line'], 2)
        self.assertEqual(sections[1]['end_line'], 5)

    def test_npc_identifiers_and_title_annotations(self):
        _, _, _, people = prepare_guide('| Alter Mann | hier | none\\_8893\\_starec |\n')
        self.assertEqual(people[0]['symbol'], 'NONE_8893_STAREC')
        self.assertEqual(heading_name('Abschied (beendet die Mod) {#bye}'), 'Abschied')
        self.assertEqual(heading_name('Titel (Teil II)'), 'Titel (Teil II)')
        _, _, _, orcs = prepare_guide('| Ghar-Pak | Lager | orkelite\\_antipaladinorkoberst |\n')
        self.assertEqual(orcs[0]['symbol'], 'ORKELITE_ANTIPALADINORKOBERST')

    def test_fuzzy_quest_titles_are_never_automatically_confirmed(self):
        pairs = align([row('Der Schlüssel zur Wahrheit')], [row('Klucz do prawdy')])
        _, _, sections, _ = prepare_guide('# Quests\n### Der Schlüssel der Wahrheit\n')
        match, = guide_matches(sections, pairs)
        self.assertEqual(match['status'], 'review')
        self.assertEqual(match['candidates'][0]['pl']['text'], 'Klucz do prawdy')

    def test_exact_heading_does_not_approve_changed_script_ids(self):
        pairs = align([row('Test', ident='1')], [row('Test PL', ident='2')])
        _, _, sections, _ = prepare_guide('# Quests\n### Test\n')
        self.assertEqual(guide_matches(sections, pairs)[0]['status'], 'review')


class IntegrationTests(unittest.TestCase):
    def test_build_search_repeat_build_and_stale_sources(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            export(root/'de.csv', [row('Verirrte Seelen')], 'DE')
            export(root/'pl.csv', [row('Zbłąkane dusze')], 'PL')
            (root/'guide.md').write_text('# Quests\n### Verirrte Seelen\nBeschreibung\n', encoding='utf-8')
            config = {'name': 'Test', 'de': {'path': 'de.csv', 'column': 'DE'},
                      'pl': {'path': 'pl.csv', 'column': 'PL'}, 'guide': {'path': 'guide.md'}, 'output': 'output'}
            config_path = root/'config.json'
            config_path.write_text(json.dumps(config), encoding='utf-8')
            hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*') if p.is_file()}
            with contextlib.redirect_stdout(io.StringIO()):
                build(config_path)
                build(config_path)  # Windows-safe replacement of an existing index.
            db = database(config_path)
            try:
                result = search(db, 'zblakane', kind='topic')
                self.assertEqual(result['total'], 1)
                self.assertEqual(result['records'][0]['de']['text'], 'Verirrte Seelen')
                self.assertEqual(search(db, 'not-there')['total'], 0)
                self.assertEqual(search(db, 'x\' OR 1=1 --')['total'], 0)
            finally:
                db.close()
            self.assertEqual(hashes, {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in root.glob('*') if p.is_file()})
            config_path.write_text(json.dumps(config)+'\n', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'Konfiguracja'):
                database(config_path)
            config_path.write_text(json.dumps(config), encoding='utf-8')
            (root/'pl.csv').write_text('changed', encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'zmieniło'):
                database(config_path)

    def test_search_normalization_keeps_original_display_available(self):
        self.assertEqual(normalize('ZAŻÓŁĆ Łódź Straße'), 'zazolc lodz strasse')


if __name__ == '__main__':
    unittest.main()
