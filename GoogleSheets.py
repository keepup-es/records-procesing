import gspread

Gsheet = "KPIs Labs"

import json
import gspread
from oauth2client.client import SignedJwtAssertionCredentials
import configparser


def connect():
    config = configparser.ConfigParser()
    config.read('config/config.txt')
    json_key_fle = config.get('Keepup', 'json_key')
    file_to_read = config.get('Keepup', 'KPIs_file_id')
    json_key = json.load(open(json_key_fle)) # json credentials you downloaded earlier
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/spreadsheets', "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    credentials = SignedJwtAssertionCredentials(json_key['client_email'], json_key['private_key'].encode(), scope) # get email and key from creds
    file = gspread.authorize(credentials) # authenticate with Google
    sheet = file.open_by_key(file_to_read).sheet1
    return sheet

def update_row(sheet, row, value, valid):
    sheet.update_cell(row, 9 , value)
    sheet.update_cell(row, 10, valid)


def read_row(sheet, row):
    return sheet.row_values(row)

def business_model(num_empleados, facturacion_media_mensual, alquiler_mensual):
    recuperacion_actividad = [0.1, 0.3, 0.6]
    iva = 0.21
    avg_actividad = sum(recuperacion_actividad)/len(recuperacion_actividad)
    meses_proy = len(recuperacion_actividad)
    porcentaje_compras = 0.1
    porcentaje_gastos_generales = 0.17
    ERTE = True
    seg_social = 0.28
    salario_empleado = 970
    facturacion = sum([recup_mes*facturacion_media_mensual for recup_mes in recuperacion_actividad])
    alquiler = meses_proy * alquiler_mensual
    if ERTE:
        coste_empleados = (num_empleados*meses_proy*(1 + seg_social)*salario_empleado)*avg_actividad
    else:
        coste_empleados = (num_empleados*meses_proy*(1 + seg_social)*salario_empleado)

    gastos_generales_barata = {"telefono": 80, "gas": 75, "agua": 75, "electricidad": 200, "limpieza": 200,
                        "marketing": 100, "otros": 433}
    gastos_generales_media = {"telefono": 80, "gas": 75, "agua": 79, "electricidad": 210, "limpieza": 210,
                        "marketing": 105, "otros": 433}
    gastos_generales_cara = {"telefono": 80, "gas": 75, "agua": 83, "electricidad": 221, "limpieza": 221,
                        "marketing": 110, "otros": 433}
    if num_empleados <= 3:
        gastos_generales_dict = gastos_generales_barata
    elif 3 < num_empleados < 5:
        gastos_generales_dict = gastos_generales_media
    else:
        gastos_generales_dict = gastos_generales_cara
    gastos_generales = sum(gastos_generales_dict.values()) * meses_proy * (1-porcentaje_gastos_generales)
    compras = porcentaje_compras * facturacion
    liquidacion_iva = (-1 * (facturacion - (facturacion / (1+iva))) + (alquiler + compras + gastos_generales) - ((alquiler + compras + gastos_generales) / (1+iva)))
    if liquidacion_iva > 0:
        liquidacion_iva = 0
    caja_necesaria = facturacion - alquiler - coste_empleados - compras - gastos_generales - liquidacion_iva
    return caja_necesaria

def apply_bussines_model(row):
    cash_prediction = 0
    try:
        rental = int(row[7].replace("\"",""))
        if rental == 'property':
            rental = 0
        yearly = row[6]
        billing = int(row[5].replace("\"",""))
        if yearly == 'TRUE':
            billing = billing / 12
        employees = int(row[4].replace("\"",""))
        cash_prediction = business_model(employees, billing, rental)
        return cash_prediction
    except:
        cash_prediction = 0
        return cash_prediction

def is_valid(cash_prediction):
    if cash_prediction > 0:
        return False
    else:
        return True

def main():
    sheet = connect()
    all_rows = sheet.get_all_values()
    all_rows.pop(0) # Remove column names
    for index, row in enumerate(all_rows):
        if row[9] != 'yes':
            cash_prediction = apply_bussines_model(row)
            if is_valid(cash_prediction):
                processed = 'yes'
            else:
                processed = 'error'
            update_row(sheet, index + 2, cash_prediction, processed)

if __name__ == '__main__':
    #business_model(9, 8000, 1000)
    main()