import json
import os
import re
import time
from datetime import datetime, timedelta

from bs4 import BeautifulSoup
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


def get_chara_dict(rank, url, masters, implementation_dates=None, namedict=None, cosdict=None):
    if namedict is None:
        namedict = getDict('namedict.txt')
    if cosdict is None:
        cosdict = getDict('cosdict.txt')

    scraped_card = scrape_card(rank, url, masters)
    outdict = build_card_record(None, scraped_card, namedict, cosdict, implementation_dates)
    outdict.pop('id', None)

    outDict('cosdict.txt', cosdict)
    outDict('namedict.txt', namedict)
    return outdict


def get_history():
    response = requests.get('https://twst.wikiru.jp/?RecentChanges')
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')
    items = soup.select('ul.list1.list-indent1 > li')

    results = []
    date_pattern = re.compile(r'\s*(\d{4}-\d{2}-\d{2}) \([月火水木金土日]\) (\d{2}:\d{2}:\d{2})')
    for item in items:
        text_content = item.text.strip()
        match = date_pattern.search(text_content)

        if match:
            date_str = match.group(1)
            time_str = match.group(2)
            date_time_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")

            if date_time_obj >= datetime.now() - timedelta(days=2):
                link_text = item.find('a').text.strip()
                if link_text.startswith('R/'):
                    results.append(['R', 'https://twst.wikiru.jp/?' + link_text])
                if link_text.startswith('SR/'):
                    results.append(['SR', 'https://twst.wikiru.jp/?' + link_text])
                if link_text.startswith('SSR/'):
                    results.append(['SSR', 'https://twst.wikiru.jp/?' + link_text])
    return results


def update_or_add_entry(data, new_entry):
    max_id = -1
    existing_entry = None

    for entry in data:
        try:
            max_id = max(max_id, int(entry.get('id', -1)))
        except (ValueError, TypeError):
            pass
        if entry.get('name') == new_entry.get('name'):
            existing_entry = entry

    if existing_entry is not None:
        preserved_id = existing_entry.get('id')
        existing_entry.update(new_entry)
        if preserved_id is not None:
            existing_entry['id'] = preserved_id
        print(f"Updated entry with name '{new_entry['name']}'.")
    else:
        new_entry['id'] = str(max_id + 1)
        data.append(new_entry)
        print(f"Added new entry with id '{new_entry['id']}' and name '{new_entry['name']}'.")
    return data


def sync_characters_info_from_namedict(info_path='characters_info.json', namedict_path='namedict.txt'):
    """
    namedict.txt から characters_info.json に不足キャラクターを追加する。
    既存キャラクターは更新せず、新規のみ追加する。
    追加時は dorm="スペシャル"、theme_1="", theme_2="" を設定。
    """
    try:
        namedict = getDict(namedict_path)
    except Exception as e:
        print(f"Failed to read {namedict_path}: {e}")
        return

    info = []
    if os.path.exists(info_path):
        try:
            with open(info_path, 'r', encoding='UTF-8') as f:
                info = json.load(f)
                if not isinstance(info, list):
                    print(f"Unexpected format in {info_path}; expected a list. Skipping update.")
                    return
        except Exception as e:
            print(f"Failed to load {info_path}: {e}")
            return

    existing_ja = {entry.get('name_ja') for entry in info if isinstance(entry, dict)}

    added = 0
    for ja_name, en_name in namedict.items():
        if not ja_name:
            continue
        if ja_name in existing_ja:
            continue
        new_entry = {
            'name_ja': ja_name,
            'name_en': en_name,
            'dorm': 'スペシャル',
            'theme_1': '',
            'theme_2': ''
        }
        info.append(new_entry)
        added += 1

    if added > 0:
        try:
            with open(info_path, 'w', encoding='UTF-8') as f:
                json.dump(info, f, ensure_ascii=False, indent=4)
            print(f"Added {added} character(s) to {info_path} from {namedict_path}.")
        except Exception as e:
            print(f"Failed to write {info_path}: {e}")
    else:
        print("No missing characters to add to characters_info.json.")


if __name__ == '__main__':
    histories = get_history()
    if len(histories) != 0:
        masters = make_type_dict(STATUS_TABLE_URL)
        implementation_dates = get_implementation_dates()
        namedict = getDict('namedict.txt')
        cosdict = getDict('cosdict.txt')

        with open("chara.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
        for history in histories:
            rank, url = history[0], history[1]
            chara_dict = get_chara_dict(rank, url, masters, implementation_dates, namedict, cosdict)
            time.sleep(1)
            data = update_or_add_entry(data, chara_dict)

        with open("chara.json", 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    sync_characters_info_from_namedict()
