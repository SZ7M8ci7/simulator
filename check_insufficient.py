import csv
import glob
import json
import time
from collections import defaultdict
from PIL import Image
from deep_translator import GoogleTranslator
import requests
from bs4 import BeautifulSoup
import random

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
def getCharaDict(path,namedict,cosdict):
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
        # 11,13,15 バディ1,2,3
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
        outdict['buddy1c'] = chara[12]
        outdict['buddy1s'] = chara[13]
        outdict['buddy2c'] = chara[14]
        outdict['buddy2s'] = chara[15]
        outdict['buddy3c'] = chara[16]
        outdict['buddy3s'] = chara[17]
        etc = ''
        magic1split = chara[9].split('&')
        for i in range(len(magic1split)):
            if i > 0:
                etc += magic1split[i]
                etc += '<br>'
        magic2split = chara[10].split('&')
        for i in range(len(magic2split)):
            if i > 0:
                if '[DUO]' not in magic2split[i]:
                    etc += magic2split[i]
                    etc += '<br>'
        magic3split = chara[11].split('&')
        for i in range(len(magic3split)):
            if i > 0:
                etc += magic3split[i]
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
            
        outdict['etc'] = etc
        outdict['rare'] = chara[3]
        outdict['growtype'] = chara[22]
        outdict['wikiURL'] = chara[-1]
        outdict['buff_count'] = buff_count
        outdict['debuff_count'] = debuff_count

        outlist.append(outdict)
        magicdict[outdict['name']] = [outdict['magic1atr'],outdict['magic2atr'],outdict['magic3atr']]

    with open('chara.json', 'w', encoding="utf-8") as f:
        json.dump(outlist, f, sort_keys=True, indent=4, ensure_ascii=False)

    return magicdict


def checkMagicPow(str):
    pow = ''
    if '2連撃' in str:
        pow += '連撃'
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

def main(rank, url):
    result = requests.get(url)
    data_all = BeautifulSoup(result.text, 'html.parser')
    count = 0
    for item in data_all.find_all("table", class_="style_table"):
        count += 1
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
    return buddies


if __name__ == '__main__':
    with open('chara.json') as f:
        di = json.load(f)
    for d in di:
        if d['buddy1c'] == '??':
            time.sleep(1)
            buddies = main(d['rare'], d['wikiURL'])
            d['buddy1c'] = buddies[0]
            d['buddy1s'] = buddies[1]
            d['buddy2c'] = buddies[2]
            d['buddy2s'] = buddies[3]
            d['buddy3c'] = buddies[4]
            d['buddy3s'] = buddies[5]
            
    with open('chara.json', 'wt') as f:
        json.dump(di, f, indent=4, ensure_ascii=False)
