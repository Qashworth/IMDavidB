import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import text

st.title('IMDavidB')
st.write('Grand total of movies screened:')

# Initialize connection.
conn = st.connection('mysql', type='sql')

df = conn.query(
    'SELECT movie_title, release_year, rating, run_time, genre, director, country, source_viewed, date_watched, oscar_win, oscar_wins_category, num_oscar_wins, oscar_nom, oscar_noms_category, num_oscar_noms FROM movies ORDER BY movie_title ASC;',
    ttl=600,
)

df.index = range(1, len(df) + 1)
st.dataframe(df)