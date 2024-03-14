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

st.text_input("Search query (try epipen, insulin pump)", key="full_query")
if st.button('Search', type="primary"):
    st.rerun()

full_query = st.session_state.full_query # retrieve full query from streamlit

#---- after user enters search ---#
if full_query:
    for query in full_query.split():
        results = maudeApi.fetch_data(query)

#---- check there are search results ---#
    if results.empty:
        st.write('No results found. Try:')
        st.markdown('- Checking for typos or misspelling\n- Increase your date range')
    else:
        st.write(results.shape[0])
        st.write(results)
    


st.markdown(f'''<div class='footer'>

<p>Copyright © 2024 {__author__}<br />Credits: {', '.join(__credits__)}</p>

</div>''', unsafe_allow_html=True)
    

