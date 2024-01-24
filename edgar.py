from gaap import US_GAAP_TAGS

import pandas as pd
from bs4 import BeautifulSoup
from collections import defaultdict
from datetime import datetime

import json
import os
import requests

def convert_decimal(tag: BeautifulSoup) -> float:
    n_decimal = int(tag['decimals'])
    if n_decimal > 0:
        return float(tag.text)
    else:
        return int(int(tag.text)*pow(10, n_decimal))

def npv(cash_flow: pd.Series, discount_rate: float) -> int:
    return sum([c/((1+discount_rate)**(t+1)) for t, c in enumerate(cash_flow)])

def get_cik(tkr: str) -> str:
    res = requests.get('https://www.sec.gov/include/ticker.txt', headers={'User-Agent': 'b2g'})
    tkr_to_cik = {l.split('\t')[0]: l.split('\t')[1] for l in res.text.split('\n')}
    return tkr_to_cik[tkr]

def get_company_facts(tkr: str) -> pd.DataFrame:
    cik = get_cik(tkr)
    cik_param = ''.join(['0']*(10-len(cik)))+cik
    res = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik_param}.json", headers={'User-Agent': 'b2g'})
    json_content = json.loads(res.content)
    gaap_content = json_content['facts']['us-gaap']
    data = {}
    for col in US_GAAP_TAGS:
        for tag in US_GAAP_TAGS[col]:
            if tag in gaap_content:
                supported_units = ['USD', 'shares', 'USD/shares']
                for unit in supported_units:
                    if unit in gaap_content[tag]['units']:
                        for entry in gaap_content[tag]['units'][unit]:
                            if 'frame' in entry:
                                frame = entry['frame']
                                if frame not in data:
                                    data[frame] = defaultdict(int)
                                data[frame][col] += entry['val']
    return pd.DataFrame(data=data)

BASE_GAAP_TAGS = {
    'us-gaap:Revenues'.lower(): 'Revenue',
    'us-gaap:SalesRevenueNet'.lower(): 'Revenue',
    'us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax'.lower(): 'Revenue',
    'us-gaap:CostOfGoodsAndServicesSold'.lower(): 'COGS',
    'us-gaap:GrossProfit'.lower(): 'Gross Profit',
    'us-gaap:ResearchAndDevelopmentExpense'.lower(): 'R&D',
    'us-gaap:SellingGeneralAndAdministrativeExpense'.lower(): 'SG&A',
    'us-gaap:OperatingExpenses'.lower(): 'Operating Expenses',
    'us-gaap:costsandexpenses': 'Operating Expenses',
    'us-gaap:NonoperatingIncomeExpense'.lower(): 'Interest Income',
    'us-gaap:IncomeLossFromContinuingOperationsBeforeIncomeTaxes'.lower(): 'Pretax Income',
    'us-gaap:IncomeTaxExpenseBenefit'.lower(): 'Taxes',
    'us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding'.lower(): 'Shares',
    'us-gaap:EarningsPerShareDiluted'.lower(): 'EPS',
    'us-gaap:marketingexpense': 'Sales and Marketing',
    'us-gaap:generalandadministrativeexpense': 'General Administrative',
    'us-gaap:otheroperatingincomeexpensenet': 'Other Operating Expenses (Income) Net',
    'us-gaap:operatingincomeloss': 'Operating Income',
    'us-gaap:investmentincomeinterest': 'Interest Income',
    'us-gaap:interestexpense': 'Interest Expense',
    'us-gaap:othernonoperatingincomeexpense': 'Other Income (Expense) Net',
    'us-gaap:nonoperatingincomeexpense': 'Total Non-Operating Income (Expense)',
    'us-gaap:incomelossfromcontinuingoperationsbeforeincometaxesminorityinterestandincomelossfromequityme': 'Pretax Income',
    'us-gaap:incometaxexpensebenefit': 'Taxes',
    'us-gaap:incomelossfromequitymethodinvestments': 'Equity-method investment activity, net of tax',
    'us-gaap:netincomeloss': 'Net income',
}

def get_context_ref_by_name(file_name: str, name: str) -> str:
    f = open(file_name)
    data = json.loads(f.read())
    f.close()
    for k in data['instance']:
        reports = data['instance'][k]['report']
        for report_id in reports:
            if reports[report_id]['shortName'].lower() == name.lower():
                return reports[report_id]['uniqueAnchor']['contextRef']
    return None

def get_report_data_by_ref(file_name: str, context_ref: str, unique_tags: dict) -> dict:
    f = open(file_name)
    xbrl = BeautifulSoup(f.read(), 'lxml')
    f.close()
    ctx = xbrl.find('context', attrs={'id': context_ref})
    start_date = ctx.find('period').find('startdate').text.strip()
    end_date = ctx.find('period').find('enddate').text.strip()
    data = {
        'start_date': datetime.strptime(start_date, '%Y-%m-%d'),
        'end_date': datetime.strptime(end_date, '%Y-%m-%d')
    }
    gaap_tags = {**BASE_GAAP_TAGS, **unique_tags}
    for tag in gaap_tags:
        entry = xbrl.find(tag, attrs={'contextref': context_ref})
        if entry != None:
            data[gaap_tags[tag]] = convert_decimal(entry)
    return data

def save_xbrl(xbrl_file_name: str, soup: BeautifulSoup) -> None:
    f = open(xbrl_file_name, 'w')
    f.write(soup.find_all('xbrl')[-1].prettify())
    f.close()

def save_meta_links(meta_file_name: str, soup: BeautifulSoup) -> None:
    f = open(meta_file_name, 'w')
    for doc in soup.find_all('document'):
        if doc.find('type').text.split('\n')[0] == 'JSON':
            f.write(doc.find('text').text.strip())
    f.close()

def get_docs(tkr: str, n_quarters: int, doc_types: list) -> None:
    cik = get_cik(tkr)
    print(f"got cik {cik} for ticker {tkr}")

    res = requests.get(f"https://www.sec.gov/Archives/edgar/data/{cik}", headers={'User-Agent': 'b2g'})
    soup = BeautifulSoup(res.content, 'html.parser')
    links = []
    for row in soup.table.find_all('tr'):
        link = row.find('a', href=True)['href']
        updated_date = datetime.strptime(row.find_all('td')[-1].contents[0], '%Y-%m-%d %H:%M:%S')
        delta = datetime.today()-updated_date
        if delta.days < n_quarters*120:
            links.append(link)

    for link in links:
        folder_name = link.split('/')[-1]
        file_name = f"{folder_name[:10]}-{folder_name[10:12]}-{folder_name[12:]}"
        header_file = f"{file_name}-index-headers"
        res = requests.get(f"https://www.sec.gov{link}/{header_file}.html", headers={'User-Agent': 'b2g'})
        file_data = res.text.split('\n')
        doc_type = file_data[5].split('>')[1]
        report_period = file_data[7].split('>')[1]
        doc_dir = f"edgar_data/{tkr}"

        if doc_type in doc_types:
            res = requests.get(f"https://www.sec.gov{link}/{file_name}.txt", headers={'User-Agent': 'b2g'})
            soup = BeautifulSoup(res.content, 'lxml')

            qtr_folder = str(pd.Series(datetime.strptime(report_period, '%Y%m%d')).dt.to_period('Q')[0])
            if qtr_folder not in os.listdir(doc_dir):
                print(f"storing {doc_type} doc: {file_name}")
                os.makedirs(f"{doc_dir}/{qtr_folder}")
                meta_file_name = f"{doc_dir}/{qtr_folder}/MetaLinks.json"
                save_meta_links(meta_file_name, soup)
                xbrl_file_name = f"{doc_dir}/{qtr_folder}/ReportData.xml"
                save_xbrl(xbrl_file_name, soup)