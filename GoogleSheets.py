import gspread

Gsheet = "KPIs Labs"

import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import configparser


def connect():
    config = configparser.ConfigParser()
    config.read('config/config.txt')
    json_key_fle = config.get('Google Sheet', 'json_key')
    file_to_read = config.get('Google Sheet', 'KPIs_file_id')
    json_key = json.load(open(json_key_fle)) # json credentials you downloaded earlier
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope) # get email and key from creds
    file = gspread.authorize(credentials) # authenticate with Google
    sheet = file.open_by_key(file_to_read).sheet1
    return sheet

def save(sheet, last_sprint_failed_challenges_count, lab):

    sheet.update_cell(7, 2, )

sheet = connect()
print(sheet.cell(1, 1).value)
