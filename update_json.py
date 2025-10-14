import json
import os
import time
from collections import defaultdict
from deep_translator import GoogleTranslator
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta

def getDict(path):
    dict = defaultdict(str)
    with open(path, "r", encoding='UTF-8') as f:
        # ファイルの各行に対して処理を行う
        for line in f:
            if len(line) <= 1:
                continue
            # 行末の改行コードを削除して分割
            key, value = line.strip().split(":")
            # 辞書型にキーと値を追加
            dict[key] = value.strip()
    return dict
def outDict(path,dict):
    with open(path, "w", encoding='UTF-8') as f:
        for key, val in dict.items():
            f.write(f"{key}:{val}\n")


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
    if 'ダメージUP(中)' in str and '味方全体' in str: # フェロー用特別ロジック
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


def get_chara_dict(rank, url, masters, implementation_dates=None):
    namedict = getDict('namedict.txt')
    cosdict = getDict('cosdict.txt')
    name_type_master = masters[0]
    name_hp_master = masters[1]
    name_atk_master = masters[2]
    name_base_hp_master = masters[3]
    name_base_atk_master = masters[4]
    result = requests.get(url)
    data_all = BeautifulSoup(result.text, 'html.parser')
    # キャラ名
    name = ""
    for item in data_all.find_all("title"):
        txt = item.getText()
        str_index = txt.find('/') + 1
        end_index = txt.rfind('【')
        name = txt[str_index:end_index]

    count = 0
    magic3 = ''
    for item in data_all.find_all("table", class_="style_table"):
        count += 1
        txt = item.getText()
        # 一つ目のテーブル
        if count == 1:
            typeindex = 0
            if 'タイプ・' in txt:
                typeindex = txt.find('タイプ')+1
            # 衣装
            str_index = txt.find('衣装') + 3
            end_index = txt.find('タイプ',typeindex) - 1
            costume = txt[str_index:end_index].strip()
            # タイプ
            str_index = txt.find('タイプ',typeindex) + 4
            end_index = txt.find('HP') - 1
            attr = txt[str_index:end_index].strip()
            # HP
            str_index = txt.find('最大') + 2
            end_index = txt.find('ATK') - 1
            HP = txt[str_index:end_index].strip()
            # ATK
            str_index = txt.rfind('最大') + 2
            end_index = str_index + 6
            ATK = txt[str_index:end_index].strip()
        # 二つ目のテーブル
        len_txt = len(txt)
        if count == 3:
            # マジック１
            str_index = txt.rfind('Lv10') + 4
            end_index = len_txt - 1
            if len_txt - str_index < 6:
                end_index = str_index - 5
                str_index = txt.rfind('Lv5') + 3
            if len_txt - str_index < 10:
                end_index = str_index - 4
                str_index = txt.find('Lv1') + 3
            magic1 = txt[str_index:end_index].strip().replace(' ', '').replace('（', '(').replace('）', ')').replace('＆', '&')
        # 三つ目のテーブル
        if count == 4:
            # マジック２
            str_index = txt.rfind('Lv10') + 4
            end_index = len_txt - 1
            if len_txt - str_index < 6:
                end_index = str_index - 5
                str_index = txt.rfind('Lv5') + 3
            if len_txt - str_index < 10:
                end_index = str_index - 4
                str_index = txt.find('Lv1') + 3
            magic2 = txt[str_index:end_index].strip().replace(' ', '').replace('（', '(').replace('）', ')').replace('＆', '&')
        # 三つ目のテーブル
        if count == 5 and rank == 'SSR':
            # マジック３
            str_index = txt.rfind('Lv10') + 4
            end_index = len_txt - 1
            if len_txt - str_index < 6:
                end_index = str_index - 5
                str_index = txt.rfind('Lv5') + 3
            if len_txt - str_index < 10:
                end_index = str_index - 4
                str_index = txt.find('Lv1') + 3
            magic3 = txt[str_index:end_index].strip().replace(' ', '').replace('（', '(').replace('）', ')').replace('＆', '&')
        # 四つ目のテーブル
        if (count == 6 and rank == 'SSR') or (count == 5 and rank != 'SSR'):
            # バディ
            trs = item.findAll("tr")
            buddies = ['','','','','','']
            buddies_num = 0
            for tr in trs:
                detail = 0
                for cell in tr.findAll('td'):
                    detail += 1
                    if detail == 3:
                        break
                    buddies[buddies_num] = cell.get_text().replace(' ', '').replace('（', '(').replace('）', ')').replace('＆', '&')
                    buddies_num+=1
    name = name.replace('【ツイステ】', '')

    outdict = dict()
    if name not in namedict.keys():
        namedict[name] = GoogleTranslator(source='ja',target='en').translate(name).replace(' ','_').replace('\'','').replace('"','')
    if costume not in cosdict.keys():
        cosdict[costume] = GoogleTranslator(source='ja',target='en').translate(costume).replace(' ','_').replace('\'','').replace('"','')
    outdict['name'] = namedict[name] + '_' + cosdict[costume]
    outdict['chara'] = name
    outdict['costume'] = costume
    outdict['attr'] = attr
    outdict['base_hp'] =  str(name_base_hp_master[name+costume])
    outdict['base_atk'] = str(name_base_atk_master[name+costume])
    outdict['hp'] = str(name_hp_master[name+costume] if name_hp_master[name+costume] else HP)
    outdict['atk'] = str(name_atk_master[name+costume] if name_atk_master[name+costume] else ATK)
    outdict['magic1pow'] = checkMagicPow(magic1)
    outdict['magic1atr'] = checkMagicAttr(magic1)
    outdict['magic1buf'] = checkMagicBuf(magic1)
    outdict['magic1heal'] = checkMagicHeal(magic1)
    outdict['magic2pow'] = checkMagicPow(magic2)
    outdict['magic2atr'] = checkMagicAttr(magic2)
    outdict['magic2buf'] = checkMagicBuf(magic2)
    outdict['magic2heal'] = checkMagicHeal(magic2)
    duo = ''
    if '[DUO]' in magic2:
        start = magic2.index('[DUO]') + 5
        end = magic2.index('と一緒')
        duo = magic2[start:end]
    outdict['duo'] = duo
    outdict['magic3pow'] = checkMagicPow(magic3)
    outdict['magic3atr'] = checkMagicAttr(magic3)
    outdict['magic3buf'] = checkMagicBuf(magic3)
    outdict['magic3heal'] = checkMagicHeal(magic3)
    outdict['buddy1c'] = buddies[0]
    outdict['buddy1s'] = buddies[1]
    outdict['buddy2c'] = buddies[2]
    outdict['buddy2s'] = buddies[3]
    outdict['buddy3c'] = buddies[4]
    outdict['buddy3s'] = buddies[5]
    etc = ''
    magic1split = magic1.split('&')
    for i in range(len(magic1split)):
        if i > 0:
            etc += magic1split[i]
            etc += '(M1)'
            etc += '<br>'
    magic2split = magic2.split('&')
    for i in range(len(magic2split)):
        if i > 0:
            if '[DUO]' not in magic2split[i]:
                etc += magic2split[i]
                etc += '(M2)'
                etc += '<br>'
    magic3split = magic3.split('&')
    for i in range(len(magic3split)):
        if i > 0:
            etc += magic3split[i]
            etc += '(M3)'
            etc += '<br>'
    etc = etc.replace(' ', '').replace('（', '(').replace('）', ')').replace('＆', '&')
    splitted_etc = etc.split('<br>')
    buff_count = 0
    debuff_count = 0
    for cur in splitted_etc:
        if '被ダメージUP' in cur:
            continue
        if '被ダメージDOWN' in cur and ('味方' in cur or '自' in cur):
            debuff_count+=1
            continue

        if 'ATKUP' in cur:
            buff_count+=1
        elif 'ダメージUP' in cur and ('味方' in cur or '自' in cur):
            buff_count+=1
        elif 'クリティカル' in cur and ('味方' in cur or '自' in cur):
            buff_count+=1

        if 'ATKDOWN' in cur and '相手' in cur:
            debuff_count+=1
        elif 'ダメージDOWN' in cur and '相手' in cur:
            debuff_count+=1
        
    outdict['etc'] = etc
    outdict['rare'] = rank
    outdict['growtype'] = name_type_master[name+costume]
    outdict['wikiURL'] = url
    outdict['buff_count'] = buff_count
    outdict['debuff_count'] = debuff_count
    
    # 実装日をマッチング
    impl_date = ''
    if implementation_dates:
        key = name + costume
        impl_date = implementation_dates.get(key, '')
    outdict['implementation_date'] = impl_date
    
    outDict('cosdict.txt',cosdict)
    outDict('namedict.txt',namedict)
    return outdict
    
def make_type_dict(url):
    response = requests.get(url)
    html = response.text

    # BeautifulSoupを使用してHTMLを解析する
    soup = BeautifulSoup(html, 'html.parser')

    # 目的のテーブルを抽出する
    table = soup.find('table', {'class': 'style_table'})

    # テーブル内のすべての行を取得する
    rows = table.find_all('tr')

    # リストを初期化する
    name_type_master = defaultdict(str)
    name_hp_master = defaultdict(str)
    name_atk_master = defaultdict(str)
    name_base_hp_master = defaultdict(str)
    name_base_atk_master = defaultdict(str)
    # 各行を反復処理し、各行のすべてのセルを取得する
    for row in rows:
        name = row.find('th')
        cells = row.find_all('td')

        # セルの値をリストに追加する
        row_data = [name.text.strip()]
        for cell in cells:
            row_data.append(cell.text.strip())
        if len(row_data) < 3:
            continue
        # 行の値をリストに追加する
        name_base_hp_master[row_data[0]+row_data[1]] = row_data[7]
        name_base_atk_master[row_data[0]+row_data[1]] = row_data[8]
        name_hp_master[row_data[0]+row_data[1]] = row_data[9]
        name_atk_master[row_data[0]+row_data[1]] = row_data[10]
        name_type_master[row_data[0]+row_data[1]] = row_data[11]
    return [name_type_master,name_hp_master,name_atk_master,name_base_hp_master,name_base_atk_master]


def get_implementation_dates():
    """実装日情報を取得する関数"""
    response = requests.get('https://twst.wikiru.jp/?SandBox/%E3%82%AB%E3%83%BC%E3%83%89%E5%AE%9F%E8%A3%85%E6%97%A5')
    html = response.text
    
    soup = BeautifulSoup(html, 'html.parser')
    
    # 実装日データ辞書を初期化
    implementation_dates = {}
    
    # テーブルを探して実装日情報を抽出
    table = soup.find('table')
    if table:
        rows = table.find_all('tr')[1:]  # ヘッダー行をスキップ
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            if len(cells) >= 4:
                character = cells[0].text.strip()
                costume = cells[1].text.strip()
                # costume内の半角括弧で囲まれた部分を除去
                costume = re.sub(r'\([^)]*\)', '', costume).strip()
                rarity = cells[2].text.strip()
                impl_date = cells[3].text.strip()
                
                # キー生成（キャラクター名＋衣装名）
                key = character + costume
                implementation_dates[key] = impl_date
    
    return implementation_dates

def get_history():
    response = requests.get('https://twst.wikiru.jp/?RecentChanges')
    html = response.text

    # BeautifulSoupでHTMLを解析
    soup = BeautifulSoup(html, 'html.parser')

    # 各<li>タグを取得
    items = soup.select('ul.list1.list-indent1 > li')

    results = []
    date_pattern = re.compile(r'\s*(\d{4}-\d{2}-\d{2}) \([月火水木金土日]\) (\d{2}:\d{2}:\d{2})')
    # 各<li>からデータを抽出し、日付フォーマットが一致する場合のみ処理
    for item in items:
        text_content = item.text.strip()
        match = date_pattern.search(text_content)  # search()に変更して柔軟にマッチ

        if match:
            # 日付と時間を抽出してdatetimeオブジェクトに変換
            date_str = match.group(1)  # YYYY-MM-DD
            time_str = match.group(2)  # HH:MM:SS
            date_time_obj = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")
            
            # 現在の日時から2日以内であればリストに追加
            if date_time_obj >= datetime.now() - timedelta(days=2):
                link_text = item.find('a').text.strip()  # リンクテキスト部分
                if link_text.startswith('R/'):
                    results.append(['R', 'https://twst.wikiru.jp/?'+link_text])
                if link_text.startswith('SR/'):
                    results.append(['SR', 'https://twst.wikiru.jp/?'+link_text])
                if link_text.startswith('SSR/'):
                    results.append(['SSR', 'https://twst.wikiru.jp/?'+link_text])
    return results


def update_or_add_entry(data, new_entry):
    max_id = -1
    existing_entry = None
    
    for entry in data:
        # 最大IDを算出（IDは文字列想定のためint変換）
        try:
            max_id = max(max_id, int(entry.get('id', -1)))
        except (ValueError, TypeError):
            pass
        # 既存エントリの有無を name で判定
        if entry.get('name') == new_entry.get('name'):
            existing_entry = entry

    if existing_entry is not None:
        # 既存のIDは保持したままフィールドを更新
        preserved_id = existing_entry.get('id')
        existing_entry.update(new_entry)
        if preserved_id is not None:
            existing_entry['id'] = preserved_id
        print(f"Updated entry with name '{new_entry['name']}'.")
    else:
        # 新規追加時は連番IDを採番
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
        namedict = getDict(namedict_path)  # JA -> EN
    except Exception as e:
        print(f"Failed to read {namedict_path}: {e}")
        return

    # 既存の characters_info.json を読み込み（なければ空リスト）
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
        # en_name が空の場合でもとりあえず追加（必要なら後で手動補完）
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
        masters = make_type_dict('https://twst.wikiru.jp/?%E3%82%AB%E3%83%BC%E3%83%89%E6%88%90%E9%95%B7%E7%8E%87')
        
        # 実装日情報を取得
        implementation_dates = get_implementation_dates()
        
        # Load the existing data
        with open("chara.json", 'r') as file:
            data = json.load(file)
        for history in histories:
            rank, url = history[0], history[1]
            chara_dict = get_chara_dict(rank, url, masters, implementation_dates)
            time.sleep(1)
            data = update_or_add_entry(data, chara_dict)
        
        with open("chara.json", 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    # namedict.txt から characters_info.json に不足キャラクターを追加
    sync_characters_info_from_namedict()
