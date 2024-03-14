# This app allows users to search the maude database

import streamlit as st

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

st.text_input("Search query", key="full_query")
if st.button('Search', type="primary"):
    st.rerun()

full_query = st.session_state.full_query # retrieve full query from streamlit

