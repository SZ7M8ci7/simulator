import gspread
from oauth2client.service_account import ServiceAccountCredentials

# 認証情報の読み込み
scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:\\Users\\K\\Downloads\\silken-buttress-304014-e70c848057bb.json', scope)
client = gspread.authorize(creds)

# スプレッドシートのURLとシート名を指定する
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1wBONE-poCXP-DTz107FEUSEqmUclGRiKjzX7lHuqNDM/edit#gid=1570231154'
sheet_name = 'シート1'

# スプレッドシートのデータを取得する
worksheet = client.open_by_url(spreadsheet_url).worksheet(sheet_name)
rows = worksheet.get_all_values()

# 取得したデータを処理する
furnitures = []
count = 0
for row in rows:
    print(row)