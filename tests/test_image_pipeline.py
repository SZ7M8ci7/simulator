import io
import os
from contextlib import redirect_stdout
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import requests
from PIL import Image

from get_img import acquire, main as download_main
from image_pipeline import Downloader, ImageFailure, filename_for, image_info, safe_child
from make_icon import generate, main as generate_main


def picture(fmt='JPEG', size=(80, 80), color='red'):
    output = io.BytesIO()
    Image.new('RGB', size, color).save(output, fmt)
    return output.getvalue()


def card(name='one'):
    return dict(name=name, chara=name, costume='衣装', rare='SSR',
                magic1atr='火', magic2atr='水', magic3atr='木')


class Response:
    def __init__(self, status=200, raw=None, content_type='image/jpeg', headers=None):
        self.status_code = status
        self.raw = picture() if raw is None else raw
        self.headers = {'Content-Type': content_type, **(headers or {})}
        self.closed = False

    def iter_content(self, _):
        yield self.raw

    def close(self):
        self.closed = True


class Session:
    def __init__(self, *responses):
        self.responses = list(responses)
        self.calls = 0

    def get(self, *args, **kwargs):
        self.calls += 1
        response = self.responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class PipelineTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'get').mkdir()
        for attribute in ('火', '水', '木', '無'):
            (self.root / (attribute + '.png')).write_bytes(picture('PNG', (12, 12)))

    def downloader(self, *responses, attempts=3):
        self.session = Session(*responses)
        self.sleeps = []
        return Downloader(self.session, sleep=self.sleeps.append, clock=lambda: 0, attempts=attempts)

    def test_html_200_not_saved_and_next_card_processed(self):
        client = self.downloader(Response(raw=b'<html>challenge</html>', content_type='text/html'),
                                 Response(), attempts=1)
        results = acquire([card('bad'), card('good')], self.root, client)
        self.assertEqual([r['status'] for r in results], ['error', 'downloaded'])
        self.assertFalse((self.root / 'get' / filename_for(card('bad'))).exists())
        image_info((self.root / 'get' / filename_for(card('good'))).read_bytes())

    def test_html_with_image_content_type_is_rejected(self):
        with self.assertRaises(ImageFailure):
            self.downloader(Response(raw=b'<html>challenge</html>'), attempts=1).fetch('url')

    def test_corrupt_existing_image_is_repaired(self):
        path = self.root / 'get' / filename_for(card())
        path.write_bytes(b'<html>old challenge</html>')
        result = acquire([card()], self.root, self.downloader(Response()))[0]
        self.assertEqual(result['status'], 'repaired')
        image_info(path.read_bytes())

    def test_failed_repair_preserves_existing_bytes(self):
        path = self.root / 'get' / filename_for(card())
        path.write_bytes(b'old')
        result = acquire([card()], self.root, self.downloader(Response(404)))[0]
        self.assertEqual(result['status'], 'error')
        self.assertEqual(path.read_bytes(), b'old')

    def test_404_does_not_retry_or_block_later_cards(self):
        client = self.downloader(Response(404), Response(), Response())
        results = acquire([card('missing'), card('two'), card('three')], self.root, client)
        self.assertEqual([r['status'] for r in results], ['pending', 'downloaded', 'downloaded'])
        self.assertEqual(self.session.calls, 3)

    def test_existing_valid_image_skips_network(self):
        (self.root / 'get' / filename_for(card())).write_bytes(picture())
        self.assertEqual(acquire([card()], self.root, self.downloader())[0]['status'], 'valid')
        self.assertEqual(self.session.calls, 0)

    def test_timeout_and_503_retry_with_backoff(self):
        client = self.downloader(requests.Timeout('timeout'), Response(503), Response())
        _, attempts = client.fetch('url')
        self.assertEqual(attempts, 3)
        self.assertIn(2, self.sleeps)
        self.assertIn(4, self.sleeps)

    def test_challenge_retries_without_caching(self):
        client = self.downloader(Response(content_type='text/html'), Response())
        self.assertEqual(client.fetch('url')[1], 2)

    def test_403_is_not_bypassed(self):
        with self.assertRaisesRegex(ImageFailure, 'HTTP 403'):
            self.downloader(Response(403)).fetch('url')
        self.assertEqual(self.session.calls, 1)

    def test_retry_limit_closes_every_response(self):
        responses = [Response(503) for _ in range(3)]
        with self.assertRaises(ImageFailure) as caught:
            self.downloader(*responses).fetch('url')
        self.assertEqual(caught.exception.attempts, 3)
        self.assertTrue(all(r.closed for r in responses))

    def test_retry_after_is_respected(self):
        client = self.downloader(Response(429, headers={'Retry-After': '9'}), Response())
        client.fetch('url')
        self.assertIn(9, self.sleeps)

    def test_long_retry_after_defers_later_network_requests(self):
        client = self.downloader(Response(429, headers={'Retry-After': '300'}))
        results = acquire([card('one'), card('two')], self.root, client)
        self.assertEqual(self.session.calls, 1)
        self.assertEqual(results[1]['status'], 'error')
        self.assertIn('Deferred', results[1]['error'])

    def test_rate_spacing_applies_between_cards(self):
        client = self.downloader(Response(), Response())
        acquire([card('one'), card('two')], self.root, client)
        self.assertIn(1.0, self.sleeps)

    def test_truncated_jpeg_is_rejected(self):
        with self.assertRaises(ImageFailure):
            image_info(picture()[:-20])

    def test_oversized_download_is_rejected(self):
        with patch('image_pipeline.MAX_BYTES', 20):
            with self.assertRaisesRegex(ImageFailure, 'size limit'):
                self.downloader(Response()).fetch('url')
        self.assertEqual(self.session.calls, 1)

    def test_retry_after_is_kept_when_retry_budget_is_exhausted(self):
        client = self.downloader(Response(429, headers={'Retry-After': '9'}), Response(), attempts=1)
        results = acquire([card('one'), card('two')], self.root, client)
        self.assertEqual(results[1]['status'], 'downloaded')
        self.assertIn(9, self.sleeps)

    def test_reviewed_source_filename_changes_url_but_keeps_canonical_storage(self):
        from image_pipeline import url_for
        c = card()
        source = 'SSRone【旧衣装】アイコン.JPG'
        results = acquire([c], self.root, self.downloader(Response()), {'one': source})
        self.assertEqual(results[0]['url'], url_for(c, source))
        self.assertTrue(results[0]['url'].endswith('.JPG'))
        self.assertTrue((self.root / 'get' / filename_for(c)).exists())

    def test_source_overrides_cannot_be_urls_or_paths(self):
        from image_pipeline import url_for
        for bad in ['https://other.example/image.jpg', '../image.jpg', 'bad.txt']:
            with self.assertRaises(ImageFailure):
                url_for(card(), bad)

    def test_checked_in_source_overrides_preserve_card_identity(self):
        root = Path(__file__).parents[1]
        sources = json.loads((root / 'image_sources.json').read_text(encoding='utf8'))
        cards = {c['name']: c for c in json.loads((root / 'chara.json').read_text(encoding='utf8'))}
        costumes = dict(line.split(':', 1) for line in (root / 'cosdict.txt').read_text(encoding='utf8').splitlines() if ':' in line)
        for name, source in sources.items():
            c = cards[name]
            self.assertTrue(source.startswith(c['rare'] + c['chara'] + '【'))
            costume = source.split('【')[1].split('】')[0]
            self.assertEqual(costumes[costume], costumes[c['costume']])

    def test_safe_paths(self):
        with self.assertRaises(ImageFailure):
            safe_child(self.root / 'img', '../outside.png')

    def test_converter_continues_after_corrupt_source(self):
        (self.root / 'get' / filename_for(card('bad'))).write_bytes(b'html')
        (self.root / 'get' / filename_for(card('good'))).write_bytes(picture())
        results = generate([card('bad'), card('good')], self.root)
        self.assertEqual([r['status'] for r in results], ['error', 'generated'])
        self.assertEqual(image_info((self.root / 'img/good.webp').read_bytes()), ('WEBP', (80, 80)))
        self.assertEqual(image_info((self.root / 'img/good.png').read_bytes()), ('PNG', (60, 60)))

    def test_invalid_generated_icon_is_repaired(self):
        (self.root / 'get' / filename_for(card())).write_bytes(picture())
        generate([card()], self.root)
        (self.root / 'img/one.webp').write_bytes(b'broken')
        self.assertEqual(generate([card()], self.root)[0]['status'], 'generated')
        image_info((self.root / 'img/one.webp').read_bytes(), 'WEBP')

    def test_invalid_attribute_fails_without_partial_output(self):
        c = card()
        c['magic3atr'] = ''
        (self.root / 'get' / filename_for(c)).write_bytes(picture())
        self.assertEqual(generate([c], self.root)[0]['status'], 'error')
        self.assertFalse((self.root / 'img/one.png').exists())

    def test_valid_outputs_are_untouched(self):
        (self.root / 'get' / filename_for(card())).write_bytes(picture())
        generate([card()], self.root)
        before = (self.root / 'img/one.webp').stat().st_mtime_ns
        self.assertEqual(generate([card()], self.root)[0]['status'], 'valid')
        self.assertEqual((self.root / 'img/one.webp').stat().st_mtime_ns, before)

    def test_repaired_source_refreshes_existing_outputs(self):
        path = self.root / 'get' / filename_for(card())
        path.write_bytes(picture())
        generate([card()], self.root)
        before = (self.root / 'img/one.webp').read_bytes()
        path.write_bytes(picture(color='blue'))
        generate([card()], self.root, {'one'})
        self.assertNotEqual((self.root / 'img/one.webp').read_bytes(), before)

    def test_cli_pending_only_returns_zero_and_does_not_notify(self):
        (self.root / 'chara.json').write_text(json.dumps([card()]), encoding='utf8')
        summary = self.root / 'summary.md'
        output = io.StringIO()
        with patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': str(summary)}), redirect_stdout(output):
            with patch('get_img.Downloader', return_value=self.downloader(Response(404))):
                self.assertEqual(download_main(['--root', str(self.root)]), 0)
            self.assertEqual(generate_main(['--root', str(self.root)]), 0)
        self.assertFalse(summary.exists())
        self.assertNotIn('one', output.getvalue())
        self.assertNotIn('warning', output.getvalue().lower())
        self.assertNotIn('error', output.getvalue().lower())
        for filename in ['get-images.json', 'make-icons.json']:
            report = json.loads((self.root / 'reports' / filename).read_text(encoding='utf8'))
            self.assertEqual(report['failedCount'], 0)
            self.assertEqual(report['pendingCount'], 1)
            self.assertEqual(report['results'][0]['status'], 'pending')

    def test_mixed_pending_corruption_and_success_preserve_updates_and_report_only_error(self):
        cards = [card('waiting'), card('broken'), card('ready')]
        (self.root / 'chara.json').write_text(json.dumps(cards), encoding='utf8')
        summary = self.root / 'summary.md'
        client = self.downloader(Response(404), Response(raw=b'<html>challenge</html>'), Response(), attempts=1)
        with patch.dict(os.environ, {'GITHUB_STEP_SUMMARY': str(summary)}), redirect_stdout(io.StringIO()):
            with patch('get_img.Downloader', return_value=client):
                self.assertEqual(download_main(['--root', str(self.root)]), 1)
            self.assertEqual(generate_main(['--root', str(self.root)]), 1)
        for filename in ['get-images.json', 'make-icons.json']:
            report = json.loads((self.root / 'reports' / filename).read_text(encoding='utf8'))
            self.assertEqual(report['failedCount'], 1)
            self.assertEqual(report['pendingCount'], 1)
            self.assertEqual([r['status'] for r in report['results'][:2]], ['pending', 'error'])
        image_info((self.root / 'img/ready.webp').read_bytes(), 'WEBP')
        notice = summary.read_text(encoding='utf8')
        self.assertIn('broken', notice)
        self.assertNotIn('waiting', notice)

    def test_pending_image_is_acquired_on_the_next_run(self):
        client = self.downloader(Response(404), Response())
        self.assertEqual(acquire([card()], self.root, client)[0]['status'], 'pending')
        self.assertEqual(acquire([card()], self.root, client)[0]['status'], 'downloaded')
        self.assertEqual(generate([card()], self.root)[0]['status'], 'generated')

    def test_html_followed_by_404_is_not_downgraded_to_pending(self):
        result = acquire([card()], self.root, self.downloader(Response(content_type='text/html'), Response(404)))[0]
        self.assertEqual(result['status'], 'error')
        self.assertIn('abnormal response', result['error'])

    def test_auth_rate_limit_and_transport_errors_are_not_pending(self):
        for response in [Response(401), Response(403), Response(429), requests.Timeout('timeout')]:
            result = acquire([card()], self.root, self.downloader(response, attempts=1))[0]
            self.assertEqual(result['status'], 'error')

    def test_missing_source_with_corrupt_existing_output_is_error(self):
        (self.root / 'img').mkdir()
        (self.root / 'img/one.webp').write_bytes(b'<html>bad cached output</html>')
        self.assertEqual(generate([card()], self.root)[0]['status'], 'error')

    def test_missing_source_with_valid_outputs_is_pending(self):
        (self.root / 'img').mkdir()
        (self.root / 'img/one.webp').write_bytes(picture('WEBP', (80, 80)))
        (self.root / 'img/one.png').write_bytes(picture('PNG', (60, 60)))
        self.assertEqual(generate([card()], self.root)[0]['status'], 'pending')

    def test_missing_render_dependency_is_error_not_pending(self):
        (self.root / 'get' / filename_for(card())).write_bytes(picture())
        (self.root / '火.png').unlink()
        self.assertEqual(generate([card()], self.root)[0]['status'], 'error')

    def test_upstream_download_error_is_preserved_by_generation(self):
        result = generate([card()], self.root, source_errors={'one': 'HTTP 403'})[0]
        self.assertEqual(result['status'], 'error')
        self.assertIn('HTTP 403', result['error'])


if __name__ == '__main__':
    unittest.main()
