import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import DEFAULT, Mock, patch

import main


class CardIdTests(unittest.TestCase):
    def test_existing_ids_survive_reordering_and_insertions(self):
        previous = [{'name': 'a', 'id': '0'}, {'name': 'b', 'id': '9'}]
        incoming = [
            {'name': 'new-first', 'id': '0'},
            {'name': 'b', 'id': '1', 'atk': 5},
            {'name': 'new-middle', 'id': '2'},
            {'name': 'a', 'id': '3'},
        ]
        actual = main.preserve_card_ids(previous, incoming)
        self.assertEqual([item['id'] for item in actual], ['10', '9', '11', '0'])
        self.assertEqual(actual[1]['atk'], 5)
        self.assertEqual(incoming[1]['id'], '1')
        self.assertEqual(main.preserve_card_ids(actual, incoming), actual)

    def test_first_run_uses_zero_and_allocates_unique_ids(self):
        actual = main.preserve_card_ids([], [{'name': 'a'}, {'name': 'b'}])
        self.assertEqual([item['id'] for item in actual], ['0', '1'])

    def test_rejects_ambiguous_or_missing_card_identities(self):
        a = {'name': 'a', 'id': '0'}
        b = {'name': 'b', 'id': '1'}
        for prior, scraped, message in [
            ([a, {**b, 'id': '0'}], [a, b], 'duplicate existing ID'),
            ([a, {**a, 'id': '1'}], [a, b], 'duplicate existing card name'),
            ([{**a, 'id': 'bad'}], [a], 'Invalid or duplicate existing ID'),
            ([a], [a, a], 'duplicate scraped card name'),
            ([a], [{}], 'Missing or duplicate scraped card name'),
            ([a, b], [a, {'name': 'new'}], 'Missing existing cards'),
        ]:
            with self.subTest(prior=prior, scraped=scraped), self.assertRaisesRegex(ValueError, message):
                main.preserve_card_ids(prior, scraped)

    def test_full_update_writes_published_ids_and_leaves_file_on_missing_card(self):
        previous = [{'name': 'a', 'id': '241'}, {'name': 'b', 'id': '536'}]
        with tempfile.TemporaryDirectory() as tmp:
            with patch.multiple(
                main, fetch_card_titles_by_rank=Mock(), make_type_dict=DEFAULT,
                getDict=DEFAULT, get_implementation_dates=DEFAULT,
                download_missing_icons=DEFAULT, scrape_card=DEFAULT,
                build_card_record=DEFAULT, outDict=DEFAULT,
                makeicon=DEFAULT,
            ) as mocks, patch.object(main.time, 'sleep'):
                Path(tmp, 'chara.json').write_text(json.dumps(previous), encoding='utf-8')
                cwd = os.getcwd()
                try:
                    os.chdir(tmp)
                    main.fetch_card_titles_by_rank.return_value = {'SSR': ['new', 'b', 'a'], 'SR': [], 'R': []}
                    mocks['build_card_record'].side_effect = [{'name': name} for name in ('new', 'b', 'a')]
                    main.run_full_update()
                    self.assertEqual([(c['name'], c['id']) for c in main.load_chara_json()],
                                     [('new', '537'), ('b', '536'), ('a', '241')])
                    before = Path('chara.json').read_bytes()
                    mocks['build_card_record'].side_effect = [{'name': name} for name in ('new', 'b', 'replacement')]
                    with self.assertRaisesRegex(ValueError, 'Missing existing cards'):
                        main.run_full_update()
                    self.assertEqual(Path('chara.json').read_bytes(), before)
                finally:
                    os.chdir(cwd)


if __name__ == '__main__':
    unittest.main()
