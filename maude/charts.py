import altair as alt
import pandas as pd

from .report import EventType, MAUDEReport
from .util import count_event_types, count_manufacturers
from typing import List, Tuple

# maximum number of entries any chart can hold
MAX_CHART = 20

def generate_date_chart(reports: List[MAUDEReport]) -> alt.Chart:
    date_dict = {}

    for report in reports:
        date = report.date
        if date in date_dict:
            date_dict[date] += 1
        else:
            date_dict[date] = 0
    
    date_keys = sorted(date_dict.items(), key=lambda x: x[1], reverse=True)
    dates = []
    date_counts = []

    i = 0
    for date, _ in date_keys:
        if i >= MAX_CHART:
            break
        count = date_dict[date]
        dates.append(pd.to_datetime(date, yearfirst=True))
        date_counts.append(count)
        i += 1
    
    date_data = pd.DataFrame({'date': dates, 'count': date_counts})
    date_chart =  alt.Chart(pd.DataFrame(date_data)) \
            .mark_line() \
            .encode(
                x=alt.X('date', title='Date of Event'),
                y=alt.Y('count', title='Count'),
            )
    return date_chart

def generate_event_chart(reports: List[MAUDEReport]) -> Tuple[pd.DataFrame, alt.Chart]: 
    event_data = pd.DataFrame({
        'event_type': ['Death', 'Injury', 'Malfunction'],
        'count': [count_event_types(reports, EventType.DEATH), count_event_types(reports, EventType.INJURY), count_event_types(reports, EventType.MALFUNCTION)]
    })

    event_chart = alt.Chart(pd.DataFrame(event_data))\
            .mark_bar()\
            .encode(
                x=alt.X('count', title='Count'),
                y=alt.Y('event_type', title='Event Type'),
                color=alt.Color('event_type', scale=alt.Scale(domain=['Death', 'Injury', 'Malfunction'], range=['red', 'orange', 'yellow']), legend=None)
                )\
            .interactive()
    return event_data, event_chart

def generate_manufacturer_chart(reports: List[MAUDEReport]) -> Tuple[pd.DataFrame, alt.Chart]: 
    manufacturer_value_counts = count_manufacturers(reports)
    manufacturer_dict = {}
    for manufacturer in manufacturer_value_counts:
        manufacturer_dict[manufacturer] = manufacturer_value_counts[manufacturer]
        
    manufacturer_keys = sorted(manufacturer_dict.items(), key=lambda x: x[1], reverse=True)
    manufacturer_names = []
    manufacturer_counts = []

    i = 0
    for name, _ in manufacturer_keys:
        if i >= MAX_CHART:
            break
        count = manufacturer_dict[name]
        manufacturer_names.append(name)
        manufacturer_counts.append(count)
        i += 1

    manufacturer_data = pd.DataFrame({'manufacturer_g1_name': manufacturer_names, 'count': manufacturer_counts})
    
    manufacturer_chart = alt.Chart(pd.DataFrame(manufacturer_data))\
            .mark_bar()\
            .encode(
                x=alt.X('count', title='Count'),
                y=alt.Y('manufacturer_g1_name', title='Manufacturer Name', axis=alt.Axis(labels=False), sort=None),
                color=alt.Color('manufacturer_g1_name', scale=alt.Scale(domain=manufacturer_data.sort_values(['count'])['manufacturer_g1_name'].tolist()), legend=None)
                )\
            .interactive()
    return manufacturer_data, manufacturer_chart

def generate_product_chart(reports: List[MAUDEReport]) -> Tuple[pd.DataFrame, alt.Chart]: 
    product_problems = {}

    for report in reports:
        for problem in report.product_problems:
            if problem in product_problems:
                product_problems[problem] += 1
            else:
                product_problems[problem] = 1
    
    product_problems_keys = sorted(product_problems.items(), key=lambda x: x[1], reverse=True)
    product_problems_problem = []
    product_problems_count = []

    i = 0
    for problem, _ in product_problems_keys:
        if i >= MAX_CHART:
            break
        count = product_problems[problem]
        product_problems_problem.append(problem)
        product_problems_count.append(count)
        i += 1
    
    product_problems_data = pd.DataFrame({'problem': product_problems_problem, 'count': product_problems_count})
    product_chart =  alt.Chart(pd.DataFrame(product_problems_data)) \
            .mark_bar()\
            .encode(
                x=alt.X('count', title='Count'),
                y=alt.Y('problem', title='Product Problem', axis=alt.Axis(labels=False), sort=None),
                color=alt.Color('problem', scale=alt.Scale(domain=product_problems_data.sort_values(['count'])['problem'].tolist()), legend=None)
            )\
            .interactive()
    return product_problems_data, product_chart

def generate_patient_chart(reports: List[MAUDEReport]) -> Tuple[pd.DataFrame, alt.Chart]: 
    patient_problems = {}

    for report in reports:
        for problem in report.patient_problems:
            if problem in patient_problems:
                patient_problems[problem] += 1
            else:
                patient_problems[problem] = 1
    
    patient_problems_keys = sorted(patient_problems.items(), key=lambda x: x[1], reverse=True)

    patient_problems_problem = []
    patient_problems_count = []

    i = 0
    for problem, _ in patient_problems_keys:
        if i >= MAX_CHART:
            break
        count = patient_problems[problem]
        patient_problems_problem.append(problem)
        patient_problems_count.append(count)
        i += 1
    
    patient_problems_data = pd.DataFrame({'problem': patient_problems_problem, 'count': patient_problems_count})
    patient_chart = alt.Chart(pd.DataFrame(patient_problems_data))\
            .mark_bar()\
            .encode(
                x=alt.X('count', title='Count'),
                y=alt.Y('problem', title='Patient Problem', axis=alt.Axis(labels=False), sort=None),
                color=alt.Color('problem', scale=alt.Scale(domain=patient_problems_data.sort_values(['count'])['problem'].tolist()), legend=None)
            )\
            .interactive()
    return patient_problems_data, patient_chart
