import streamlit as st

pg = st.navigation([st.Page('current_year.py'), st.Page('grand_total.py')])
pg.run()