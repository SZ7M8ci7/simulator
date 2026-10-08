"""Generate verified card icons and fail visibly on unresolved cards."""
import argparse
import io
import json
from pathlib import Path

from PIL import Image

from image_pipeline import atomic_write, filename_for, image_info, safe_child, write_report


def render_icon(card, raw, root, size):
    image_info(raw)
    with Image.open(io.BytesIO(raw)) as source:
        background = source.convert('RGBA').resize((size, size))
    count = 3 if card['rare'] == 'SSR' else 2
    magic_size = 16 if size == 80 else 12
    start = size - count * magic_size - (count - 1)
    for index in range(count):
        attribute = card['magic{}atr'.format(index + 1)]
        if attribute not in {'火', '水', '木', '無'}:
            raise ValueError('Missing/invalid magic attribute: ' + attribute)
        with Image.open(Path(root) / (attribute + '.png')) as source:
            overlay = source.convert('RGBA')
        if overlay.size != (magic_size, magic_size):
            overlay = overlay.resize((16, 18) if size == 80 else (magic_size, magic_size))
        background.alpha_composite(overlay, (start + (magic_size + 1) * index, 0))
    output = io.BytesIO()
    fmt = 'WEBP' if size == 80 else 'PNG'
    background.save(output, fmt, **({'quality': 85} if fmt == 'WEBP' else {}))
    raw = output.getvalue()
    image_info(raw, fmt)
    return raw


def generate(cards, root, refresh=()):
    results = []
    root = Path(root)
    for card in cards:
        result = {'name': card['name']}
        try:
            raw = safe_child(root / 'get', filename_for(card)).read_bytes()
            image_info(raw)
            outputs = []
            for extension, fmt, size in [('png', 'PNG', 60), ('webp', 'WEBP', 80)]:
                path = safe_child(root / 'img', card['name'] + '.' + extension)
                valid = False
                if path.exists() and card['name'] not in refresh:
                    try:
                        _, dimensions = image_info(path.read_bytes(), fmt)
                        valid = dimensions == (size, size)
                    except ValueError:
                        pass
                if not valid:
                    outputs.append((path, render_icon(card, raw, root, size)))
            for path, data in outputs:
                atomic_write(path, data)
            result['status'] = 'generated' if outputs else 'valid'
        except Exception as error:
            result.update(status='error', error=str(error))
        results.append(result)
    return results


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path('.'))
    args = parser.parse_args(argv)
    cards = json.loads((args.root / 'chara.json').read_text(encoding='utf-8'))
    report_path = args.root / 'reports/get-images.json'
    refresh = set()
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding='utf-8'))
        refresh = {r['name'] for r in report['results'] if r['status'] in {'repaired', 'downloaded'}}
    results = generate(cards, args.root, refresh)
    report = write_report(args.root / 'reports/make-icons.json', 'Generate card icons', results)
    return 1 if report['failedCount'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
