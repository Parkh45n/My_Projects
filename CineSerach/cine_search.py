import streamlit as st
import requests
import json
from PIL import Image
from io import BytesIO
import pandas as pd

# Set page configuration
st.set_page_config(
    page_title="CineSearch - Movie Explorer",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
        .main {
            background-color: #0E1117;
        }
        .title {
            color: #FF4B4B;
            text-align: center;
            font-size: 3.5em;
            margin-bottom: 0.5em;
        }
        .sidebar .sidebar-content {
            background-color: #1a1a1a;
        }
        .movie-card {
            background-color: #1a1a1a;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
        }
        .movie-title {
            color: #FF4B4B;
            font-size: 2em;
            margin-bottom: 0.2em;
        }
        .movie-info {
            color: #f0f2f6;
            font-size: 1.1em;
            margin-bottom: 0.5em;
        }
        .movie-plot {
            color: #d1d1d1;
            font-size: 1em;
            line-height: 1.6;
            margin-top: 1em;
        }
        .rating-badge {
            display: inline-block;
            background-color: #FF4B4B;
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-weight: bold;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .section-title {
            color: #FF4B4B;
            font-size: 1.5em;
            margin-top: 1em;
            margin-bottom: 0.5em;
            border-bottom: 2px solid #FF4B4B;
            padding-bottom: 5px;
        }
    </style>
""", unsafe_allow_html=True)

# API key and base URL
API_KEY = "bb724370"  # Replace with your actual OMDB API key
BASE_URL = "http://www.omdbapi.com/"

# App title
st.markdown('<h1 class="title">🎬 CineSearch</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: #f0f2f6;">Explore Movies with OMDB API</h3>', unsafe_allow_html=True)

# Sidebar for search and filters
with st.sidebar:
    st.markdown("## Search Filters")
    
    search_query = st.text_input("Search for a movie or TV show", value="", 
                                placeholder="e.g. The Dark Knight")
    
    search_type = st.selectbox("Type", ["movie", "series", "episode", ""], index=0)
    
    year = st.text_input("Year", value="", placeholder="e.g. 2010")
    
    if st.button("Search"):
        st.experimental_rerun()

# Function to fetch movie data
def get_movie_data(title, type_="", year=""):
    params = {
        "apikey": API_KEY,
        "t": title,
        "type": type_,
        "y": year,
        "plot": "full"
    }
    
    try:
        response = requests.get(BASE_URL, params=params)
        data = response.json()
        
        if data.get("Response") == "True":
            return data
        else:
            st.error(f"Error: {data.get('Error', 'Unknown error')}")
            return None
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return None

# Main content area
if search_query:
    movie_data = get_movie_data(search_query, search_type, year)
    
    if movie_data:
        # Create columns for poster and info
        col1, col2 = st.columns([1, 2])
        
        with col1:
            # Display movie poster
            if movie_data.get("Poster") and movie_data["Poster"] != "N/A":
                try:
                    response = requests.get(movie_data["Poster"])
                    img = Image.open(BytesIO(response.content))
                    st.image(img, use_container_width=True)
                except:
                    st.warning("Couldn't load poster image")
            else:
                st.warning("No poster available")
        
        with col2:
            # Display movie info
            st.markdown(f'<div class="movie-card">', unsafe_allow_html=True)
            
            st.markdown(f'<h1 class="movie-title">{movie_data.get("Title", "N/A")}</h1>', unsafe_allow_html=True)
            
            # Basic info line
            info_line = f"{movie_data.get('Year', 'N/A')} • {movie_data.get('Rated', 'N/A')} • {movie_data.get('Runtime', 'N/A')}"
            st.markdown(f'<p class="movie-info">{info_line}</p>', unsafe_allow_html=True)
            
            # Genres
            genres = movie_data.get("Genre", "N/A").split(", ")
            genres_html = "".join([f'<span class="rating-badge">{genre}</span>' for genre in genres])
            st.markdown(genres_html, unsafe_allow_html=True)
            
            # Ratings
            st.markdown('<p class="section-title">Ratings</p>', unsafe_allow_html=True)
            
            if "Ratings" in movie_data:
                ratings_df = pd.DataFrame(movie_data["Ratings"])
                # Display IMDb rating prominently
                imdb_rating = movie_data.get("imdbRating", "N/A")
                if imdb_rating != "N/A":
                    st.markdown(f'<p class="movie-info">IMDb: ⭐ {imdb_rating}/10</p>', unsafe_allow_html=True)
                
                # Display other ratings
                for rating in movie_data["Ratings"]:
                    st.markdown(f'<p class="movie-info">{rating["Source"]}: {rating["Value"]}</p>', unsafe_allow_html=True)
            else:
                st.markdown('<p class="movie-info">No ratings available</p>', unsafe_allow_html=True)
            
            # Additional info
            st.markdown('<p class="section-title">Details</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="movie-info"><strong>Director:</strong> {movie_data.get("Director", "N/A")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="movie-info"><strong>Writer:</strong> {movie_data.get("Writer", "N/A")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="movie-info"><strong>Actors:</strong> {movie_data.get("Actors", "N/A")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="movie-info"><strong>Language:</strong> {movie_data.get("Language", "N/A")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="movie-info"><strong>Country:</strong> {movie_data.get("Country", "N/A")}</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="movie-info"><strong>Awards:</strong> {movie_data.get("Awards", "N/A")}</p>', unsafe_allow_html=True)
            
            # Plot
            st.markdown('<p class="section-title">Plot</p>', unsafe_allow_html=True)
            st.markdown(f'<p class="movie-plot">{movie_data.get("Plot", "N/A")}</p>', unsafe_allow_html=True)
            
            # DVD/Box office info if available
            if movie_data.get("DVD") != "N/A" or movie_data.get("BoxOffice") != "N/A":
                st.markdown('<p class="section-title">Release & Box Office</p>', unsafe_allow_html=True)
                if movie_data.get("DVD") != "N/A":
                    st.markdown(f'<p class="movie-info"><strong>DVD Release:</strong> {movie_data.get("DVD", "N/A")}</p>', unsafe_allow_html=True)
                if movie_data.get("BoxOffice") != "N/A":
                    st.markdown(f'<p class="movie-info"><strong>Box Office:</strong> {movie_data.get("BoxOffice", "N/A")}</p>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display raw JSON data in expander for debugging
        with st.expander("View Raw API Response"):
            st.json(movie_data)
    else:
        st.warning("No results found. Try a different search.")
else:
    # Show welcome message when no search has been performed
    st.markdown("""
        <div style="text-align: center; margin-top: 5em;">
            <h3 style="color: #f0f2f6;">Search for a movie or TV show using the sidebar</h3>
            <p style="color: #d1d1d1;">Get detailed information including ratings, plot, cast, and more</p>
        </div>
    """, unsafe_allow_html=True)