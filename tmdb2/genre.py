import requests
import pandas as pd
import streamlit as st
import os
import time

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
data = pd.read_csv('tmdb2/top_100.csv')

def get_movie_poster(movie_id, retries=3, delay=5):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={TMDB_API_KEY}"
    for attempt in range(retries):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                poster_path = data.get('poster_path')
                if poster_path:
                    return f"https://image.tmdb.org/t/p/w500{poster_path}"
        except requests.ConnectionError:
            print(f"Connection error. Retrying in {delay} seconds...")
            time.sleep(delay)
    return None

def recommend_movies_by_user_genre(selected_genre, data, top_n=30):
    data['genres'] = data['genres'].fillna('')
    if data['genres'].dtype == object:
        data['genres'] = data['genres'].apply(lambda x: x.split(',') if isinstance(x, str) else [])
    filtered_movies = data[data['genres'].apply(lambda genres: selected_genre in genres)]
    recommended_movies = filtered_movies.sort_values(by='rating', ascending=False).head(top_n)
    return recommended_movies

def main():
    st.title("Movie Recommendations by Genre")
    selected_genre = st.selectbox("Select a genre to get movie recommendations:", 
                                options=["Action", "Comedy", "Drama", "Horror", "Romance", 
                                            "Science Fiction", "Thriller", "Family", "Crime", "Fantasy"])

    if st.button("Get Recommendations"):
        recommended_movies = recommend_movies_by_user_genre(selected_genre, data)
        st.session_state['recommended_movies'] = recommended_movies
        st.session_state['selected_genre'] = selected_genre 
        st.write(f"Recommendations loaded for genre: {selected_genre}")

    if 'recommended_movies' in st.session_state:
        recommended_movies = st.session_state['recommended_movies']
        st.subheader(f"Top {len(recommended_movies)} Movies in {st.session_state['selected_genre']} Genre")
        cols = st.columns(3)
        for index, row in recommended_movies.iterrows():
            poster_url = get_movie_poster(row['movie_id'])
            tmdb_link = f"https://www.themoviedb.org/movie/{row['movie_id']}"
            with cols[index % 3]:
                st.subheader(row['title'])
                st.subheader(f"Rating: {row['rating']:.1f}")
                if poster_url:
                    st.image(poster_url, caption=row['title'], use_column_width=True)
                    st.markdown(f"[View on TMDB]({tmdb_link})")
                else:
                    st.write("Poster: Not available")

if __name__ == "__main__":
    main()
