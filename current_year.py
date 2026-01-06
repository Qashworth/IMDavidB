import streamlit as st
import pandas as pd
import numpy as np
import uuid
from datetime import date
from sqlalchemy import text

get_uuid = str(uuid.uuid4())
emoji_map_oscar_win = {0: "", 1: "🏆"}
emoji_map_oscar_nom = {0: "", 1: "✉️"}
emoji_map_thumbs_up = {0: "", 1: "👍"}
emoji_map_bomb = {0: "", 1: "💣"}

def apply_emoji(df):
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

st.title('IMDavidB')
st.write('Movies screened so far this year:')

# Initialize connection.
conn = st.connection('mysql', type='sql')

# Perform query (exclude movie_id).
df = conn.query(
    'SELECT movie_title, thumbs_up, bomb, release_year, rating, run_time, genre, director, country, source_viewed, date_watched, oscar_nom, oscar_noms_category, num_oscar_noms, oscar_win, oscar_wins_category, num_oscar_wins FROM movies WHERE date_watched >= "2026-01-01";',
    ttl=600,
)
# use a placeholder so we can update the table after inserts
df_placeholder = st.empty()
if not df.empty:
    df.index = range(1, len(df) + 1)
df = apply_emoji(df)
df_placeholder.dataframe(df)
    
# Form allows us to receive user input without forcing a rerun
with st.sidebar.form("Add a New Movie:"):
    rating_list = ["G","PG","PG-13","R","NC-17","M","X","P","GP","NR","UR","AP"]
    genre_list = ["Mystery/Suspense/Thriller","Drama","Comedy","Foreign","Sci-Fi","Action","Fantasy","Horror","War","Family","Sports","Western","Documentary","Short","Musical","F"]

    movie_id = get_uuid
    movie_title = st.text_input("Movie Title", value="", max_chars=None, key="movie_title")
    thumbs_up = st.checkbox("👍", value=False, key="thumbs_up")
    bomb = st.checkbox("💣", value=False, key="bomb")
    release_year = st.number_input("Year Released", min_value=0, value=None, key="release_year")
    rating = st.selectbox("Rating", rating_list, key="rating")
    run_time = st.number_input("Run Time", min_value=0,value=None, key="run_time")
    genre = st.multiselect("Genre", genre_list, key="genre") 
    director = st.text_input("Director", value="", max_chars=None, key="director")
    country = st.text_input("Country", value="", max_chars=None, key="country")
    source_viewed = st.text_input("Source", value="", max_chars=None, key="source_viewed")
    date_watched = st.date_input("Date Watched", key="date_watched") 
    oscar_nom = st.checkbox("✉️", value=False, key="oscar_nom")
    num_oscar_noms = st.number_input("Number of Oscar noms", min_value=0, key="num_oscar_noms")
    oscar_noms_category = st.text_input("Oscar nomination categories", value="", max_chars=None, key="oscar_noms_category")
    oscar_win = st.checkbox("🏆", value=False, key="oscar_win")
    num_oscar_wins = st.number_input("Number of Oscar wins", min_value=0, key="num_oscar_wins")
    oscar_wins_category = st.text_input("Oscar win categories", value="", max_chars=None, key="oscar_wins_category")

    # Build new movie payload and submit on form submit
    submitted = st.form_submit_button('Add Movie')

    if submitted:
        # generate a fresh UUID per submission
        movie_id = str(uuid.uuid4())

        # normalize fields for SQL
        genre_str = ",".join(genre) if isinstance(genre, (list, tuple)) else str(genre)

        # Convert booleans to integers for DB
        def bool_to_int(v):
            return 1 if v else 0

        params = {
            "movie_id": movie_id,
            "movie_title": movie_title or None,
            "thumbs_up": bool_to_int(thumbs_up),
            "bomb": bool_to_int(bomb),
            "release_year": int(release_year) if release_year != "" and release_year is not None else None,
            "rating": rating or None,
            "run_time": int(run_time) if run_time is not None else None,
            "genre": genre_str or None,
            "director": director or None,
            "country": country or None,
            "source_viewed": source_viewed or None,
            "date_watched": date_watched or None,
            "oscar_nom": bool_to_int(oscar_nom),
            "oscar_noms_category": oscar_noms_category or None,
            "num_oscar_noms": int(num_oscar_noms) if num_oscar_noms is not None else 0,
            "oscar_win": bool_to_int(oscar_win),
            "oscar_wins_category": oscar_wins_category or None,
            "num_oscar_wins": int(num_oscar_wins) if num_oscar_wins is not None else 0,
        }

        insert_sql = text(
            """
            INSERT INTO movies (
                movie_id, movie_title, thumbs_up, bomb, release_year, rating, run_time, genre,
                director, country, source_viewed, date_watched, oscar_nom, oscar_noms_category, num_oscar_noms, oscar_win,
                oscar_wins_category, num_oscar_wins,
            ) VALUES (
                :movie_id, :movie_title, :thumbs_up, :bomb, :release_year, :rating, :run_time, :genre,
                :director, :country, :source_viewed, :date_watched, :oscar_nom, :oscar_noms_category, :num_oscar_noms, :oscar_win,
                :oscar_wins_category, :num_oscar_wins
            )
            """
        )

        try:
            with conn.session as s:
                s.execute(insert_sql, params)
                s.commit()
            st.success("Movie added.")

            # Refresh the dataframe display immediately (bypass cache)
            try:
                refreshed = conn.query(
                    'SELECT movie_title, thumbs_up, bomb, release_year, rating, run_time, genre, director, country, source_viewed, date_watched,  oscar_nom, oscar_noms_category, num_oscar_noms, oscar_win, oscar_wins_category, num_oscar_wins FROM movies WHERE date_watched >= "2026-01-01";',
                    ttl=0,
                )
                if not refreshed.empty:
                    refreshed.index = range(1, len(refreshed) + 1)
                refreshed = apply_emoji(refreshed)
                df_placeholder.dataframe(refreshed)
            except Exception as e:
                st.warning(f"Could not refresh dataframe: {e}")
        except Exception as e:
            st.error(f"Insert failed: {e}")
            st.write("SQL:", insert_sql)
            st.write("Params:", params)

