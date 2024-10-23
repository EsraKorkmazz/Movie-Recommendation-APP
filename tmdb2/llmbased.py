import asyncio
import aiohttp
import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables and configure API keys
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"

# Initialize OpenAI client
if not OPENAI_API_KEY:
    st.error("OpenAI API key is missing. Please check your .env file.")
    OPENAI_CLIENT = None
else:
    OPENAI_CLIENT = OpenAI(api_key=OPENAI_API_KEY)

class MovieRecommender:
    def __init__(self):
        if not TMDB_API_KEY:
            st.error("TMDB API key is missing. Please check your .env file.")
    
    async def get_recommendations(self, query: str) -> list[str]:
        """Get movie recommendations from OpenAI"""
        if not OPENAI_CLIENT:
            st.error("OpenAI client not initialized. Check your API key.")
            return []
            
        try:
            response = OPENAI_CLIENT.chat.completions.create(
                model="gpt-3.5-turbo",  # You can use gpt-4 if available
                messages=[
                    {"role": "system", "content": "You are a movie recommendation expert. Provide only movie titles without any additional text."},
                    {"role": "user", "content": f"List 10 movies that match these criteria: {query}. Just list the movie titles, one per line, without any additional text or numbering."}
                ]
            )
            return [title.strip() for title in response.choices[0].message.content.split('\n') if title.strip()]
        except Exception as e:
            st.error(f"Error getting recommendations: {str(e)}")
            return []

    async def fetch_movie_details(self, session: aiohttp.ClientSession, title: str) -> dict:
        """Fetch details for a single movie from TMDB"""
        if not title:
            return None
            
        try:
            # Search for movie
            search_url = f"{TMDB_BASE_URL}/search/movie"
            params = {
                "api_key": TMDB_API_KEY,
                "query": title,
                "language": "en-US"
            }
            
            async with session.get(search_url, params=params) as response:
                search_data = await response.json()
                
                if not search_data.get("results"):
                    return None
                    
                movie = search_data["results"][0]
                movie_id = movie["id"]
                
                # Get detailed movie information
                detail_url = f"{TMDB_BASE_URL}/movie/{movie_id}"
                params["append_to_response"] = "credits,reviews"
                
                async with session.get(detail_url, params=params) as response:
                    movie_data = await response.json()
                    
                    return {
                        "id": movie_id,
                        "title": movie_data["title"],
                        "poster_path": movie_data.get("poster_path"),
                        "vote_average": movie_data.get("vote_average"),
                        "overview": movie_data.get("overview", "No overview available."),
                        "release_date": movie_data.get("release_date"),
                        "genres": [genre["name"] for genre in movie_data.get("genres", [])],
                        "runtime": movie_data.get("runtime"),
                        "director": next((crew["name"] for crew in movie_data.get("credits", {}).get("crew", []) 
                                       if crew["job"] == "Director"), "Unknown")
                    }
                    
        except Exception as e:
            st.error(f"Error fetching movie details: {str(e)}")
            return None

    async def get_all_movie_details(self, titles: list[str]) -> list[dict]:
        """Fetch details for all recommended movies"""
        async with aiohttp.ClientSession() as session:
            tasks = [self.fetch_movie_details(session, title) for title in titles]
            results = await asyncio.gather(*tasks)
            return [movie for movie in results if movie is not None]

def display_movie_card(movie: dict):
    """Display a single movie card in the Streamlit interface"""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if movie.get('poster_path'):
            poster_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"
            st.image(poster_url, width=200)
        else:
            st.image("https://via.placeholder.com/200x300?text=No+Poster", width=200)
            
    with col2:
        movie_url = f"https://www.themoviedb.org/movie/{movie['id']}"
        st.markdown(f"### [{movie['title']}]({movie_url})")
        
        if movie.get('vote_average'):
            st.write(f"⭐ Rating: {round(movie['vote_average'], 1)}/10")
            
        if movie.get('release_date'):
            st.write(f"📅 Release Date: {movie['release_date']}")
            
        if movie.get('runtime'):
            st.write(f"⏱️ Runtime: {movie['runtime']} minutes")
            
        if movie.get('director'):
            st.write(f"🎬 Director: {movie['director']}")
            
        if movie.get('genres'):
            st.write("🎭 Genres: " + ", ".join(movie['genres']))
            
        if movie.get('overview'):
            st.write("📝 Overview:")
            st.write(movie['overview'])
            
    st.divider()

def main():
    st.set_page_config(page_title="Movie Recommender", page_icon="🎬", layout="wide")
    st.title("🎬 Movie Recommendation System")
    
    recommender = MovieRecommender()
    
    # User input
    query = st.text_input(
        "What kind of movie are you looking for?",
        placeholder="E.g.: Science fiction movies with time travel themes"
    )
    
    if query:
        with st.spinner('Finding perfect movies for you...'):
            # Get recommendations and movie details
            movie_titles = asyncio.run(recommender.get_recommendations(query))
            
            if movie_titles:
                movie_details = asyncio.run(recommender.get_all_movie_details(movie_titles))
                
                if movie_details:
                    st.success(f"Found {len(movie_details)} movies matching your criteria!")
                    for movie in movie_details:
                        display_movie_card(movie)
                else:
                    st.warning("Couldn't fetch details for the recommended movies. Please try again.")
            else:
                st.error("Couldn't get movie recommendations. Please try a different query.")

if __name__ == "__main__":
    main()