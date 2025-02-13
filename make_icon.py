from collections import defaultdict
import glob
import json
from PIL import Image

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

def make_icon(chara_data, filename):
    try:
        max_magic = 2
        if chara_data['rare'] == 'SSR':
            max_magic = 3
        # 画像合成
        background_image = Image.open(filename).convert("RGBA")

        # 背景画像を60x60の正方形にリサイズする
        background_image = background_image.resize((60, 60))
        start_pos = background_image.width - max_magic*12 - (max_magic-1)
        for magic in range(max_magic):

            # 合成する画像を開く
            magic_atr_key = f"magic{magic+1}atr"
            foreground_image = Image.open(f"{chara_data[magic_atr_key]}.png")

            # 透過PNGをサポートするように設定する
            foreground_image = foreground_image.convert("RGBA")

            # 合成する画像を背景画像の中央に配置する
            background_image.alpha_composite(foreground_image, (start_pos+foreground_image.width*magic+magic, 0))

        # 合成した画像を保存する
        background_image.save('img/' + chara_data['name'] +'.png')

    except Exception as e:
        print(e, file)

if __name__ == '__main__':
    
    namedict = getDict('namedict.txt')
    cosdict = getDict('cosdict.txt')
    img_files = glob.glob("img/*")
    exists_files = set()
    for file in img_files:
        try:
            sp = file.split('/')[-1]
            filename = sp.replace('img/','').replace('img\\','')
            exists_files.add(filename)
        except Exception as e:
            print(e, file)

    with open("chara.json", 'r') as file:
        data = json.load(file)
    chara_data_dict = {}
    for d in data:
        chara_data_dict[d['name']] = d
    get_files = glob.glob("get/*")
    for file in get_files:
        try:
            sp = file.split('/')[-1]
            filename = sp.replace('get/','').replace('get\\','').replace('SSR','').replace('SR','').replace('R','').replace('】アイコン.jpg','')
            name_costume = filename.split('【')
            output_filename = namedict[name_costume[0]]+'_'+cosdict[name_costume[1]]
            output_filename_ext = output_filename+'.png'
            if output_filename_ext in exists_files:
                continue
            make_icon(chara_data_dict[output_filename], file)
        except Exception as e:
            print(e, file)

        