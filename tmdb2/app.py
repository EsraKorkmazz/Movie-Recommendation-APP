import streamlit as st
import pandas as pd
import requests 
from content_base import get_content_based_recommendations
from genre import main
from streamlit_option_menu import option_menu
import time
from llmbased import movie_recommendations_page
import os
import dotenv

dotenv.load_dotenv()

# Set page configuration
st.set_page_config(
    menu_items={
        "About": "For More Information\n" + "https://github.com/EsraKorkmazz/Movie-Recommendation-APP"
    }
)

def fetch_popular_movies(api_key):
    api_key = os.getenv("TMDB_API_KEY")
    url = f"https://api.themoviedb.org/3/movie/popular?api_key={api_key}&language=en-US&page=1"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()['results']
    else:
        st.error("Unable to fetch data from TMDb. Please try again later.")
        return []

st.set_page_config(page_title="Movie Recommendation System", layout="wide")

placeholder = st.empty()

with placeholder.container():
    st.markdown(
        """
        <div style='text-align: center;'>
            <h1>🎬 Movie Recommendation System Loading...</h1>
            <img src="https://media.giphy.com/media/3oKHWza7CiVMP0f41a/giphy.gif" style="width:600px;">
        </div>
        """, 
        unsafe_allow_html=True
    )

time.sleep(3)

placeholder.empty()

with st.sidebar:
    selected = option_menu(
        menu_title="Menu",  
        options=["Home Page", "Content Based Movie Recommendation", "Select by Genre", "Select by PROMPT"],  
        icons=["house", "film", "list-task"],  
        menu_icon="cast",  
        default_index=0,  
        styles={
            "container": {"padding": "5px", "background": "linear-gradient(to right,  #6a0dad, #0000ff)"},  
            "icon": {
                "color": "white", 
                "font-size": "25px", 
                "transition": "transform 0.3s ease-in-out"  
            },
            "nav-link": {
                "font-size": "18px", 
                "text-align": "left", 
                "margin": "10px", 
                "background-color": "#444444", 
                "color": "#fff", 
                "border-radius": "8px", 
                "box-shadow": "0px 4px 6px rgba(0, 0, 0, 0.1)",  
                "transition": "background-color 0.3s, transform 0.3s", 
                "--hover-color": "#ff9800"
            },
            "nav-link:hover": {
                "transform": "scale(1.1)",  
                "background-color": "linear-gradient(to right,  #6a0dad, #0000ff)", 
                "box-shadow": "0px 8px 10px rgba(0, 0, 0, 0.2)", 
            },
            "nav-link-selected": {
                "background-color": "#00c0f0", 
                "color": "white" 
            },
            "icon:hover": {
                "transform": "rotate(360deg)", 
                "color": "#ff9800" 
            }
        }
    )

if selected == "Home Page":
    st.title("🎬 Movie Recommendation System")
    st.markdown("Welcome to the **Movie Recommendation System!** Discover movies and explore different genres.")

    
    st.subheader("🍿 Currently Popular Movies")
    api_key = os.getenv("TMDB_API_KEY")
    popular_movies = fetch_popular_movies(api_key)

    if popular_movies:
        st.markdown("Here are some of the most popular movies right now:")
        num_columns = 3  
        cols = st.columns(num_columns)
        for idx, movie in enumerate(popular_movies):
            with cols[idx % num_columns]: 
                st.image(f"https://image.tmdb.org/t/p/w200{movie['poster_path']}", width=150)
                st.markdown(f"**{movie['title']}**")
                st.markdown(f"Rating: **{movie['vote_average']} / 10**")
                st.markdown(f"[View on TMDB](https://www.themoviedb.org/movie/{movie['id']})")

    else:
        st.warning("No popular movies found.")


elif selected == "Content Based Movie Recommendation":
    @st.cache_data
    def load_movie_titles():
        movies = pd.read_csv(r"top_100.csv")
        return movies['title'].tolist()

    movie_titles = load_movie_titles()

    st.subheader("🔍 Get Movie Recommendations")
    
    selected_movie = st.selectbox("Choose a movie from the list:", movie_titles)

    if st.button("Get Recommendations"):
        if selected_movie:
            with st.spinner("Fetching recommendations..."):
                recommendations = get_content_based_recommendations(selected_movie)
                if recommendations:
                    st.subheader(f"Recommendations for '{selected_movie}':")
                    cols = st.columns(2)
                    for i, (title, link, poster_url) in enumerate(recommendations):
                        with cols[i % 2]:
                            st.image(poster_url, width=200)
                            st.write(f"**{title}**")
                            st.write(f"[View on TMDB]({link})")
                else:
                    st.warning("No recommendations found for this movie.")
        else:
            st.warning("Please select a movie from the dropdown list.")


elif selected == "Select by Genre":
    st.subheader("🎭 Find Movies by Genre")
    st.write("Select your favorite genre to discover movies.")
    main()

elif selected == "Select by PROMPT":
    movie_recommendations_page()

# Sidebar help section
st.sidebar.markdown(
    """
    <div style="padding: 15px; border-radius: 10px; text-align: center; background: linear-gradient(to right,  #6a0dad, #0000ff);">
        <h3 style="color:white; text-align: center;">💡 Need Help? We've got you covered!</h3>
        <p style="font-size:16px; color:white;">To get movie recommendations, select a movie or genre from the sidebar.</p>
        <p style="font-size:16px; color:white;">If you have any questions, feel free to ask us! 🎬</p>
    </div>
    """,
    unsafe_allow_html=True
)
