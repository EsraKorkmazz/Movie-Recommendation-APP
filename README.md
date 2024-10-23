# Movie-Recommendation-APP
🎬 Movie Recommendation System

This is a comprehensive movie recommendation system that helps users discover movies using multiple approaches:

-Content-based filtering


-Genre-based recommendations


-LLM-based recommendations, where users can interact with an AI model to get personalized suggestions based on natural language input.
****

The app leverages machine learning techniques and data from the TMDB API, offering personalized movie recommendations in an intuitive and user-friendly way.

📌 Features

-Content-Based Movie Recommendation: Users can input a movie, and the system will recommend similar films based on the movie's description.

-Genre-Based Recommendations: Users can choose their favorite genre and get top-rated movies in that category.

-LLM-Based Recommendations: An AI-powered chatbot helps users get personalized recommendations based on natural language queries (e.g., "I want to watch a sci-fi movie with great visuals").

-TMDB Integration: Fetches real-time movie details, such as posters and ratings, using the TMDB API.

-Interactive UI: Built with Streamlit for easy navigation and interaction.

🛠️ Technologies Used

-Python: Core logic of the system.

-Pandas: Data manipulation and preprocessing.

-Scikit-learn: Machine learning algorithms like cosine similarity for content-based filtering.

-FuzzyWuzzy: For flexible movie title search using fuzzy matching.

-TMDB API: For fetching real-time movie data (posters, links, ratings).

-Streamlit: For building the interactive UI.

-Large Language Model (LLM): For AI-based movie recommendations based on natural language input.

```
📂 Project Structure

├── tmdb-api.ipynb          # Notebook for TMDB API integration
├── content_base.py         # Content-based recommendation logic
├── genre.py                # Genre-based recommendation logic
├── llmbased.py             # LLM-based recommendation logic
├── app.py                  # Main Streamlit app
├── top_100.csv             # Movie dataset used for recommendations
└── README.md               # This file
```

🧠 LLM-Based Recommendations

The LLM-based recommendation feature allows you to ask for movie suggestions using natural language queries. You can say things like:

"Recommend me a comedy with heartwarming moments."
"I want to watch an action movie set in space."
The AI will understand the context of your request and provide tailored recommendations.


🌐 TMDB API Key

This project requires a TMDB API key to fetch movie details. To use the app:

Create a TMDB account here.
Go to Settings -> API -> Create an API key.
Replace the TMDB_API_KEY in the code with your API key.
You can also explore the API integration by running the tmdb-api.ipynb notebook, which provides code examples for working with the TMDB API.

📊 Dataset

The dataset (top_100.csv) contains a collection of movies with their descriptions, genres, and other metadata. It can be updated or expanded to include more movies for improved recommendations.

📝 License

This project is open-source and available under the MIT License.
