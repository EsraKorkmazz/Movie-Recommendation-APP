import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from fuzzywuzzy import process
import requests
import streamlit as st

movies = pd.read_csv('tmdb2/top_100.csv')
movies['combined'] = movies['overview'] + movies['keywords']+ ' ' + movies['cast'] + ' ' + movies['crew']
movies['combined'] = movies['combined'].str.lower()
movies = movies.drop(columns =['overview','keywords','cast','crew','vote_count']).drop_duplicates(keep=False).dropna()

tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(movies['combined'])

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)

def clean_title(title):
    return title.lower().strip()

title_to_index = {clean_title(title): idx for idx, title in enumerate(movies['title'])}

TMDB_API_KEY = st.secrets["tmdb"]["TMDB_API_KEY"]
TMDB_BASE_URL = "https://api.themoviedb.org/3"

def get_movie_poster(movie_id):
    url = f"{TMDB_BASE_URL}/movie/{movie_id}?api_key={TMDB_API_KEY}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        poster_path = data.get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    return None

def get_content_based_recommendations(movie_title, n_recommendations=10):
    cleaned_title = clean_title(movie_title)
    closest_title, score = process.extractOne(cleaned_title, title_to_index.keys())
    if score < 90:  # Threshold
        return []
    
    idx = title_to_index[closest_title]
    sim_scores = list(enumerate(cosine_sim[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    sim_scores = sim_scores[1:n_recommendations + 1]
    movie_indices = [i[0] for i in sim_scores]
    
    recommended_movies = movies['title'].iloc[movie_indices].tolist()
    recommended_movies = recommended_movies.sort_values(by='rating', ascending=False)
    recommended_movie_ids = movies['movie_id'].iloc[movie_indices].tolist()
    
    recommendations_with_details = []
    for title, movie_id in zip(recommended_movies, recommended_movie_ids):
        link = f"https://www.themoviedb.org/movie/{movie_id}"
        poster_url = get_movie_poster(movie_id)
        recommendations_with_details.append((title, link, poster_url))
    
    return recommendations_with_details
if __name__ == "__main__":

    pass

