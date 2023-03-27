import gspread
import os
from oauth2client.service_account import ServiceAccountCredentials

PROJECT_ID = os.getenv('PROJECT_ID').replace('\\n', '\n')
PRIVATE_KEY_ID = os.getenv('PRIVATE_KEY_ID').replace('\\n', '\n')
PRIVATE_KEY = os.getenv('PRIVATE_KEY').replace('\\n', '\n')
CLIENT_EMAIL = os.getenv('CLIENT_EMAIL').replace('\\n', '\n')
CLIENT_ID = os.getenv('CLIENT_ID').replace('\\n', '\n')
CLIENT_X509_CERT_URL = os.getenv('CLIENT_X509_CERT_URL').replace('\\n', '\n')

# 認証情報の読み込み
scope = ['https://www.googleapis.com/auth/spreadsheets.readonly']
client_credentials = {
  "type": "service_account",
  "project_id": PROJECT_ID,
  "private_key_id": PRIVATE_KEY_ID,
  "private_key": PRIVATE_KEY,
  "client_email": CLIENT_EMAIL,
  "client_id": CLIENT_ID,
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": CLIENT_X509_CERT_URL
}

creds = ServiceAccountCredentials._from_parsed_json_keyfile(client_credentials, scope, None, None)
client = gspread.authorize(creds)
# スプレッドシートのURLとシート名を指定する
spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1eYWEERQz3dL7lDFd5H63rWABSAci6LSX9xFB33eA9Yo/edit#gid=1570231154'
sheet_name = '家具データ'

# スプレッドシートのデータを取得する
worksheet = client.open_by_url(spreadsheet_url).worksheet(sheet_name)
rows = worksheet.get_all_values()

# 取得したデータを処理する
with open('data.csv', mode='w', encoding='UTF-8') as file:
    count = 0
    for row in rows:
        if len(row) == 0:
            continue
        if row[1] == '' or row[1] == '名前':
            continue
        line = ','.join([str(count)]+row[1:15]) + '\r\n'
        file.write(line)
        count+=1

sheet_name = '参照用素材数計算'

# スプレッドシートのデータを取得する
worksheet = client.open_by_url(spreadsheet_url).worksheet(sheet_name)
rows = worksheet.get_all_values()

# 取得したデータを処理する
with open('series.csv', mode='w', encoding='UTF-8') as file:
    count = 0
    for row in rows:
        count+=1
        if count <= 21:
            continue
        if 'シリーズ' in row[73]:
            line = ','.join(row[73:73+17]) + '\r\n'
            file.write(line)

with open('roomrank.csv', mode='w', encoding='UTF-8') as file:
    count = 0
    for row in rows:
        count+=1
        if count <= 21:
            continue
        if row[63].isdigit():
            line = ','.join(row[63:63+6]) + '\r\n'
            file.write(line)

