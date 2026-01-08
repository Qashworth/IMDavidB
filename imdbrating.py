import streamlit as st
import requests
import pandas as pd
import numpy as np
import uuid
from datetime import date
import urllib.parse
import requests


@st.cache_resource
def get_connection():
    return st.connection('mysql', type='sql')

conn = get_connection()

# create query (exclude movie_id).
df = conn.query(
    'SELECT movie_title, thumbs_up, bomb, release_year, rating, run_time, genre, director, country, source_viewed, date_watched, oscar_nom, oscar_noms_category, num_oscar_noms, oscar_win, oscar_wins_category, num_oscar_wins FROM movies WHERE date_watched >= "2026-01-01";',
    ttl=600,
)

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