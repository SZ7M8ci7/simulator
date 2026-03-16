import csv
import glob
import json
import os
import time
from collections import defaultdict
from PIL import Image
from deep_translator import GoogleTranslator
import requests
from bs4 import BeautifulSoup
import re
import random

STATUS_TABLE_URL = 'https://twst.wikiru.jp/?%E3%83%86%E3%83%BC%E3%83%96%E3%83%AB/%E3%82%B9%E3%83%86%E3%83%BC%E3%82%BF%E3%82%B9%E4%B8%80%E8%A6%A7'
CARD_INFO_PATTERN = re.compile(
    r'レアリティ\s*(?P<rank>\S+)\s*衣装\s*(?P<costume>\S+)\s*タイプ\s*(?P<attr>\S+)'
    r'\s*HP\s*初期\s*(?P<base_hp>\d+)\s*最大\s*(?P<hp>\d+)'
    r'\s*ATK\s*初期\s*(?P<base_atk>\d+)\s*最大\s*(?P<atk>\d+)'
)

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
def getCharaDict(path,namedict,cosdict, implementation_dates=None):
    csv_file = open(path, "r", encoding="utf-8", errors="", newline="")
    # リスト形式
    f = csv.reader(csv_file, delimiter="\t", doublequote=True, lineterminator="\r\n", quotechar='"',
                   skipinitialspace=True)
    card_list = [row for row in f]
    outlist = []
    magicdict = defaultdict(list)
    for chara in card_list:
        # 1,2 名前
        # 3,4 レア,タイプ
        # 7,8 HP,ATK
        # 12-20 バディ関連（*_totsu を含む）
        # 17,18  デバフ
        # 19,20  回復
        outdict = dict()
        outdict['id'] = chara[0]
        if chara[1] not in namedict.keys():
            namedict[chara[1]] = GoogleTranslator(source='ja',target='en').translate(chara[1]).replace(' ','_').replace('\'','').replace('"','')
        if chara[2] not in cosdict.keys():
            cosdict[chara[2]] = GoogleTranslator(source='ja',target='en').translate(chara[2]).replace(' ','_').replace('\'','').replace('"','')
        outdict['name'] = namedict[chara[1]] + '_' + cosdict[chara[2]]
        outdict['chara'] = chara[1]
        outdict['costume'] = chara[2]
        outdict['attr'] = chara[4]
        outdict['base_hp'] = chara[5]
        outdict['base_atk'] = chara[6]
        outdict['hp'] = chara[7]
        outdict['atk'] = chara[8]
        outdict['magic1pow'] = checkMagicPow(chara[9])
        outdict['magic1atr'] = checkMagicAttr(chara[9])
        outdict['magic1buf'] = checkMagicBuf(chara[9])
        outdict['magic1heal'] = checkMagicHeal(chara[9])
        outdict['magic2pow'] = checkMagicPow(chara[10])
        outdict['magic2atr'] = checkMagicAttr(chara[10])
        outdict['magic2buf'] = checkMagicBuf(chara[10])
        outdict['magic2heal'] = checkMagicHeal(chara[10])
        duo = ''
        if '[DUO]' in chara[10]:
            start = chara[10].index('[DUO]') + 5
            end = chara[10].index('と一緒')
            duo = chara[10][start:end]
        outdict['duo'] = duo
        outdict['magic3pow'] = checkMagicPow(chara[11])
        outdict['magic3atr'] = checkMagicAttr(chara[11])
        outdict['magic3buf'] = checkMagicBuf(chara[11])
        outdict['magic3heal'] = checkMagicHeal(chara[11])
        if len(chara) >= 28:
            outdict['buddy1c'] = chara[12]
            outdict['buddy1s'] = chara[13]
            outdict['buddy1s_totsu'] = chara[14]
            outdict['buddy2c'] = chara[15]
            outdict['buddy2s'] = chara[16]
            outdict['buddy2s_totsu'] = chara[17]
            outdict['buddy3c'] = chara[18]
            outdict['buddy3s'] = chara[19]
            outdict['buddy3s_totsu'] = chara[20]
            growtype_index = 25
        elif len(chara) >= 26:
            outdict['buddy1c'] = chara[12]
            outdict['buddy1s'] = chara[13]
            outdict['buddy1s_totsu'] = chara[14]
            outdict['buddy2c'] = chara[15]
            outdict['buddy2s'] = chara[16]
            outdict['buddy2s_totsu'] = chara[16]
            outdict['buddy3c'] = chara[17]
            outdict['buddy3s'] = chara[18]
            outdict['buddy3s_totsu'] = chara[18]
            growtype_index = 23
        else:
            outdict['buddy1c'] = chara[12]
            outdict['buddy1s'] = chara[13]
            outdict['buddy1s_totsu'] = chara[13]
            outdict['buddy2c'] = chara[14]
            outdict['buddy2s'] = chara[15]
            outdict['buddy2s_totsu'] = chara[15]
            outdict['buddy3c'] = chara[16]
            outdict['buddy3s'] = chara[17]
            outdict['buddy3s_totsu'] = chara[17]
            growtype_index = 22
        etc = ''
        magic1split = chara[9].split('&')
        for i in range(len(magic1split)):
            if i > 0:
                etc += magic1split[i]
                etc += '(M1)'
                etc += '<br>'
        magic2split = chara[10].split('&')
        for i in range(len(magic2split)):
            if i > 0:
                if '[DUO]' not in magic2split[i]:
                    etc += magic2split[i]
                    etc += '(M2)'
                    etc += '<br>'
        magic3split = chara[11].split('&')
        for i in range(len(magic3split)):
            if i > 0:
                etc += magic3split[i]
                etc += '(M3)'
                etc += '<br>'
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
            if '暗闇' in cur and '相手' in cur:
                debuff_count+=1
            
        outdict['etc'] = etc
        outdict['rare'] = chara[3]
        outdict['growtype'] = chara[growtype_index]
        outdict['wikiURL'] = chara[-1]
        outdict['buff_count'] = buff_count
        outdict['debuff_count'] = debuff_count
        # 実装日をマッチング
        impl_date = ''
        if implementation_dates:
            key = chara[1] + chara[2]
            impl_date = implementation_dates.get(key, '')
        outdict['implementation_date'] = impl_date

        outlist.append(outdict)
        magicdict[outdict['name']] = [outdict['magic1atr'],outdict['magic2atr'],outdict['magic3atr']]

    with open('chara.json', 'w', encoding="utf-8") as f:
        json.dump(outlist, f, sort_keys=True, indent=4, ensure_ascii=False)

    return magicdict


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

def makeicon(implementation_dates=None):
    cosdict = getDict('cosdict.txt')
    namedict = getDict('namedict.txt')
    charadict = getCharaDict('charadata.tsv',namedict,cosdict, implementation_dates)
    files = glob.glob("get/*")
    out_files = glob.glob("img/*")
    out_files = [file.split('/')[-1] for file in out_files]

    for file in files:
        try:
            filename = file.split('/')[-1]
            rank = ''
            if 'SSR' in filename:
                rank = 'SSR'
            elif 'SR' in filename:
                rank = 'SR'
            else:
                rank = 'R'
            if '【' not in filename:
                continue
            if '】' not in filename:
                continue
            leftbracket = filename.index('【')
            rightbracket = filename.index('】')

            name = filename[len(rank):leftbracket]
            cos = filename[leftbracket+1:rightbracket]
            if name not in namedict:
                add_name = GoogleTranslator(source='ja',target='en').translate(name).replace(' ','_')
                if add_name == '':
                    add_name = str(random.randint(1,100000))
                namedict[name] = add_name.replace('\'','').replace('"','')
            if cos not in cosdict:
                add_cos = GoogleTranslator(source='ja',target='en').translate(cos).replace(' ','_')
                if add_cos == '':
                    add_cos = str(random.randint(1,100000))
                cosdict[cos] = add_cos.replace('\'','').replace('"','')
            output_filename = namedict[name] + '_' + cosdict[cos]

            max_magic = 2
            if rank == 'SSR':
                max_magic = 3
            magics = charadict[output_filename]
            # 画像合成
            background_image = Image.open(file).convert("RGBA")

            # 背景画像を60x60の正方形にリサイズする
            background_image = background_image.resize((60, 60))
            start_pos = background_image.width - max_magic*12 - (max_magic-1)
            for magic in range(max_magic):

                # 合成する画像を開く
                foreground_image = Image.open(f"{magics[magic]}.png")

                # 透過PNGをサポートするように設定する
                foreground_image = foreground_image.convert("RGBA")

                # 合成する画像を背景画像の中央に配置する
                background_image.alpha_composite(foreground_image, (start_pos+foreground_image.width*magic+magic, 0))

            # 合成した画像を保存する
            background_image.save('img/' + output_filename+'.png')

            if output_filename+'.png' in out_files:
                continue
        except Exception as e:
            print(e, file)

    outDict('cosdict.txt',cosdict)
    outDict('namedict.txt',namedict)



def main(rank, url, masters):
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
    buddy_fields = build_buddy_fields(parse_buddy_entries(buddy_table))
    name = name.replace('【ツイステ】', '')
    key = name + costume
    growtype = name_type_master[key] if name_type_master[key] else infer_growtype(rank, attr, HP, ATK)
    out_txt = (name
               + "\t" + costume
               + "\t" + rank
               + "\t" + attr
               + "\t" + str(name_base_hp_master[key] if name_base_hp_master[key] else base_hp)
               + "\t" + str(name_base_atk_master[key] if name_base_atk_master[key] else base_atk)
               + "\t" + str(name_hp_master[key] if name_hp_master[key] else HP)
               + "\t" + str(name_atk_master[key] if name_atk_master[key] else ATK)
               + "\t" + magic1
               + "\t" + magic2
               + "\t" + magic3
               + "\t" + buddy_fields['buddy1c']
               + "\t" + buddy_fields['buddy1s']
               + "\t" + buddy_fields['buddy1s_totsu']
               + "\t" + buddy_fields['buddy2c']
               + "\t" + buddy_fields['buddy2s']
               + "\t" + buddy_fields['buddy2s_totsu']
               + "\t" + buddy_fields['buddy3c']
               + "\t" + buddy_fields['buddy3s']
               + "\t" + buddy_fields['buddy3s_totsu']
               + "\t" + "\t" + "\t" + "\t" + "\t"
               + growtype
               ).replace(' ', '').replace('（', '(').replace('）', ')').replace('＆', '&')

    return out_txt

def get_img(title, exists_files):

    filename = title.replace('/','')+'アイコン.jpg'
    # 条件にマッチするすべてのリンクを探す
    try:
        
        # if filename in exists_files:
        #     return
        time.sleep(1)
        url = "https://twst.wikiru.jp/attach2/696D67_" + filename.encode('utf-8').hex().rstrip().upper() + ".jpg"
        r = requests.get(url)
        if 200 != r.status_code:
            return
        path = 'get/' + filename
        image_file = open(path, 'wb')
        image_file.write(r.content)
        image_file.close()
    except:
        pass

def get_list(rank):
    url = "https://twst.wikiru.jp/?cmd=list"
    result = requests.get(url)
    data_all = BeautifulSoup(result.text, 'html.parser')
    url_list = []
    
    files = glob.glob("get/*")
    exists_files = set()
    for file in files:
        try:
            sp = file.split('/')[-1]
            exists_files.add(sp.replace('get/',''))
        except:
            pass
    for link in data_all.find_all('a'):
        if link.text.startswith(rank) and link.text.endswith('】'):
            url_list.append('https://twst.wikiru.jp/?' + link.text)
            get_img(link.text, exists_files)
    return url_list
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



if __name__ == '__main__':
    masters = make_type_dict(STATUS_TABLE_URL)
    output = []
    count = 0
    # 実装日情報を取得
    implementation_dates = get_implementation_dates()
    for rank in ('SSR','SR','R'):
        url_all_list = get_list(rank)
        for cur_url in url_all_list:
            try:
                time.sleep(1)
                output.append(str(count) + '\t' + main(rank, cur_url, masters) + '\t' + cur_url)
                count+=1
            except Exception as e:
                print(e,cur_url)
    print(output)
    with open("charadata.tsv", "w", encoding='UTF-8') as f:
        for out in output:
            f.write(f"{out}\n")
    makeicon(implementation_dates)
