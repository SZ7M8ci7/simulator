import json
import os
import random
import re
from collections import defaultdict

from bs4 import BeautifulSoup
from deep_translator import GoogleTranslator
import requests


STATUS_TABLE_URL = 'https://twst.wikiru.jp/?%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB/%E3%82%B9%E3%83%86%E3%83%BC%E3%82%BF%E3%82%B9%E4%B8%80%E8%A6%A7'
CARD_INFO_PATTERN = re.compile(
    r'レアリティ\s*(?P<rank>\S+)\s*衣装\s*(?P<costume>\S+)\s*タイプ\s*(?P<attr>\S+)'
    r'\s*HP\s*初期\s*(?P<base_hp>\d+)\s*最大\s*(?P<hp>\d+)'
    r'\s*ATK\s*初期\s*(?P<base_atk>\d+)\s*最大\s*(?P<atk>\d+)'
)


def getDict(path):
    dict = defaultdict(str)
    with open(path, "r", encoding='UTF-8') as f:
        for line in f:
            if len(line) <= 1:
                continue
            key, value = line.strip().split(":")
            dict[key] = value.strip()
    return dict


def outDict(path, dict):
    with open(path, "w", encoding='UTF-8') as f:
        for key, val in dict.items():
            f.write(f"{key}:{val}\n")


def normalize_card_text(text):
    return text.replace(' ', '').replace('（', '(').replace('）', ')').replace('＆', '&')


def is_limit_break_base(detail):
    return 'まで' in detail or '無凸' in detail


def find_card_tables(soup):
    info_table = None
    buddy_table = None
    magic_tables = []

    for table in soup.find_all("table", class_="style_table"):
        first_row = table.find("tr")
        if first_row is None:
            continue

        headers = [normalize_card_text(cell.get_text()) for cell in first_row.find_all(["th", "td"])]
        table_text = normalize_card_text(table.get_text())

        if info_table is None and 'レアリティ' in table_text and '衣装' in table_text and 'タイプ' in table_text and 'ATK' in table_text:
            info_table = table
        elif headers[:3] == ['属性', '名称', '効果']:
            magic_tables.append(table)
        elif headers and headers[0] == 'キャラ' and '名称' in headers and '効果' in headers:
            buddy_table = table

    return info_table, magic_tables, buddy_table


def parse_card_info(table):
    match = CARD_INFO_PATTERN.search(table.get_text())
    if match is None:
        raise ValueError('card info table format changed')
    return match.groupdict()


def is_valid_status_value(value):
    if value is None:
        return False

    text = str(value).strip()
    if text == '' or text.lower() in ('none', 'null'):
        return False

    if not text.isdigit():
        return False

    return int(text) > 0


def choose_status_value(fetched_value, fallback_value):
    if is_valid_status_value(fetched_value):
        return str(fetched_value).strip()
    if is_valid_status_value(fallback_value):
        return str(fallback_value).strip()
    return str(fetched_value).strip() if fetched_value is not None else ''


def parse_magic_text(table):
    txt = table.get_text()
    len_txt = len(txt)
    str_index = txt.rfind('Lv10') + 4
    end_index = len_txt - 1
    if len_txt - str_index < 6:
        end_index = str_index - 5
        str_index = txt.rfind('Lv5') + 3
    if len_txt - str_index < 10:
        end_index = str_index - 4
        str_index = txt.find('Lv1') + 3
    return normalize_card_text(txt[str_index:end_index].strip())


def load_local_masters():
    name_type_master = defaultdict(str)
    name_hp_master = defaultdict(str)
    name_atk_master = defaultdict(str)
    name_base_hp_master = defaultdict(str)
    name_base_atk_master = defaultdict(str)

    if not os.path.exists('chara.json'):
        return [name_type_master, name_hp_master, name_atk_master, name_base_hp_master, name_base_atk_master]

    with open('chara.json', 'r', encoding='utf-8') as f:
        for item in json.load(f):
            key = item.get('chara', '') + item.get('costume', '')
            if not key:
                continue
            name_type_master[key] = item.get('growtype', '')
            name_hp_master[key] = str(item.get('hp', ''))
            name_atk_master[key] = str(item.get('atk', ''))
            name_base_hp_master[key] = str(item.get('base_hp', ''))
            name_base_atk_master[key] = str(item.get('base_atk', ''))

    return [name_type_master, name_hp_master, name_atk_master, name_base_hp_master, name_base_atk_master]


def infer_growtype(rank, attr, hp, atk):
    if not os.path.exists('chara.json'):
        return ''

    try:
        hp_value = int(hp)
        atk_value = int(atk)
    except (TypeError, ValueError):
        return ''

    with open('chara.json', 'r', encoding='utf-8') as f:
        candidates = []
        for item in json.load(f):
            if item.get('rare') != rank or item.get('attr') != attr or not item.get('growtype'):
                continue
            try:
                ref_hp = int(item.get('hp', ''))
                ref_atk = int(item.get('atk', ''))
            except (TypeError, ValueError):
                continue
            if ref_hp == hp_value and ref_atk == atk_value:
                return item['growtype']
            candidates.append((abs((ref_hp / ref_atk) - (hp_value / atk_value)), item['growtype']))

    if not candidates:
        return ''

    candidates.sort(key=lambda item: item[0])
    return candidates[0][1]


def parse_buddy_entries(table):
    entries = []
    pending_entry = None

    for tr in table.find_all("tr"):
        cells = tr.find_all(["th", "td"])
        if not cells:
            continue

        first_text = normalize_card_text(cells[0].get_text())
        if first_text == 'キャラ':
            continue

        if cells[0].name == 'td':
            char_name = first_text
            if len(cells) >= 3 and cells[1].name == 'th':
                detail = normalize_card_text(cells[1].get_text())
                bonus = normalize_card_text(cells[2].get_text())
                entry = {'char': char_name, 'base': '', 'totsu': ''}
                if is_limit_break_base(detail):
                    entry['base'] = bonus
                else:
                    entry['totsu'] = bonus
                entries.append(entry)
                pending_entry = entry if cells[0].has_attr('rowspan') else None
            elif len(cells) >= 2:
                bonus = normalize_card_text(cells[1].get_text())
                entries.append({'char': char_name, 'base': bonus, 'totsu': bonus})
                pending_entry = None
        elif cells[0].name == 'th' and pending_entry is not None:
            detail = first_text
            bonus = normalize_card_text(cells[1].get_text()) if len(cells) >= 2 else ''
            if is_limit_break_base(detail):
                pending_entry['base'] = bonus
            else:
                pending_entry['totsu'] = bonus

    for entry in entries:
        if not entry['base']:
            entry['base'] = entry['totsu']
        if not entry['totsu']:
            entry['totsu'] = entry['base']

    return entries[:3]


def build_buddy_fields(entries):
    normalized_entries = list(entries)
    while len(normalized_entries) < 3:
        normalized_entries.append({'char': '', 'base': '', 'totsu': ''})

    return {
        'buddy1c': normalized_entries[0]['char'],
        'buddy1s': normalized_entries[0]['base'],
        'buddy1s_totsu': normalized_entries[0]['totsu'],
        'buddy2c': normalized_entries[1]['char'],
        'buddy2s': normalized_entries[1]['base'],
        'buddy2s_totsu': normalized_entries[1]['totsu'],
        'buddy3c': normalized_entries[2]['char'],
        'buddy3s': normalized_entries[2]['base'],
        'buddy3s_totsu': normalized_entries[2]['totsu'],
    }


def is_buddy_status(text):
    if not text:
        return False
    status_tokens = ('UP', '無効', '回避', '回復', 'ダメージ', 'クリティカル', 'ATK', 'HP')
    return any(token in text for token in status_tokens)


def normalize_buddy_fields(fields):
    for index in range(1, 4):
        char_key = f'buddy{index}c'
        status_key = f'buddy{index}s'
        totsu_key = f'buddy{index}s_totsu'

        char_value = fields.get(char_key, '')
        status_value = fields.get(status_key, '')
        totsu_value = fields.get(totsu_key, '')
        char_candidates = [value for value in (char_value, status_value, totsu_value) if value and not is_buddy_status(value)]
        status_candidates = [value for value in (status_value, totsu_value, char_value) if is_buddy_status(value)]

        if not char_value or is_buddy_status(char_value):
            fields[char_key] = char_candidates[0] if char_candidates else ''

        if not is_buddy_status(status_value):
            fields[status_key] = status_candidates[0] if status_candidates else ''

        if not is_buddy_status(totsu_value):
            replacement = next((value for value in status_candidates if value != fields[status_key]), '')
            fields[totsu_key] = replacement if replacement else fields[status_key]
        elif not totsu_value:
            fields[totsu_key] = fields[status_key]

    return fields


def sanitize_translated_text(text):
    return text.replace(' ', '_').replace('\'', '').replace('"', '')


def translate_cached(text, cache):
    if text not in cache:
        translated = GoogleTranslator(source='ja', target='en').translate(text).replace(' ', '_')
        if translated == '':
            translated = str(random.randint(1, 100000))
        cache[text] = sanitize_translated_text(translated)
    return cache[text]


def extract_duo_partner(magic_text):
    if '[DUO]' not in magic_text or 'と一緒' not in magic_text:
        return ''
    start = magic_text.index('[DUO]') + 5
    end = magic_text.index('と一緒')
    return magic_text[start:end]


def build_extra_effect_text(*magic_texts):
    etc_parts = []
    for magic_index, magic_text in enumerate(magic_texts, start=1):
        if not magic_text:
            continue
        for split_index, effect in enumerate(magic_text.split('&')):
            if split_index == 0:
                continue
            if magic_index == 2 and '[DUO]' in effect:
                continue
            etc_parts.append(f'{effect}(M{magic_index})')
    return normalize_card_text('<br>'.join(etc_parts))


def count_status_effects(etc_text):
    buff_count = 0
    debuff_count = 0

    for cur in etc_text.split('<br>'):
        if '被ダメージUP' in cur:
            continue
        if '被ダメージDOWN' in cur and ('味方' in cur or '自' in cur):
            debuff_count += 1
            continue

        if 'ATKUP' in cur:
            buff_count += 1
        elif 'ダメージUP' in cur and ('味方' in cur or '自' in cur):
            buff_count += 1
        elif 'クリティカル' in cur and ('味方' in cur or '自' in cur):
            buff_count += 1

        if 'ATKDOWN' in cur and '相手' in cur:
            debuff_count += 1
        elif 'ダメージDOWN' in cur and '相手' in cur:
            debuff_count += 1
        if '暗闇' in cur and '相手' in cur:
            debuff_count += 1

    return buff_count, debuff_count


def checkMagicPow(str):
    pow = ''
    if '2連撃' in str:
        pow += '連撃'
    elif '3連撃' in str:
        pow += '3連撃'
    else:
        pow += '単発'
    if '(強)' in str:
        pow += '(強)'
    else:
        pow += '(弱)'
    return pow


def checkMagicAttr(string):
    string = string[:8]
    attribute = ''
    if '火' in string:
        attribute = '火'
    elif '水' in string:
        attribute = '水'
    elif '木' in string:
        attribute = '木'
    elif '無' in string:
        attribute = '無'

    return attribute


def checkMagicHeal(str):
    heal = ''
    if 'HP回復(極小)' in str:
        heal = '回復(極小)'
    if 'HP回復(小)' in str:
        heal = '回復(小)'
    if 'HP回復(中)' in str:
        heal = '回復(中)'
    if 'HP継続回復(小)' in str:
        heal = '継続回復(小)'
    if 'HP継続回復(中)' in str:
        heal = '継続回復(中)'
    if 'HP継続回復(小)' in str and 'HP回復(小)' in str:
        heal = '回復&継続回復(小)'

    return heal


def checkMagicBuf(str):
    buf = ''
    if not ('自' in str or '味方' in str):
        return buf
    if 'ATKUP(極小)' in str:
        buf = 'ATKUP(極小)'
    if 'ATKUP(小)' in str:
        buf = 'ATKUP(小)'
    if 'ATKUP(中)' in str:
        buf = 'ATKUP(中)'
    if 'ATKUP(大)' in str:
        buf = 'ATKUP(大)'
    if 'ATKUP(極大)' in str:
        buf = 'ATKUP(極大)'
    if 'ダメージUP(極小)' in str and '被ダメージ' not in str:
        buf = 'ダメUP(極小)'
    if 'ダメージUP(小)' in str and '被ダメージ' not in str:
        buf = 'ダメUP(小)'
    if 'ダメージUP(中)' in str and '被ダメージ' not in str:
        buf = 'ダメUP(中)'
    if 'ダメージUP(中)' in str and '味方全体' in str:
        buf = 'ダメUP(中)'
    if 'ダメージUP(大)' in str and '被ダメージ' not in str:
        buf = 'ダメUP(大)'
    if 'ダメージUP(極大)' in str and '被ダメージ' not in str:
        buf = 'ダメUP(極大)'
    if '属性ダメージUP(極小)' in str:
        buf = '属性ダメUP(極小)'
    if '属性ダメージUP(小)' in str:
        buf = '属性ダメUP(小)'
    if '属性ダメージUP(中)' in str:
        buf = '属性ダメUP(中)'
    if '属性ダメージUP(大)' in str:
        buf = '属性ダメUP(大)'
    if '属性ダメージUP(極大)' in str:
        buf = '属性ダメUP(極大)'
    return buf


def build_card_record(card_id, scraped_card, namedict, cosdict, implementation_dates=None):
    magic1 = scraped_card['magic1']
    magic2 = scraped_card['magic2']
    magic3 = scraped_card['magic3']
    etc = build_extra_effect_text(magic1, magic2, magic3)
    buff_count, debuff_count = count_status_effects(etc)
    key = scraped_card['chara'] + scraped_card['costume']

    record = {
        'id': '' if card_id is None else str(card_id),
        'name': translate_cached(scraped_card['chara'], namedict) + '_' + translate_cached(scraped_card['costume'], cosdict),
        'chara': scraped_card['chara'],
        'costume': scraped_card['costume'],
        'attr': scraped_card['attr'],
        'base_hp': scraped_card['base_hp'],
        'base_atk': scraped_card['base_atk'],
        'hp': scraped_card['hp'],
        'atk': scraped_card['atk'],
        'magic1pow': checkMagicPow(magic1),
        'magic1atr': checkMagicAttr(magic1),
        'magic1buf': checkMagicBuf(magic1),
        'magic1heal': checkMagicHeal(magic1),
        'magic2pow': checkMagicPow(magic2),
        'magic2atr': checkMagicAttr(magic2),
        'magic2buf': checkMagicBuf(magic2),
        'magic2heal': checkMagicHeal(magic2),
        'duo': extract_duo_partner(magic2),
        'magic3pow': checkMagicPow(magic3),
        'magic3atr': checkMagicAttr(magic3),
        'magic3buf': checkMagicBuf(magic3),
        'magic3heal': checkMagicHeal(magic3),
        'etc': etc,
        'rare': scraped_card['rare'],
        'growtype': scraped_card['growtype'],
        'wikiURL': scraped_card['wikiURL'],
        'buff_count': buff_count,
        'debuff_count': debuff_count,
        'implementation_date': implementation_dates.get(key, '') if implementation_dates else '',
    }
    record.update({
        'buddy1c': scraped_card['buddy1c'],
        'buddy1s': scraped_card['buddy1s'],
        'buddy1s_totsu': scraped_card['buddy1s_totsu'],
        'buddy2c': scraped_card['buddy2c'],
        'buddy2s': scraped_card['buddy2s'],
        'buddy2s_totsu': scraped_card['buddy2s_totsu'],
        'buddy3c': scraped_card['buddy3c'],
        'buddy3s': scraped_card['buddy3s'],
        'buddy3s_totsu': scraped_card['buddy3s_totsu'],
    })
    return record


def extract_card_name(data_all):
    name = ''
    for item in data_all.find_all("title"):
        txt = item.getText()
        str_index = txt.find('/') + 1
        end_index = txt.rfind('【')
        name = txt[str_index:end_index]
    return name.replace('【ツイステ】', '')


def scrape_card(rank, url, masters):
    name_type_master = masters[0]
    name_hp_master = masters[1]
    name_atk_master = masters[2]
    name_base_hp_master = masters[3]
    name_base_atk_master = masters[4]
    result = requests.get(url)
    data_all = BeautifulSoup(result.text, 'html.parser')

    name = extract_card_name(data_all)
    info_table, magic_tables, buddy_table = find_card_tables(data_all)
    if info_table is None or len(magic_tables) < 2 or buddy_table is None:
        raise ValueError('card page table format changed')

    info = parse_card_info(info_table)
    costume = info['costume']
    attr = info['attr']
    base_hp = info['base_hp']
    base_atk = info['base_atk']
    HP = info['hp']
    ATK = info['atk']

    magic1 = parse_magic_text(magic_tables[0])
    magic2 = parse_magic_text(magic_tables[1])
    magic3 = parse_magic_text(magic_tables[2]) if rank == 'SSR' and len(magic_tables) >= 3 else ''
    buddy_fields = normalize_buddy_fields(build_buddy_fields(parse_buddy_entries(buddy_table)))
    key = name + costume
    growtype = name_type_master[key] if name_type_master[key] else infer_growtype(rank, attr, HP, ATK)
    return {
        'chara': name,
        'costume': costume,
        'rare': rank,
        'attr': attr,
        'base_hp': choose_status_value(base_hp, name_base_hp_master[key]),
        'base_atk': choose_status_value(base_atk, name_base_atk_master[key]),
        'hp': choose_status_value(HP, name_hp_master[key]),
        'atk': choose_status_value(ATK, name_atk_master[key]),
        'magic1': magic1,
        'magic2': magic2,
        'magic3': magic3,
        'growtype': growtype,
        'wikiURL': url,
        'buddy1c': buddy_fields['buddy1c'],
        'buddy1s': buddy_fields['buddy1s'],
        'buddy1s_totsu': buddy_fields['buddy1s_totsu'],
        'buddy2c': buddy_fields['buddy2c'],
        'buddy2s': buddy_fields['buddy2s'],
        'buddy2s_totsu': buddy_fields['buddy2s_totsu'],
        'buddy3c': buddy_fields['buddy3c'],
        'buddy3s': buddy_fields['buddy3s'],
        'buddy3s_totsu': buddy_fields['buddy3s_totsu'],
    }


def make_type_dict(url):
    masters = load_local_masters()

    try:
        response = requests.get(url)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'id': 'sortabletable1'})
        if table is None:
            return masters

        rows = table.find_all('tr')
        name_type_master, name_hp_master, name_atk_master, name_base_hp_master, name_base_atk_master = masters
        for row in rows:
            name = row.find('th')
            cells = row.find_all('td')
            if name is None:
                continue

            row_data = [name.text.strip()]
            for cell in cells:
                row_data.append(cell.text.strip())
            if len(row_data) < 12:
                continue

            key = row_data[0] + row_data[1]
            name_base_hp_master[key] = row_data[7]
            name_base_atk_master[key] = row_data[8]
            name_hp_master[key] = row_data[9]
            name_atk_master[key] = row_data[10]
            name_type_master[key] = row_data[11]
    except Exception:
        pass

    return masters


def get_implementation_dates():
    response = requests.get('https://twst.wikiru.jp/?SandBox/%E3%82%AB%E3%83%BC%E3%83%89%E5%AE%9F%E8%A3%85%E6%97%A5')
    html = response.text

    soup = BeautifulSoup(html, 'html.parser')
    implementation_dates = {}

    table = soup.find('table')
    if table:
        rows = table.find_all('tr')[1:]

        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 4:
                character = cells[0].text.strip()
                costume = cells[1].text.strip()
                costume = re.sub(r'\([^)]*\)', '', costume).strip()
                impl_date = cells[3].text.strip()

                key = character + costume
                implementation_dates[key] = impl_date

    return implementation_dates
