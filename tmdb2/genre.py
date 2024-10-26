import requests
import pandas as pd
import streamlit as st

TMDB_BASE_URL = "https://api.themoviedb.org/3"
TMDB_API_KEY = "312b27b45aa8ea633a041adb1f7276ff"

data = pd.read_csv('tmdb2/top_100.csv')

def get_movie_poster(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

def recommend_movies_by_user_genre(selected_genre, movies_df, top_n=30):
    movies_df['genres'] = movies_df['genres'].fillna('')
    if movies_df['genres'].dtype == object:
        movies_df['genres'] = movies_df['genres'].apply(lambda x: x.split(',') if isinstance(x, str) else [])

    filtered_movies = movies_df[movies_df['genres'].apply(lambda genres: selected_genre in genres)]
    recommended_movies = filtered_movies.sort_values(by='rating', ascending=False).head(top_n)
    return recommended_movies

def main():
    selected_genre = st.selectbox("Select a genre to get movie recommendations:", options=["Action", "Comedy", "Drama", "Horror", "Romance", "Science Fiction", "Thriller", "Family", "Crime", "Fantasy"])

    if st.button("Get Recommendations"):
        recommended_movies = recommend_movies_by_user_genre(selected_genre, data)

        st.subheader(f"Top {len(recommended_movies)} Movies in {selected_genre} Genre")
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


