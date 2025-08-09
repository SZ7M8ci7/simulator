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

def create_composite_image(chara_data, filename, size, magic_icon_size):
    max_magic = 2
    if chara_data['rare'] == 'SSR':
        max_magic = 3
    
    background_image = Image.open(filename).convert("RGBA")
    background_image_resized = background_image.resize((size, size))
    start_pos = background_image_resized.width - max_magic * magic_icon_size - (max_magic - 1)
    
    for magic in range(max_magic):
        magic_atr_key = f"magic{magic+1}atr"
        foreground_image = Image.open(f"{chara_data[magic_atr_key]}.png")
        foreground_image = foreground_image.convert("RGBA")
        
        if foreground_image.size != (magic_icon_size, magic_icon_size):
            foreground_image = foreground_image.resize((magic_icon_size, magic_icon_size))
        
        background_image_resized.alpha_composite(foreground_image, (start_pos + magic_icon_size * magic + magic, 0))
    
    return background_image_resized

def make_png_icon(chara_data, filename):
    try:
        composite_image = create_composite_image(chara_data, filename, 60, 12)
        composite_image.save('img/' + chara_data['name'] +'.png')
    except Exception as e:
        print(e, filename)

def make_webp_icon(chara_data, filename):
    try:
        composite_image = create_composite_image(chara_data, filename, 80, 16)
        composite_image.save('img/' + chara_data['name'] +'.webp', 'WEBP', quality=85)
    except Exception as e:
        print(e, filename)

if __name__ == '__main__':
    
    namedict = getDict('namedict.txt')
    cosdict = getDict('cosdict.txt')
    img_files = glob.glob("img/*")
    exists_png_files = set()
    exists_webp_files = set()
    for file in img_files:
        try:
            sp = file.split('/')[-1]
            filename = sp.replace('img/','').replace('img\\','')
            if filename.endswith('.png'):
                exists_png_files.add(filename)
            elif filename.endswith('.webp'):
                exists_webp_files.add(filename)
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
            output_png_filename = output_filename+'.png'
            output_webp_filename = output_filename+'.webp'
            
            # PNG画像の存在チェックと生成
            if output_png_filename not in exists_png_files:
                make_png_icon(chara_data_dict[output_filename], file)
            
            # WebP画像の存在チェックと生成
            if output_webp_filename not in exists_webp_files:
                make_webp_icon(chara_data_dict[output_filename], file)
        except Exception as e:
            print(e, file)

        