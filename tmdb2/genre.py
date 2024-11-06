import requests
import pandas as pd
import streamlit as st
import time
import ast

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = st.secrets["tmdb"]["TMDB_API_KEY"]
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

def safe_eval_genres(genre_str):
    try:
        if pd.isna(genre_str):
            return []
        if isinstance(genre_str, str):
            # Remove any leading/trailing whitespace and check if it starts with [
            genre_str = genre_str.strip()
            if genre_str.startswith('['):
                return ast.literal_eval(genre_str)
            else:
                return [g.strip() for g in genre_str.split(',') if g.strip()]
        return []
    except:
        return []

def recommend_movies_by_user_genre(selected_genre, data, top_n=30):
    # Debug: Print data info
    st.write("Data Info:", data.info())
    
    # Make sure genres column exists
    if 'genres' not in data.columns:
        st.error("The 'genres' column is missing in the CSV file.")
        return pd.DataFrame()
    
    # Show sample of raw genres data
    st.write("Raw genres sample:", data['genres'].head())
    
    # Process genres
    data['genres_list'] = data['genres'].apply(safe_eval_genres)
    
    # Show processed genres
    st.write("Processed genres sample:", data['genres_list'].head())
    
    # Convert selected genre to lowercase for comparison
    selected_genre_lower = selected_genre.lower()
    
    # Filter movies
    filtered_movies = data[data['genres_list'].apply(
        lambda genres: any(selected_genre_lower in g.lower() for g in genres)
    )]
    
    # Debug: Show number of filtered movies
    st.write(f"Number of movies found for genre '{selected_genre}': {len(filtered_movies)}")
    
    # Sort by rating and get top N
    recommended_movies = filtered_movies.sort_values(by='rating', ascending=False).head(top_n)
    return recommended_movies

def main():
    st.title("Movie Recommendations by Genre")
    
    # Debug: Show initial data
    st.write("Total number of movies in dataset:", len(data))
    
    selected_genre = st.selectbox(
        "Select a genre to get movie recommendations:", 
        options=["Action", "Comedy", "Drama", "Horror", "Romance", 
                "Science Fiction", "Thriller", "Family", "Crime", "Fantasy"]
    )
    
    if st.button("Get Recommendations"):
        if 'recommended_movies' in st.session_state:
            del st.session_state['recommended_movies']
        recommended_movies = recommend_movies_by_user_genre(selected_genre, data)
        st.session_state['recommended_movies'] = recommended_movies
        st.session_state['selected_genre'] = selected_genre
        st.write(f"Recommendations loaded for genre: {selected_genre}")
    
    if 'recommended_movies' in st.session_state:
        recommended_movies = st.session_state['recommended_movies']
        st.subheader(f"Top {len(recommended_movies)} Movies in {st.session_state['selected_genre']} Genre")
        
        if len(recommended_movies) == 0:
            st.warning("No movies found for the selected genre. Please try another genre.")
            return
            
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