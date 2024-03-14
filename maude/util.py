import datetime
from .report import MAUDEReport, EventType
from typing import List, Dict

# used to combine text in a report to a string
def combine_text(report: MAUDEReport, sep=' ') -> str:
    text = ''
    for mdr_text in report['mdr_text']:
        text += mdr_text['text'] + sep
    text = text.lower()
    return text

def process_sort_exist(report: MAUDEReport, full_query: str) -> int:
    return __prioritize_words_exist(report.text, full_query.split(), full_query)

def __prioritize_words_exist(text: str, target_words: List[str], full_query: str) -> int:
    found = 0
    for target_word in target_words:
        if target_word in text:
            found += 1
            found += 0.02 * text.count(target_word)
    if full_query in text:
        found += 10
    return found

def parse_date(date):
    if date != 'nan' and date is not None and len(date) <= 8:
        return datetime.datetime.strptime(date, "%Y%m%d").date()
    else:
        return datetime.datetime.now().date()

def parse_patient_problems(report):
    patient = report['patient']
    if len(patient) > 0:
        if 'patient_problems' in patient[0]:
            problems = patient[0]['patient_problems']
            if isinstance(problems, list):
                return problems
    return []

def parse_product_problems(report):
    product_problems = report['product_problems']
    if isinstance(product_problems, list):
        return product_problems
    return []

def count_event_types(reports: List[MAUDEReport], event_type: EventType) -> int: 
    count = 0
    for report in reports:
        if report.event_type == event_type:
            count += 1
    return count

def count_manufacturers(reports: List[MAUDEReport]) -> Dict[str,int]: 
    counts = {}
    for report in reports:
        if report.manufacturer not in counts:
            counts[report.manufacturer] = 1
        else:
            counts[report.manufacturer] += 1
    return counts
