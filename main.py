import streamlit as st

pg = st.navigation([st.Page('current_year.py'), st.Page('grand_total.py')])
pg.run()

st.set_page_config(layout="wide", initial_sidebar_state="expanded")