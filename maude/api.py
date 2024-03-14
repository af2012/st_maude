import requests
import pandas as pd
from .report import MAUDEReport
from .util import parse_date
from datetime import datetime, timedelta

BASE_URL = 'https://api.fda.gov/device/event.json'
API_KEY = 'Wf2Sd79fZ5pPEe9e6Z9idXaGUhTnkdWDGoag8cLI'

def fetch_data(search: str) -> pd.DataFrame:
    resp = requests.get(f'{BASE_URL}?search=mdr_text="{search}"&sort=date_of_event:desc&limit={999}', headers={
        'Authorization': f'Basic {API_KEY}'
    })
    if resp.status_code == 200:
        return pd.DataFrame(resp.json()['results'])
    return pd.DataFrame()


def fetch_trends_dataA() -> pd.DataFrame:
    start_date = (datetime.now() - timedelta(days=30)).date()
    end_date = datetime.now().date()
    resp = requests.get(f'{BASE_URL}?sort=date_of_event:desc&limit={999}', headers={
        'Authorization': f'Basic {API_KEY}'
    })
    if resp.status_code == 200:
        df = pd.DataFrame(resp.json()['results'])
        reports = []
        for i, report in df.iterrows():
            date_of_event = parse_date(str(report['date_of_event']))
            if date_of_event < start_date or date_of_event > end_date or report['event_type'].lower() == 'malfunction':
                df = df.drop(index=i)
        for _, jsonReport in df.iterrows():
            reports.append(MAUDEReport(jsonReport))
        problems = {}
        for report in reports:
            for problem in report.product_problems:
                if problem in problems:
                    problems[problem] += 1
                else:
                    problems[problem] = 1
        return problems
    return {}

def fetch_trends_dataB() -> pd.DataFrame:
    start_date = (datetime.now() - timedelta(days=90)).date()
    end_date = (datetime.now() - timedelta(days=30)).date()
    resp = requests.get(f'{BASE_URL}?sort=date_of_event:desc&limit={999}', headers={
        'Authorization': f'Basic {API_KEY}'
    })
    if resp.status_code == 200:
        df = pd.DataFrame(resp.json()['results'])
        reports = []
        for i, report in df.iterrows():
            date_of_event = parse_date(str(report['date_of_event']))
            if date_of_event < start_date or date_of_event > end_date or report['event_type'].lower() == 'malfunction':
                df = df.drop(index=i)
        for _, jsonReport in df.iterrows():
            reports.append(MAUDEReport(jsonReport))
        problems = {}
        for report in reports:
            for problem in report.product_problems:
                if problem in problems:
                    problems[problem] += 1
                else:
                    problems[problem] = 1
        return problems
    return {}
