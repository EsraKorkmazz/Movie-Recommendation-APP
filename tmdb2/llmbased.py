import asyncio
import aiohttp
import streamlit as st
from openai import OpenAI
import os
import dotenv
from dotenv import load_dotenv

dotenv.load_dotenv()

# API Yapılandırmaları
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
OPENAI_CLIENT = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_movie_recommendations(query):
    """OpenAI API kullanarak film önerileri al"""
    prompt = f"List 10 movies that match these criteria: {query}. Just list the movie titles, one per line, without any additional text or numbering."
    
    try:
        response = OPENAI_CLIENT.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a movie recommendation expert. Provide only movie titles without any additional text."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"OpenAI API hatası: {str(e)}")
        return None

async def fetch_movie_detail(session, title):
    """Get Movie Details"""
    if not title or len(title) < 2:
        return None
        
    search_url = f"{TMDB_BASE_URL}/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "language": "en-EN"
    }
    
    try:
        async with session.get(search_url, params=params) as response:
            data = await response.json()
            
            if data.get("results") and len(data["results"]) > 0:
                movie = data["results"][0]
                movie_id = movie["id"]
                
                detail_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
                detail_params = {
                    "api_key": TMDB_API_KEY,
                    "language": "en-EN"
                }
                
                async with session.get(detail_url, params=detail_params) as detail_response:
                    detail_data = await detail_response.json()
                    
                    return {
                        "id": movie_id,  # Include movie ID
                        "title": detail_data["title"],
                        "poster_path": detail_data.get("poster_path"),
                        "imdb_rating": detail_data.get("vote_average"),
                        "overview": detail_data.get("overview", "Açıklama bulunmuyor"),
                        "release_date": detail_data.get("release_date")
                    }
                    
    except Exception as e:
        st.write(f"Film detayları alınırken hata: {str(e)}")
    return None

async def get_movie_details(movie_titles):
    """Tüm filmler için detayları getir"""
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_movie_detail(session, title) for title in movie_titles]
        results = await asyncio.gather(*tasks)
        return [movie for movie in results if movie is not None]

def extract_movie_titles(text):
    """OpenAI yanıtından film başlıklarını ayıkla"""
    if not text:
        return []
    return [line.strip() for line in text.split('\n') if line.strip()]

def movie_recommendations_page():
    st.title("Film Öneri Sistemi")
    query = st.text_input("Film önerisi için kriterleri girin:")
    
    if query:
        with st.spinner('Film önerileri alınıyor...'):
            # OpenAI'dan önerileri al
            recommendations = asyncio.run(get_movie_recommendations(query))
            movie_titles = extract_movie_titles(recommendations)
            
            if movie_titles:
                # TMDB'den film detaylarını al
                movie_details = asyncio.run(get_movie_details(movie_titles))
                
                if movie_details:
                    st.write("\n### Önerilen Filmler:")
                    for movie in movie_details:
                        col1, col2 = st.columns([1, 2])
                        
                        with col1:
                            if movie.get('poster_path'):
                                poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
                                st.image(poster_url, width=200)
                            else:
                                st.write("Poster bulunamadı")
                                
                        with col2:
                            # Create a clickable title that links to the TMDB movie page
                            movie_url = f"https://www.themoviedb.org/movie/{movie['id']}"
                            st.markdown(f"### [{movie['title']}]({movie_url})")
                            st.write(f"IMDB Puanı: {round(movie['imdb_rating'], 1)}/10")
                            if movie.get('release_date'):
                                st.write(f"Yayın Tarihi: {movie['release_date']}")
                            st.write(movie['overview'])
                            
                else:
                    st.error("Film detayları alınamadı.")
            else:
                st.error("Film önerileri alınamadı.")

if __name__ == "__main__":
    movie_recommendations_page()
