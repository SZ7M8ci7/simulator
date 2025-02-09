import glob
import json
import time
import requests

def get_img(filename):

    try:
        time.sleep(1)
        url = "https://twst.wikiru.jp/attach2/696D67_" + filename.encode('utf-8').hex().rstrip().upper()+".jpg"
        r = requests.get(url)
        if 200 != r.status_code:
            return
        path = 'get/' + filename
        image_file = open(path, 'wb')
        image_file.write(r.content)
        print(r.content)
        image_file.close()
    except:
        pass

if __name__ == '__main__':
    with open("chara.json", 'r') as file:
        data = json.load(file)
    files = glob.glob("get/*")
    exists_files = set()
    for file in files:
        try:
            sp = file.split('/')[-1]
            exists_files.add(sp.replace('get/','').replace('get\\',''))
        except:
            pass
    for d in data:
        filename = f"{d['rare']}{d['chara']}【{d['costume']}】アイコン.jpg"
        if filename not in exists_files:
            get_img(filename)
            break