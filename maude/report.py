from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import List

import pandas as pd


class EventType(Enum):
    DEATH = 0
    INJURY = 1
    MALFUNCTION = 2

# The purpose of this class is to encase the report DataFrame in an object to hide it when using __repr__ on MAUDEReport
class ReportJSON:
    def __init__(self, report):
        self.report = report
    
    def __getitem__(self, item):
        return self.report.__getitem__(item)
    
    def __repr__(self) -> str:
        return 'Report (JSON)'
    
    def __str__(self) -> str:
        return 'Report (JSON)'

@dataclass
class MAUDEReport:
    # declare variables
    __report: ReportJSON # report is hidden

    id: int
    date: datetime
    text: str
    event_type: EventType
    manufacturer: str
    patient_problems: List[str]
    product_problems: List[str]
    sort_exist_val: int = 0

    def __init__(self, report: pd.DataFrame):
        # utilities must be imported in here, and not in main code to fix circular import
        global combine_text, parse_date, parse_patient_problems, parse_product_problems
        from maude.util import (
            combine_text,
            parse_date,
            parse_patient_problems,
            parse_product_problems,
        )
        
        self.__report = ReportJSON(report) # encase DataFrame in ReportJSON

        # parse and set variables
        self.id = self.__report['mdr_report_key']
        self.date = parse_date(str(self.__report['date_of_event']))
        self.text = combine_text(self.__report)
        self.event_type = {'death': EventType.DEATH, 'injury': EventType.INJURY, 'malfunction': EventType.MALFUNCTION}[self.__report['event_type'].lower()]
        self.manufacturer = self.__report['manufacturer_g1_name']
        self.patient_problems = parse_patient_problems(self.__report)
        self.product_problems = parse_product_problems(self.__report)

    # utility function; used to extract all the text from a given report
    def combine_text(self, sep=' ') -> str:
        return combine_text(self.__report, sep=sep)
    
    # used as an accessor for self.__report
    def get_report(self):
        return self.__report.report
