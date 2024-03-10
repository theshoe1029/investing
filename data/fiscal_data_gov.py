import pandas as pd
import requests
from io import StringIO

def treasury_rate(security_desc):
    res = requests.get('https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates?sort=-record_date&format=csv')
    df = pd.read_csv(StringIO(res.content.decode('utf-8')))
    return df.loc[df.security_desc == security_desc].iloc[0].avg_interest_rate_amt/100

def t_bill_rate():
    return treasury_rate('Treasury Bills')