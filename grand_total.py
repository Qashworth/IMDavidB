import streamlit as st
import pandas as pd
import numpy as np
from sqlalchemy import text
from PIL import Image
import urllib.parse
import requests

def apply_emoji(df):
    emoji_map_oscar_win = {0: "", 1: "🏆"}
    emoji_map_oscar_nom = {0: "", 1: "✉️"}
    emoji_map_thumbs_up = {0: "", 1: "👍"}
    emoji_map_bomb = {0: "", 1: "💣"}
    if isinstance(df, pd.DataFrame):
        df = df.copy()
        if "oscar_win" in df.columns:
            df["oscar_win"] = df["oscar_win"].map(emoji_map_oscar_win).fillna("")
        if "oscar_nom" in df.columns:
            df["oscar_nom"] = df["oscar_nom"].map(emoji_map_oscar_nom).fillna("")
        if "thumbs_up" in df.columns:
            df["thumbs_up"] = df["thumbs_up"].map(emoji_map_thumbs_up).fillna("")
        if "bomb" in df.columns:
            df["bomb"] = df["bomb"].map(emoji_map_bomb).fillna("")
    return df

def create_api_requests():
    api_requests = []
    for m in range(len(df)):
        encoded_movie_title = urllib.parse.quote(df.loc[m, 'movie_title'])
        api_requests.append(f"https://api.imdbapi.dev/search/titles?query={encoded_movie_title}")
    return api_requests

def get_json_data(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch data. Status code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"An error occurred: {e}")
        return None

def get_imdb_ratings():
    ratings = []
    for url in create_api_requests():
        data = get_json_data(url)
        if data and "titles" in data and len(data["titles"]) > 0:
            ratings.append(data["titles"][0]["rating"]["aggregateRating"])
        else:
            ratings.append(None)
    return ratings

get_imdb_ratings()

left_co, cent_co, right_co = st.columns(3)
with left_co:
    st.title('IMDavidB')
    st.write('All movies screened:')
with cent_co:
    st.image("https://imdavidb2.s3.us-east-2.amazonaws.com/assets/cinema_wellman_logo.JPG", width=300)

# Initialize connection.
@st.cache_resource
def get_connection():
    return st.connection('mysql', type='sql')

conn = get_connection()

df = conn.query(
    'SELECT movie_title, thumbs_up, bomb, release_year, rating, run_time, genre, director, country, source_viewed, date_watched, oscar_nom, oscar_noms_category, num_oscar_noms, oscar_win, oscar_wins_category, num_oscar_wins FROM movies ORDER BY movie_title ASC;',
    ttl=600,
)

df.index = range(1, len(df) + 1)
df = apply_emoji(df)
df = 
st.dataframe(df)