"""Acquire every missing/invalid card icon; never cache an HTML response."""
import argparse
import json
from pathlib import Path

from image_pipeline import (Downloader, ImagePending, atomic_write, filename_for, image_info,
                            safe_child, url_for, write_report)


def acquire(cards, root, downloader, source_filenames=None):
    results = []
    for card in cards:
        result = {'name': card['name']}
        invalid = False
        try:
            result['url'] = url_for(card, (source_filenames or {}).get(card['name']))
            path = safe_child(Path(root) / 'get', filename_for(card))
            if path.exists():
                try:
                    image_info(path.read_bytes())
                    result['status'] = 'valid'
                    results.append(result)
                    continue
                except ValueError as error:
                    invalid = True
                    result['previousError'] = str(error)
            raw, attempts = downloader.fetch(result['url'])
            image_info(raw)
            atomic_write(path, raw)
            result.update(status='repaired' if invalid else 'downloaded', attempts=attempts)
        except ImagePending as error:
            if invalid:
                result.update(status='error', error='Corrupt cached source could not be repaired: ' + str(error), attempts=error.attempts)
            else:
                result.update(status='pending', reason=str(error), attempts=error.attempts)
        except Exception as error:
            result.update(status='error', error=str(error), attempts=getattr(error, 'attempts', 0))
        results.append(result)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    parser.add_argument('--interval', type=float, default=1.0)
    parser.add_argument('--attempts', type=int, default=3)
    args = parser.parse_args(argv)
    cards = json.loads((args.root / 'chara.json').read_text(encoding='utf-8'))
    overrides_path = args.root / 'image_sources.json'
    sources = json.loads(overrides_path.read_text(encoding='utf-8')) if overrides_path.exists() else {}
    results = acquire(cards, args.root, Downloader(interval=args.interval, attempts=args.attempts), sources)
    report = write_report(args.root / 'reports/get-images.json', 'Download card images', results)
    return 1 if report['failedCount'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
