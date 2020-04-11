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

def update_row(sheet, row, value, valid):
    sheet.update_cell(row, 10 , value)
    sheet.update_cell(row, 1, valid)


def read_row(sheet, row):
    return sheet.row_values(row)


def apply_bussines_model(row):
    cash_prediction = 0
    try:
        for element in row:
            cash_prediction += int(element)
        return cash_prediction
    except:
        cash_prediction = 0
        return cash_prediction

def is_valid(cash_prediction):
    if cash_prediction <= 0:
        return False
    else:
        return True

def main():
    sheet = connect()
    all_rows = sheet.get_all_values()
    all_rows.pop(0) # Remove column names
    for index, row in enumerate(all_rows):
        if row[0] != 'yes':
            row.pop(0)
            row.pop(-1)
            cash_prediction = apply_bussines_model(row)
            if is_valid(cash_prediction):
                processed = 'yes'
            else:
                processed = 'error'
            update_row(sheet, index + 2, cash_prediction, processed)

if __name__ == '__main__':
    main()