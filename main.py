import glob
import json
import os
import tempfile
import time
from collections import defaultdict

from bs4 import BeautifulSoup
from PIL import Image
import requests

from scraper_common import (
    STATUS_TABLE_URL,
    build_card_record,
    getDict,
    get_implementation_dates,
    make_type_dict,
    outDict,
    scrape_card,
)


GET_DIR = 'get'
IMG_DIR = 'img'
CARD_LIST_URL = 'https://twst.wikiru.jp/?cmd=list'
MIN_CARD_TITLE_COUNT = 400
MIN_PREVIOUS_COUNT_RATIO = 0.98
REQUEST_ATTEMPTS = 3
REQUEST_TIMEOUT_SECONDS = 30


def ensure_output_dirs():
    os.makedirs(GET_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)


def build_magicdict(cards):
    magicdict = defaultdict(list)
    for card in cards:
        magicdict[card['name']] = [card['magic1atr'], card['magic2atr'], card['magic3atr']]
    return magicdict


def load_chara_json(path='chara.json'):
    if not os.path.exists(path):
        return []

    with open(path, 'r', encoding='utf-8') as f:
        cards = json.load(f)

    if not isinstance(cards, list):
        raise ValueError(f'{path} must contain a JSON list')
    return cards


def write_chara_json(cards, path='chara.json'):
    if not cards:
        raise ValueError('Refusing to replace chara.json with an empty card list')

    target_path = os.path.abspath(path)
    target_dir = os.path.dirname(target_path)
    os.makedirs(target_dir, exist_ok=True)
    file_descriptor, temp_path = tempfile.mkstemp(
        dir=target_dir,
        prefix=f'.{os.path.basename(target_path)}.',
        suffix='.tmp',
        text=True,
    )

    try:
        with os.fdopen(file_descriptor, 'w', encoding='utf-8') as f:
            json.dump(cards, f, sort_keys=True, indent=4, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, target_path)
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        raise


def parse_icon_source(file_path):
    filename = os.path.basename(file_path)
    rank = next((candidate for candidate in ('SSR', 'SR', 'R') if filename.startswith(candidate)), '')
    if not rank or '【' not in filename or '】' not in filename:
        return None

    leftbracket = filename.index('【')
    rightbracket = filename.index('】')
    return rank, filename[len(rank):leftbracket], filename[leftbracket + 1:rightbracket]


def makeicon(cards):
    ensure_output_dirs()
    card_lookup = {
        (card['rare'], card['chara'], card['costume']): card
        for card in cards
    }

    for file in glob.glob(os.path.join(GET_DIR, '*')):
        try:
            icon_source = parse_icon_source(file)
            if icon_source is None:
                continue

            card = card_lookup.get(icon_source)
            if card is None:
                continue

            max_magic = 3 if card['rare'] == 'SSR' else 2
            magics = [card['magic1atr'], card['magic2atr'], card['magic3atr']]
            if any(not magic for magic in magics[:max_magic]):
                continue

            background_image = Image.open(file).convert("RGBA")
            background_image = background_image.resize((60, 60))
            start_pos = background_image.width - max_magic * 12 - (max_magic - 1)
            for magic_index in range(max_magic):
                foreground_image = Image.open(f"{magics[magic_index]}.png").convert("RGBA")
                background_image.alpha_composite(
                    foreground_image,
                    (start_pos + foreground_image.width * magic_index + magic_index, 0),
                )

            background_image.save(os.path.join(IMG_DIR, card['name'] + '.png'))
        except Exception as e:
            print(e, file)


def main(rank, url, masters):
    return scrape_card(rank, url, masters)


def get_img(title, exists_files):
    ensure_output_dirs()
    filename = title.replace('/', '').replace('\\', '') + 'アイコン.jpg'
    normalized_filename = filename.lower()
    try:
        if normalized_filename in exists_files:
            return
        time.sleep(1)
        url = "https://twst.wikiru.jp/attach2/696D67_" + filename.encode('utf-8').hex().rstrip().upper() + ".jpg"
        r = requests.get(url)
        if 200 != r.status_code:
            return
        path = os.path.join(GET_DIR, filename)
        with open(path, 'wb') as image_file:
            image_file.write(r.content)
        exists_files.add(normalized_filename)
    except Exception:
        pass


def build_card_url(title):
    return 'https://twst.wikiru.jp/?' + title


def get_with_retries(url, attempts=REQUEST_ATTEMPTS, timeout=REQUEST_TIMEOUT_SECONDS):
    last_error = None
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            return response
        except requests.RequestException as error:
            last_error = error
            if attempt < attempts:
                time.sleep(2 ** (attempt - 1))

    raise RuntimeError(f'Failed to fetch {url} after {attempts} attempts') from last_error


def validate_card_titles(titles_by_rank, previous_count=0):
    counts = {rank: len(titles_by_rank.get(rank, [])) for rank in ('SSR', 'SR', 'R')}
    total_count = sum(counts.values())
    minimum_count = max(
        MIN_CARD_TITLE_COUNT,
        int(previous_count * MIN_PREVIOUS_COUNT_RATIO),
    )

    if any(count == 0 for count in counts.values()) or total_count < minimum_count:
        raise RuntimeError(
            'Card list response is incomplete; refusing to update chara.json '
            f'(counts={counts}, total={total_count}, required>={minimum_count})'
        )

    return total_count


def fetch_card_titles_by_rank(previous_count=0):
    result = get_with_retries(CARD_LIST_URL)
    data_all = BeautifulSoup(result.text, 'html.parser')
    titles_by_rank = {'SSR': [], 'SR': [], 'R': []}
    seen_titles = {rank: set() for rank in titles_by_rank}

    for link in data_all.find_all('a'):
        title = link.get_text(strip=True)
        for rank in titles_by_rank:
            if (
                title.startswith(f'{rank}/')
                and title.endswith('】')
                and title not in seen_titles[rank]
            ):
                titles_by_rank[rank].append(title)
                seen_titles[rank].add(title)
                break

    validate_card_titles(titles_by_rank, previous_count)
    return titles_by_rank


def validate_generated_cards(cards, expected_count):
    if len(cards) != expected_count:
        raise RuntimeError(
            'Card scraping was incomplete; refusing to update chara.json '
            f'(generated={len(cards)}, expected={expected_count})'
        )


def download_missing_icons(card_titles):
    ensure_output_dirs()
    exists_files = {os.path.basename(file).lower() for file in glob.glob(os.path.join(GET_DIR, '*'))}
    for title in card_titles:
        get_img(title, exists_files)


def get_list(rank):
    titles_by_rank = fetch_card_titles_by_rank()
    return [build_card_url(title) for title in titles_by_rank.get(rank, [])]


def run_full_update():
    previous_cards = load_chara_json()
    titles_by_rank = fetch_card_titles_by_rank(len(previous_cards))
    expected_count = sum(len(titles) for titles in titles_by_rank.values())
    masters = make_type_dict(STATUS_TABLE_URL)
    namedict = getDict('namedict.txt')
    cosdict = getDict('cosdict.txt')
    implementation_dates = get_implementation_dates()
    download_missing_icons([
        title
        for rank in ('SSR', 'SR', 'R')
        for title in titles_by_rank.get(rank, [])
    ])

    cards = []
    failures = []
    count = 0
    for rank in ('SSR', 'SR', 'R'):
        for title in titles_by_rank.get(rank, []):
            cur_url = build_card_url(title)
            try:
                time.sleep(1)
                scraped_card = scrape_card(rank, cur_url, masters)
                cards.append(build_card_record(count, scraped_card, namedict, cosdict, implementation_dates))
                count += 1
            except Exception as e:
                print(e, cur_url)
                failures.append(cur_url)

    if failures:
        print(f'Failed to scrape {len(failures)} card(s).')
    validate_generated_cards(cards, expected_count)
    write_chara_json(cards)
    outDict('cosdict.txt', cosdict)
    outDict('namedict.txt', namedict)
    makeicon(cards)


if __name__ == '__main__':
    run_full_update()
