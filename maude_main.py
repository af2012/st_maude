#!/usr/bin/env python
'''streamlit-learning.py: A MAUDE search application written in Streamlit'''

__author__ = 'Christopher Mattar'
__copyright__ = 'Copyright (C) 2024 Christopher Mattar'
__credits__ = ['Christopher Mattar', 'Allan Fong']
__license__ = 'GPLv3'
__version__ = '0.9'
__maintainer__ = 'Christopher Mattar'
__email__ = 'Allan.Fong@medstar.net'
__status__ = 'Development'

# This app allows users to search the maude database
import datetime
import re
import streamlit as st
import requests
import pandas as pd
import numpy as np

import maude.api as maudeApi
import maude.charts as maudeCharts
from maude.util import parse_date, process_sort_exist
from maude.report import MAUDEReport, EventType
from maude.trends import fetch_trends

st.set_page_config(layout='wide')

st.title('FDA MAUDE Search')

'''
This test app lets you search the FDA MAUDE free-text.

If you have any questions, please reach out to Allan.Fong@medstar.net
'''

# input fields
start_date = st.date_input(
    "Start Date",
    datetime.datetime.today() - datetime.timedelta(days=90)
)
end_date = st.date_input(
    "End Date",
    'today'
)

@st.cache_data
def has_searched(s):
    if s.strip() != '':
        return True
    return False

st.text_input("Search query (not case sensitive: try epipen, insulin pump, oxygen, oxygen AND tank, empty AND (oxygen OR o2) and tank)", key="full_query")
if st.button('Search', type="primary"):
    st.rerun()

user_input_1 = st.session_state.full_query # retrieve full query from streamlit

#---- after user enters search ---#
if user_input_1:
    user_input_4 = '('+'+'.join(user_input_1.split(' '))+')'   # split with space and combine with '+' and add ( )
    st.write(user_input_4)
    resp = requests.get('https://api.fda.gov/device/event.json?search=mdr_text.text:'+user_input_4+'&limit=10')
    
#---- check there are search results ---#
    if resp.status_code != 200:
        st.write('No results found. Try:')
        st.markdown('- Checking for typos or misspelling\n- Increase your date range')
    else:
        df = pd.DataFrame(resp.json()['results'])

        # shorten columns
        df = df[['report_number', 'event_type', 'type_of_report', 'date_received', 'device', 'product_problems', 'mdr_text']]
        # date_added, device_date_of_manufacturer, date_report, manufacturer_contact_address_1
        
        st.write('Number of search results: ' + str(df.shape[0]))
        st.write(df)

        ##############################
        # combine mdr_text
        df['combine_text'] = ''
        for i in range(0, df.shape[0]):
            temp_mdr_text = df.loc[i,'mdr_text']
            temp_combine_text = ''
            for t in temp_mdr_text:
                temp_combine_text = temp_combine_text + t['text'] + ' '
            df.loc[i,'combine_text'] = temp_combine_text
            
        ##############################
        # clip text (OR statement can be optimized)
        user_input_clean_1 = re.sub(r'(?i)\b(and|or)\b', '', user_input_1)
        user_input_clean_2 = re.sub(r'\(', '', user_input_clean_1)
        user_input_clean_3 = re.sub(r'\)', '', user_input_clean_2)
        user_input_clean_4 = re.sub(r'  ', ' ', user_input_clean_3)

        st.write(user_input_clean_4)

        user_tokens = user_input_4.split(' ')
        st.write(user_tokens)
        token = user_tokens[0] # always use first token to create base dataframe
        #re_pattern = re.compile(user_input_1, re.IGNORECASE)
        
        match_str_list = []
        text_list = list(df['combine_text'])
        for text in text_list:
            for m in re.finditer(token, text, re.IGNORECASE):
                ms = m.start()-70
                ms = 0 if ms<0 else ms
                me = m.end()+70
                t1 = text[ms:me]
                match_str_list.append(t1)
        match_str_df = pd.DataFrame({'clip':match_str_list})
        match_str_df[token] = 1
        
        if len(user_tokens)>1:
            for i in range(1, len(user_tokens)):
                temp_token = user_tokens[i]
                match_str_df[temp_token] = 0
                match_str_df.loc[match_str_df['clip'].str.contains(r'(?i)'+temp_token), temp_token] = 1
        match_str_df['matched_cnt'] = np.sum(match_str_df[user_tokens], axis=1)
        match_str_df['matched_per'] = np.round(match_str_df['matched_cnt']/len(user_tokens),2)
        match_str_df.sort_values(by=['matched_per'], ascending=False, inplace=True, ignore_index=True)

        st.write(match_str_df)


    


st.markdown(f'''<div class='footer'>

<p>Copyright © 2024 {__author__}<br />Credits: {', '.join(__credits__)}</p>

</div>''', unsafe_allow_html=True)
    

