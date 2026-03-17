import glob
import json
import os
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


def ensure_output_dirs():
    os.makedirs(GET_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)


def build_magicdict(cards):
    magicdict = defaultdict(list)
    for card in cards:
        magicdict[card['name']] = [card['magic1atr'], card['magic2atr'], card['magic3atr']]
    return magicdict


def write_chara_json(cards, path='chara.json'):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(cards, f, sort_keys=True, indent=4, ensure_ascii=False)


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


def fetch_card_titles_by_rank():
    url = "https://twst.wikiru.jp/?cmd=list"
    result = requests.get(url)
    data_all = BeautifulSoup(result.text, 'html.parser')
    titles_by_rank = {'SSR': [], 'SR': [], 'R': []}

    for link in data_all.find_all('a'):
        for rank in titles_by_rank:
            if link.text.startswith(rank) and link.text.endswith('】'):
                titles_by_rank[rank].append(link.text)
                break

    return titles_by_rank


def download_missing_icons(card_titles):
    ensure_output_dirs()
    exists_files = {os.path.basename(file).lower() for file in glob.glob(os.path.join(GET_DIR, '*'))}
    for title in card_titles:
        get_img(title, exists_files)


def get_list(rank):
    titles_by_rank = fetch_card_titles_by_rank()
    return [build_card_url(title) for title in titles_by_rank.get(rank, [])]


if __name__ == '__main__':
    masters = make_type_dict(STATUS_TABLE_URL)
    namedict = getDict('namedict.txt')
    cosdict = getDict('cosdict.txt')
    implementation_dates = get_implementation_dates()
    titles_by_rank = fetch_card_titles_by_rank()
    download_missing_icons([
        title
        for rank in ('SSR', 'SR', 'R')
        for title in titles_by_rank.get(rank, [])
    ])

    cards = []
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

    write_chara_json(cards)
    outDict('cosdict.txt', cosdict)
    outDict('namedict.txt', namedict)
    makeicon(cards)
