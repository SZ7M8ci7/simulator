"""Validation, bounded downloads and reporting shared by the icon jobs."""
import io
import json
import os
import tempfile
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import requests
from PIL import Image

MAX_BYTES = 10 * 1024 * 1024
ORIGIN = 'https://twst.wikiru.jp/'


class ImageFailure(ValueError):
    def __init__(self, message, attempts=0):
        super().__init__(message)
        self.attempts = attempts


def image_info(raw, expected_format=None):
    if not raw or len(raw) > MAX_BYTES:
        raise ImageFailure('Empty or oversized image')
    try:
        with Image.open(io.BytesIO(raw)) as image:
            fmt, size = image.format, image.size
            if fmt not in {'JPEG', 'PNG', 'WEBP'}:
                raise ImageFailure('Unsupported image format: ' + str(fmt))
            if expected_format and fmt != expected_format:
                raise ImageFailure('Expected ' + expected_format + ', got ' + fmt)
            if min(size) < 16 or max(size) > 4096:
                raise ImageFailure('Unexpected image dimensions: ' + str(size))
            image.verify()
        # verify() alone does not detect every truncated JPEG.
        with Image.open(io.BytesIO(raw)) as image:
            image.load()
        return fmt, size
    except ImageFailure:
        raise
    except Exception as error:
        raise ImageFailure('Image decode failed: ' + str(error)) from error


def filename_for(card):
    return '{}{}【{}】アイコン.jpg'.format(card['rare'], card['chara'], card['costume'])


def url_for(card, source_filename=None):
    filename = source_filename or filename_for(card)
    # Overrides are exact, reviewed attachment filenames, never arbitrary URLs.
    if '/' in filename or '\\' in filename or '..' in filename:
        raise ImageFailure('Unsafe source filename')
    extension = filename.rsplit('.', 1)[-1]
    if extension not in {'jpg', 'JPG', 'png', 'PNG', 'webp'}:
        raise ImageFailure('Unsupported source extension')
    return ORIGIN + 'attach2/696D67_' + filename.encode('utf-8').hex().upper() + '.' + extension


def safe_child(folder, name):
    folder = Path(folder).resolve()
    path = (folder / name).resolve()
    if path.parent != folder:
        raise ImageFailure('Unsafe image filename')
    return path


def atomic_write(path, raw):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as stream:
            tmp = Path(stream.name)
            stream.write(raw)
        os.replace(tmp, path)
    finally:
        if tmp is not None and tmp.exists():
            tmp.unlink()


class Downloader:
    """Sequential requests; no challenge solving or alternate identity tricks."""
    def __init__(self, session=None, interval=1.0, attempts=3,
                 sleep=time.sleep, clock=time.monotonic):
        if interval < 0 or attempts < 1:
            raise ValueError('Invalid request interval or retry count')
        self.session = session or requests.Session()
        self.interval, self.attempts = interval, attempts
        self.sleep, self.clock = sleep, clock
        self.last_request = None
        self.blocked = False
        self.retry_until = 0

    def fetch(self, url):
        if self.blocked:
            raise ImageFailure('Deferred: server requested a long Retry-After; retry next run')
        for attempt in range(1, self.attempts + 1):
            if self.last_request is not None:
                self.sleep(max(0, self.interval - (self.clock() - self.last_request), self.retry_until - self.clock()))
            self.last_request = self.clock()
            delay = min(2 ** attempt, 30)
            retry = True
            response = None
            try:
                response = self.session.get(url, timeout=(10, 30), stream=True)
                status = response.status_code
                if status != 200:
                    retry = status in {408, 429, 500, 502, 503, 504}
                    if status in {429, 503}:
                        value = response.headers.get('Retry-After', '')
                        if value:
                            try:
                                wait = float(value)
                            except ValueError:
                                try:
                                    wait = (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
                                except (ValueError, TypeError):
                                    wait = 0
                            if wait > 30:
                                self.blocked = True
                                retry = False
                            self.retry_until = self.clock() + min(max(wait, 0), 30)
                            delay = max(delay, min(max(wait, 0), 30))
                    raise ImageFailure('HTTP ' + str(status))
                content_type = response.headers.get('Content-Type', '').split(';')[0].lower()
                if content_type.startswith('text/') or content_type in {'application/json', 'application/xhtml+xml'}:
                    raise ImageFailure('Non-image response: ' + content_type + ' (possible HTML challenge)')
                chunks, length = [], 0
                for chunk in response.iter_content(65536):
                    length += len(chunk)
                    if length > MAX_BYTES:
                        retry = False
                        raise ImageFailure('Image exceeds download size limit')
                    chunks.append(chunk)
                raw = b''.join(chunks)
                image_info(raw)
                return raw, attempt
            except (requests.RequestException, ImageFailure) as error:
                message = str(error)
                if not retry or attempt == self.attempts:
                    raise ImageFailure(message, attempt) from error
            finally:
                if response is not None:
                    response.close()
            self.sleep(delay)


def write_report(path, stage, results):
    failures = [r for r in results if r['status'] == 'error']
    report = {'stage': stage, 'checkedAt': datetime.now(timezone.utc).isoformat(),
              'cardCount': len(results), 'failedCount': len(failures), 'results': results}
    atomic_write(path, (json.dumps(report, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
    summary = '{}: {} cards checked; {} unresolved\n'.format(stage, len(results), len(failures))
    print(summary.strip())
    details = ''.join('- `{}`: {}\n'.format(r['name'], r['error'].replace('\n', ' ')) for r in failures)
    print(details, end='')
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a', encoding='utf-8') as stream:
            stream.write('### ' + summary + '\n' + details + '\n')
    return report
