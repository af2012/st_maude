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

### Process search results
if full_query:
    for query in full_query.split():
        results = maudeApi.fetch_data(query)
        if results.empty:
            continue

        # sort by malfunction, injury, and death
        if 'jsonReports' in globals():
            for _, report in jsonReports.iterrows():  # noqa: F821
                results.loc[len(results.index)] = report
            jsonReports = results.sort_values(by='event_type', key=lambda x: x.map({'Malfunction': 0, 'Injury': 1, 'Death': 2}), ascending=False)
        else:
            jsonReports = results.sort_values(by='event_type', key=lambda x: x.map({'Malfunction': 0, 'Injury': 1, 'Death': 2}), ascending=False)

        for i, report in jsonReports.iterrows():
            date_of_event = parse_date(str(report['date_of_event']))
            if date_of_event < start_date or date_of_event > end_date:
                jsonReports = jsonReports.drop(index=i)
    
    if 'jsonReports' in globals():
        reports = []
        for id, jsonReport in jsonReports.iterrows():
            reports.append(MAUDEReport(jsonReport))

        date_chart = maudeCharts.generate_date_chart(reports)
        st.altair_chart(date_chart, use_container_width=True)

        event_data, event_chart = maudeCharts.generate_event_chart(reports)
        manufacturer_data, manufacturer_chart = maudeCharts.generate_manufacturer_chart(reports)

        event_chart_col, manufacturer_chart_col = st.columns(2)
        event_chart_col.altair_chart(event_chart)
        manufacturer_chart_col.altair_chart(manufacturer_chart)

        product_problems_data, product_chart = maudeCharts.generate_product_chart(reports)
        patient_problems_data, patient_chart = maudeCharts.generate_patient_chart(reports)
        
        product_chart_col, patient_chart_col = st.columns(2)
        product_chart_col.altair_chart(product_chart)
        patient_chart_col.altair_chart(patient_chart)

        st.header(f'{len(reports)} reports were found')

        death_counts = event_data['count'][0]
        st.write(f'{death_counts} were deaths')

        common_manufacturer = manufacturer_data['manufacturer_g1_name'].get(0, 'No Manufacturer Specified')
        common_manufacturer_count = manufacturer_data['count'].get(0, 0)
        st.write(f'{common_manufacturer_count} were from {common_manufacturer}')
        
        common_product_problem = product_problems_data['problem'].get(0, 'No Product Problem Specified')
        common_product_problem_count = product_problems_data['count'].get(0, 0)
        st.write(f'{common_product_problem_count} were from {common_product_problem}')
        
        common_patient_problem = patient_problems_data['problem'].get(0, 'No Patient Problem Specified')
        common_patient_problem_count = patient_problems_data['count'].get(0, 0)
        st.write(f'{common_patient_problem_count} were from {common_patient_problem}')
        st.write('<br />', unsafe_allow_html=True)

        common_sentences = []

        i = 0
        for report in reports:
            if i >= 10:
                break
            for sentence in report.text.split('.'):
                if full_query.lower() in sentence.lower():
                    common_sentences.append(sentence.strip().lower())
                    i += 1

        common_sentences = list(sorted(common_sentences, key=lambda x: len(x)))

        for subsentence in common_sentences:
            subwords = subsentence.lower().split()
            for sentence in common_sentences:
                if sentence == subsentence:
                    continue
                words = sentence.lower().split()
                count = 0
                for subword in subwords:
                    if subword in words:
                        count += 1
                
                ratio = count / len(subwords)
                if ratio > 0.9:
                    shorter = min([subsentence, sentence], key=lambda x: len(x))
                    if shorter in common_sentences:
                        common_sentences.remove(shorter)

        common_sentences = set(common_sentences)
        s = '#### List of common sentences:\n' if len(common_sentences) > 0 else 'No common sentences found'
        for common_sentence in common_sentences:
            common_sentence = escape(common_sentence)
            common_sentence = common_sentence.lower().replace(full_query, f'<span class="highlight">{full_query.upper()}</span>')
            for query_word in full_query.split():
                common_sentence = common_sentence.lower().replace(query_word, f'<span class="highlight">{query_word}</span>')
            s += f'- {common_sentence}\n'
        st.markdown(s, unsafe_allow_html=True)

        sort_by = st.selectbox('Sort', ('Default', 'Time'))

        filter_manufacturer = st.selectbox('Filter Manufacturer', ['No Filter'] + list(manufacturer_data['manufacturer_g1_name']))
        if filter_manufacturer != 'No Filter':
            new_reports = []
            for report in reports:
                if report.manufacturer == filter_manufacturer:
                    new_reports.append(report)
            reports = new_reports
        filter_event_type = st.selectbox('Filter Event Type', ['No Filter', 'Death', 'Injury', 'Malfunction'])
        if filter_event_type != 'No Filter':
            new_reports = []
            for report in reports:
                if report.event_type == EventType._member_map_[filter_event_type.upper()]:
                    new_reports.append(report)
            reports = new_reports

        filter_product_problem = st.selectbox('Filter Product Problem', ['No Filter'] + list(sorted(product_problems_data['problem'])))
        if filter_product_problem != 'No Filter':
            new_reports = []
            for report in reports:
                if filter_product_problem in report.product_problems:
                    new_reports.append(report)
            reports = new_reports
        
        filter_patient_problem = st.selectbox('Filter Patient Problem', ['No Filter'] + list(sorted(patient_problems_data['problem'])))
        if filter_patient_problem != 'No Filter':
            new_reports = []
            for report in reports:
                if filter_patient_problem in report.patient_problems:
                    new_reports.append(report)
            reports = new_reports

        if has_searched(st.session_state.full_query):
            num_results = st.slider('Number of results to show:', value=10, max_value=50, step=10)
            
        if len(reports) > 0:
            st.subheader(f'Currently {min(num_results, len(reports))} out of {len(reports)} shown')
            if st.button('Show all results'):
                num_results = len(reports) - 1
        
        ids = list(map(lambda x: x.id, reports))
        for i, jsonReport in jsonReports.iterrows():
            if jsonReport['mdr_report_key'] not in ids:
                jsonReports.drop(i)

        st.download_button('Export all results as .csv', jsonReports.to_csv(), f'maude-{full_query}.csv', mime='text/csv')
                
        xlsx = BytesIO()
        jsonReports.to_excel(xlsx)
        xlsx_data = xlsx.getvalue()
        xlsx.close()
        st.download_button('Export all results as Excel', xlsx_data, f'maude-{full_query}.xlsx', mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

        st.write('<hr />', unsafe_allow_html=True)

        for report in reports:
            report.sort_exist_val = process_sort_exist(report, full_query)

        if sort_by == 'Default':
            reports = list(sorted(reports, key=lambda x: x.sort_exist_val, reverse=True))
        elif sort_by == 'Time':
            reports = list(sorted(reports, key=lambda x: x.date, reverse=True))

        i = 0
        if len(jsonReports) < 1:
            st.write('No results found. Try:')
            st.markdown('- Checking for typos or misspelling\n- Increase your date range\n- Use less filters')
        for report in reports:
            if i >= num_results:
                break
            event_type = report.event_type
            date_of_event = report.date
            manufacturer_name = report.manufacturer
            text = report.combine_text(sep='\n')

            first = -1
            last = -1
            
            text = text.lower().replace(full_query, f'<span class="highlight">{full_query.upper()}</span>')
            for query_word in full_query.split():
                text = text.lower().replace(query_word, f'<span class="highlight">{query_word}</span>')
            
            finds = [m for m in re.finditer('(?=%s)(?!.{1,%d}%s)' % ('<span', 4, '<span'), text)]
            first = min(list(map(lambda x: x.start(), finds)) + [0])

            finds = [m for m in re.finditer('(?=%s)(?!.{1,%d}%s)' % ('/span>', 5, '/span>'), text)]
            last = max((list(map(lambda x: x.end(), finds))) + [-1])
            
            text = text[max(first-50, 0):min(last+50, len(text))]

            if event_type == EventType.MALFUNCTION:
                event_text = '<span class="malfunction event-text">Malfunction</span>'
            elif event_type == EventType.INJURY:
                event_text = '<span class="injury event-text">Injury</span>'
            else:
                event_text = '<span class="death event-text">Death</span>'

            st.write(event_text, unsafe_allow_html=True)
            st.write(f'{date_of_event}\n{manufacturer_name}')
            st.write(text.lower(), unsafe_allow_html=True)
            link = WEB_URL + str(report.id)
            st.write(f'[more details]({link})')

            st.write('<hr />', unsafe_allow_html=True)

            i += 1
    else:
        st.write('No results found. Try:')
        st.markdown('- Checking for typos or misspelling\n- Increase your date range\n- Use less filters')

st.markdown(f'''<div class='footer'>

<p>Copyright © 2024 {__author__}<br />Credits: {', '.join(__credits__)}</p>

</div>''', unsafe_allow_html=True)
    

