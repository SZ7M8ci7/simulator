import glob
import json
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


def get_chara_dict(rank, url, masters):
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
            etc += '<br>'
    magic2split = magic2.split('&')
    for i in range(len(magic2split)):
        if i > 0:
            if '[DUO]' not in magic2split[i]:
                etc += magic2split[i]
                etc += '<br>'
    magic3split = magic3.split('&')
    for i in range(len(magic3split)):
        if i > 0:
            etc += magic3split[i]
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
            
            # 現在の日時から3日以内であればリストに追加
            if date_time_obj >= datetime.now() - timedelta(days=7):
                link_text = item.find('a').text.strip()  # リンクテキスト部分
                if link_text.startswith('R/'):
                    results.append(['R', 'https://twst.wikiru.jp/?'+link_text])
                if link_text.startswith('SR/'):
                    results.append(['SR', 'https://twst.wikiru.jp/?'+link_text])
                if link_text.startswith('SSR/'):
                    results.append(['SSR', 'https://twst.wikiru.jp/?'+link_text])
    return results

def make_html(eng):
    out_html = '    <a href="#" rel="modal:close" onclick="gtag(\'event\', \'click\', {\'event_category\': \'chara\', \'event_label\':\'' + eng + '\', \'value\':\'1\'});changeImg(\''+eng+'\')"><img src="img/'+eng+'.png "onerror="this.onerror=null; this.src=\'notyet.png\';"></a>'
    return out_html

def update_or_add_entry(data, new_entry):

    max_id = -1
    existing_entry = None
    
    for entry in data:
        max_id = max(max_id, int(entry['id']))
        if entry['name'] == new_entry['name']:
            existing_entry = entry

    if existing_entry:
        # Update the existing entry
        existing_entry.update(new_entry)
        print(f"Updated entry with name '{new_entry['name']}'.")
    else:
        # Add the new entry with an incremented 'id'
        new_entry['id'] = str(max_id + 1)
        data.append(new_entry)
        print(f"Added new entry with id '{new_entry['id']}' and name '{new_entry['name']}'.")
        try:
                
            input_file = 'index.html'
            with open(input_file, 'r',encoding='UTF-8') as file:
                # ファイルを1行ずつ読み込み、処理を行う
                lines = file.readlines()
                for i in range(len(lines)):
                    if new_entry['chara']+'バースデー追加エリア' in lines[i] and 'birth' in new_entry['name']:
                        lines[i] = make_html(new_entry['name'])+'\n' + lines[i]
                        break
                    elif new_entry['chara']+'部活追加エリア' in lines[i] and 'club' in new_entry['name']:
                        lines[i] = make_html(new_entry['name'])+'\n' + lines[i]
                        break
                    elif new_entry['chara']+new_entry['rare']+'追加エリア' in lines[i]:
                        lines[i] = make_html(new_entry['name'])+'\n' + lines[i]
                        break

            # 処理結果を同一ファイルに書き込む
            with open(input_file, 'w',encoding='UTF-8') as file:
                file.writelines(lines)
        except Exception as e:
            print(e)
    return data

if __name__ == '__main__':
    histories = get_history()
    if len(histories) != 0:
        masters = make_type_dict('https://twst.wikiru.jp/?%E3%82%AB%E3%83%BC%E3%83%89%E6%88%90%E9%95%B7%E7%8E%87')
        
        # Load the existing data
        with open("chara.json", 'r') as file:
            data = json.load(file)
        for history in histories:
            rank, url = history[0], history[1]
            chara_dict = get_chara_dict(rank, url, masters)
            time.sleep(1)
            data = update_or_add_entry(data, chara_dict)
        
        with open("chara.json", 'w') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)