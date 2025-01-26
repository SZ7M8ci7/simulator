import collections
import itertools
import json

def main1():

    # JSONファイルのパス
    file_path = 'chara.json'

    # ファイルを開く
    with open(file_path, 'r', encoding='UTF-8') as file:
        # JSONデータを読み込む
        data = json.load(file)

    card_list = [row for row in data if row['rare'] in ('SR','SSR')]
    print(len(card_list))
    N = len(card_list)
    for com in itertools.combinations(card_list, 4):
        member = [c for c in com]
        buddy = 0
        member_name_set = {member[0]['chara'],member[1]['chara'],member[2]['chara'],member[3]['chara']}
        d = collections.defaultdict(int)
        for mem in member:
            if mem['buddy1c'] in member_name_set:
                buddy+=1
            else:
                d[mem['buddy1c']]+=1
            if mem['buddy2c'] in member_name_set:
                buddy+=1
            else:
                d[mem['buddy2c']]+=1

            if mem['buddy3c'] in member_name_set:
                buddy+=1
            else:
                d[mem['buddy3c']]+=1
        if buddy <= 6:
            continue
        for j in range(N):
            c = card_list[j]
            name = c['chara']
            tmp = len(member_name_set&{c['buddy1c'],c['buddy2c'],c['buddy3c']})

            if buddy+d[name]+tmp > 13:
                print(','.join(sorted([i.get('name') for i in member]+[c['name']])))
                raise Exception()


if __name__ == '__main__':
    main1()
