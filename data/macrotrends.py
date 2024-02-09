from bs4 import BeautifulSoup
import pandas as pd

from datetime import datetime
import requests
import json

INCOME = 'income-statement'
BALANCE_SHEET = 'balance-sheet'
CASH_FLOW = 'cash-flow-statement'

def get_financial_statement(tkr: str, company_name: str, statement_type: str) -> pd.DataFrame:
    res = requests.get(f'https://www.macrotrends.net/stocks/charts/{tkr}/{str}/{statement_type}', headers={'User-Agent': 'b2g'})
    soup = BeautifulSoup(res.content, 'html.parser')

    scripts = soup.find_all('script', {'type': 'text/javascript'})
    data_script = str(list(filter(lambda s: 'originalData' in str(s), scripts))[0])
    data_line = list(filter(lambda l: 'originalData' in l and '=' in l, data_script.split('\n')))[0]
    json_data = json.loads('['+data_line.split('[')[-1][:-3]+']')

    data = {}
    for row in json_data:
        row_name = BeautifulSoup(row['field_name'], 'html.parser').text
        row_data = {}
        for k in row.keys():
            if k not in ['field_name', 'popup_icon'] and row[k] != '':
                year = datetime.strptime(k, '%Y-%m-%d').year
                row_data[year] = float(row[k])
        data[row_name] = row_data
    df = pd.DataFrame(data, dtype='float32').dropna(axis=1)
    return df

def init_model(tkr: str, company_name: str, path: str, to_excel: bool = False) -> None:
    income_statement = get_financial_statement(tkr, company_name, INCOME)
    balance_sheet = get_financial_statement(tkr, company_name, BALANCE_SHEET)
    cash_flow = get_financial_statement(tkr, company_name, CASH_FLOW)

    df = income_statement.join([balance_sheet, cash_flow]).transpose().sort_index(axis=1)

    if to_excel:
        df.to_excel(f'{path}/{tkr}.xlsx', float_format='%.2f', engine='openpyxl')
    else:
        df.to_csv(f'{path}/{tkr}.csv', float_format='%.2f')
