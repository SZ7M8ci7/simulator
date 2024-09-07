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

def makeicon():
    cosdict = getDict('cosdict.txt')
    namedict = getDict('namedict.txt')
    charadict = getCharaDict('charadata.tsv',namedict,cosdict)
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

            input_file = 'index.html'

            with open(input_file, 'r',encoding='UTF-8') as file:
                # ファイルを1行ずつ読み込み、処理を行う
                lines = file.readlines()
                for i in range(len(lines)):
                    if name+'バースデー追加エリア' in lines[i] and 'birth' in cosdict[cos]:
                        lines[i] = make_html(namedict[name],cosdict[cos])+'\n' + lines[i]
                        break
                    elif name+'部活追加エリア' in lines[i] and 'club' in cosdict[cos]:
                        lines[i] = make_html(namedict[name],cosdict[cos])+'\n' + lines[i]
                        break
                    elif name+rank+'追加エリア' in lines[i]:
                        lines[i] = make_html(namedict[name],cosdict[cos])+'\n' + lines[i]
                        break

            # 処理結果を同一ファイルに書き込む
            with open(input_file, 'w',encoding='UTF-8') as file:
                file.writelines(lines)
        except Exception as e:
            print(e, file)

    outDict('cosdict.txt',cosdict)
    outDict('namedict.txt',namedict)

def make_html(name,cos):
    eng = name + '_' + cos
    out_html = '    <a href="#" rel="modal:close" onclick="gtag(\'event\', \'click\', {\'event_category\': \'chara\', \'event_label\':\'' + eng + '\', \'value\':\'1\'});changeImg(\''+eng+'\')"><img src="img/'+eng+'.png"></a>'
    return out_html


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
            magic1 = txt[str_index:end_index].strip()
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
            magic2 = txt[str_index:end_index].strip()
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
            magic3 = txt[str_index:end_index].strip()
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
                    buddies[buddies_num] = cell.get_text()
                    buddies_num+=1
    name = name.replace('【ツイステ】', '')
    out_txt = (name
               + "\t" + costume
               + "\t" + rank
               + "\t" + attr
               + "\t" + str(name_base_hp_master[name+costume])
               + "\t" + str(name_base_atk_master[name+costume])
               + "\t" + str(name_hp_master[name+costume] if name_hp_master[name+costume] else HP)
               + "\t" + str(name_atk_master[name+costume] if name_atk_master[name+costume] else ATK)
               + "\t" + magic1
               + "\t" + magic2
               + "\t" + magic3
               + "\t" + '\t'.join(buddies)
               + "\t" + "\t" + "\t" + "\t" + "\t"
               + name_type_master[name+costume]
               ).replace(' ', '').replace('（', '(').replace('）', ')').replace('＆', '&')

    return out_txt

def get_img(title, exists_files):

    filename = title.replace('/','')+'アイコン.jpg'
    # 条件にマッチするすべてのリンクを探す
    try:
        time.sleep(1)
        url = "https://twst.wikiru.jp/attach2/696D67_" + filename.encode('utf-8').hex().rstrip().upper() + ".jpg"
        r = requests.get(url)
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




if __name__ == '__main__':
    masters = make_type_dict('https://twst.wikiru.jp/?%E3%82%AB%E3%83%BC%E3%83%89%E6%88%90%E9%95%B7%E7%8E%87')
    output = []
    count = 0
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
    makeicon()
