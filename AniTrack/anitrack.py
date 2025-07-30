import streamlit as st
import requests
from PIL import Image
from io import BytesIO
import pandas as pd
import json
import time
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="AniTrack – Anime Watchlist & Recommender",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
    <style>
        :root {
            --primary: #ff6584;
            --secondary: #6e45e2;
            --dark: #1a1a2e;
            --light: #f9f9f9;
        }
        .main {
            background-color: var(--dark);
        }
        .title {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            -webkit-background-clip: text;
            background-clip: text;
            color: transparent;
            text-align: center;
            font-size: 3.5em;
            margin-bottom: 0.5em;
        }
        .sidebar .sidebar-content {
            background-color: #16213e;
        }
        .anime-card {
            background-color: #16213e;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 20px 0 rgba(0,0,0,0.3);
            border-left: 5px solid var(--primary);
        }
        .anime-title {
            color: var(--primary);
            font-size: 2em;
            margin-bottom: 0.2em;
        }
        .anime-info {
            color: var(--light);
            font-size: 1.1em;
            margin-bottom: 0.5em;
        }
        .anime-synopsis {
            color: #d1d1d1;
            font-size: 1em;
            line-height: 1.6;
            margin-top: 1em;
        }
        .tag {
            display: inline-block;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 3px 10px;
            border-radius: 15px;
            font-weight: bold;
            margin-right: 10px;
            margin-bottom: 10px;
            font-size: 0.8em;
        }
        .section-title {
            color: var(--primary);
            font-size: 1.5em;
            margin-top: 1em;
            margin-bottom: 0.5em;
            border-bottom: 2px solid var(--primary);
            padding-bottom: 5px;
        }
        .watchlist-btn {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            border: none;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            margin-bottom: 10px;
        }
        .score-badge {
            display: inline-block;
            background-color: #4CAF50;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-weight: bold;
            margin-right: 10px;
        }
    </style>
""", unsafe_allow_html=True)

# Jikan API base URL
JIKAN_BASE_URL = "https://api.jikan.moe/v4"

# Initialize session state for watchlist
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = {
        'watching': [],
        'completed': [],
        'plan_to_watch': []
    }

# App title
st.markdown('<h1 class="title">🌸 AniTrack</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: var(--light);">Your Anime Watchlist & Recommender</h3>', unsafe_allow_html=True)

# Function to search anime
def search_anime(query):
    try:
        response = requests.get(f"{JIKAN_BASE_URL}/anime", params={"q": query, "limit": 5})
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {str(e)}")
        return []

# Function to get anime details
def get_anime_details(anime_id):
    try:
        response = requests.get(f"{JIKAN_BASE_URL}/anime/{anime_id}/full")
        response.raise_for_status()
        return response.json().get("data", {})
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching anime details: {str(e)}")
        return {}

# Function to get anime recommendations
def get_anime_recommendations(anime_id):
    try:
        response = requests.get(f"{JIKAN_BASE_URL}/anime/{anime_id}/recommendations")
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching recommendations: {str(e)}")
        return []

# Function to add to watchlist
def add_to_watchlist(anime_id, list_type):
    anime = next((a for a in st.session_state.search_results if a['mal_id'] == anime_id), None)
    if anime:
        # Remove from other lists first
        for lst in st.session_state.watchlist:
            st.session_state.watchlist[lst] = [a for a in st.session_state.watchlist[lst] if a['mal_id'] != anime_id]
        
        # Add to selected list
        st.session_state.watchlist[list_type].append({
            'mal_id': anime['mal_id'],
            'title': anime['title'],
            'image_url': anime['images']['jpg']['image_url'],
            'added_on': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        st.success(f"Added {anime['title']} to {list_type.replace('_', ' ')} list!")

# Function to remove from watchlist
def remove_from_watchlist(anime_id, list_type):
    st.session_state.watchlist[list_type] = [
        a for a in st.session_state.watchlist[list_type] if a['mal_id'] != anime_id
    ]
    st.success("Removed from your list!")

# Sidebar for search and watchlist
with st.sidebar:
    st.markdown("## 🔍 Search Anime")
    search_query = st.text_input("Enter anime title", key="search_query")
    
    if st.button("Search"):
        with st.spinner("Searching..."):
            st.session_state.search_results = search_anime(search_query)
    
    st.markdown("## 📋 My Watchlist")
    
    watchlist_tab1, watchlist_tab2, watchlist_tab3 = st.tabs(["Watching", "Completed", "Plan to Watch"])
    
    with watchlist_tab1:
        if st.session_state.watchlist['watching']:
            for anime in st.session_state.watchlist['watching']:
                st.image(anime['image_url'], width=100)
                st.write(anime['title'])
                if st.button(f"Remove from Watching", key=f"remove_watching_{anime['mal_id']}"):
                    remove_from_watchlist(anime['mal_id'], 'watching')
        else:
            st.write("No anime in this list yet.")
    
    with watchlist_tab2:
        if st.session_state.watchlist['completed']:
            for anime in st.session_state.watchlist['completed']:
                st.image(anime['image_url'], width=100)
                st.write(anime['title'])
                if st.button(f"Remove from Completed", key=f"remove_completed_{anime['mal_id']}"):
                    remove_from_watchlist(anime['mal_id'], 'completed')
        else:
            st.write("No anime in this list yet.")
    
    with watchlist_tab3:
        if st.session_state.watchlist['plan_to_watch']:
            for anime in st.session_state.watchlist['plan_to_watch']:
                st.image(anime['image_url'], width=100)
                st.write(anime['title'])
                if st.button(f"Remove from Plan to Watch", key=f"remove_plan_{anime['mal_id']}"):
                    remove_from_watchlist(anime['mal_id'], 'plan_to_watch')
        else:
            st.write("No anime in this list yet.")

# Main content area
tab1, tab2, tab3 = st.tabs(["🔍 Search Results", "📃 Anime Details", "🧠 Recommendations"])

with tab1:
    if 'search_results' in st.session_state and st.session_state.search_results:
        st.markdown(f"<h3>Search Results for '{search_query}'</h3>", unsafe_allow_html=True)
        
        for idx, anime in enumerate(st.session_state.search_results):
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if anime['images']['jpg']['image_url']:
                    st.image(anime['images']['jpg']['image_url'], use_container_width=True)
            
            with col2:
                st.markdown(f'<div class="anime-card">', unsafe_allow_html=True)
                st.markdown(f'<h2 class="anime-title">{anime["title"]}</h2>', unsafe_allow_html=True)
                
                # Basic info
                info_line = f"{anime.get('type', 'N/A')} • {anime.get('episodes', '?')} eps • {anime.get('status', 'N/A')}"
                st.markdown(f'<p class="anime-info">{info_line}</p>', unsafe_allow_html=True)
                
                # Score
                if anime.get('score'):
                    st.markdown(f'<span class="score-badge">⭐ {anime["score"]}/10</span>', unsafe_allow_html=True)
                
                # Genres
                genres = [genre['name'] for genre in anime.get('genres', [])]
                themes = [theme['name'] for theme in anime.get('themes', [])]
                all_tags = genres + themes
                tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in all_tags])
                st.markdown(tags_html, unsafe_allow_html=True)
                
                # Synopsis (shortened)
                synopsis = anime.get('synopsis', 'No synopsis available.')
                if len(synopsis) > 200:
                    synopsis = synopsis[:200] + "..."
                st.markdown(f'<p class="anime-synopsis">{synopsis}</p>', unsafe_allow_html=True)
                
                # Buttons to view details or add to watchlist
                col_btn1, col_btn2, col_btn3, col_btn4 = st.columns(4)
                with col_btn1:
                    if st.button(f"View Details", key=f"view_{anime['mal_id']}_{idx}"):
                        st.session_state.selected_anime_id = anime['mal_id']
                with col_btn2:
                    if st.button("Add to Watching", key=f"watching_{anime['mal_id']}_{idx}"):
                        add_to_watchlist(anime['mal_id'], 'watching')
                with col_btn3:
                    if st.button("Add to Completed", key=f"completed_{anime['mal_id']}_{idx}"):
                        add_to_watchlist(anime['mal_id'], 'completed')
                with col_btn4:
                    if st.button("Add to Plan to Watch", key=f"plan_{anime['mal_id']}_{idx}"):
                        add_to_watchlist(anime['mal_id'], 'plan_to_watch')
                
                st.markdown('</div>', unsafe_allow_html=True)
    elif 'search_results' in st.session_state:
        st.warning("No results found. Try a different search.")
    else:
        st.info("Enter an anime title in the sidebar to begin searching.")

with tab2:
    if 'selected_anime_id' in st.session_state:
        with st.spinner("Loading anime details..."):
            anime_details = get_anime_details(st.session_state.selected_anime_id)
        
        if anime_details:
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if anime_details['images']['jpg']['image_url']:
                    st.image(anime_details['images']['jpg']['image_url'], use_container_width=True)
                
                # Trailer
                if anime_details.get('trailer') and anime_details['trailer'].get('embed_url'):
                    st.markdown('<p class="section-title">Trailer</p>', unsafe_allow_html=True)
                    st.components.v1.html(f"""
                        <iframe width="100%" height="315" src="{anime_details['trailer']['embed_url']}" 
                        frameborder="0" allowfullscreen></iframe>
                    """, height=350)
            
            with col2:
                st.markdown(f'<div class="anime-card">', unsafe_allow_html=True)
                st.markdown(f'<h2 class="anime-title">{anime_details["title"]}</h2>', unsafe_allow_html=True)
                
                # Japanese title
                if anime_details.get('title_japanese'):
                    st.markdown(f'<p class="anime-info">{anime_details["title_japanese"]}</p>', unsafe_allow_html=True)
                
                # Basic info
                info_line = f"{anime_details.get('type', 'N/A')} • {anime_details.get('episodes', '?')} eps • {anime_details.get('status', 'N/A')}"
                st.markdown(f'<p class="anime-info">{info_line}</p>', unsafe_allow_html=True)
                
                # Aired date
                if anime_details.get('aired'):
                    aired_date = anime_details['aired'].get('string', 'N/A')
                    st.markdown(f'<p class="anime-info"><strong>Aired:</strong> {aired_date}</p>', unsafe_allow_html=True)
                
                # Score
                if anime_details.get('score'):
                    st.markdown(f'<p class="anime-info"><strong>Score:</strong> <span class="score-badge">{anime_details["score"]}/10</span> (from {anime_details.get("scored_by", "N/A")} users)</p>', unsafe_allow_html=True)
                
                # Rankings
                if anime_details.get('rank'):
                    st.markdown(f'<p class="anime-info"><strong>Rank:</strong> #{anime_details["rank"]} on MyAnimeList</p>', unsafe_allow_html=True)
                
                # Popularity
                if anime_details.get('popularity'):
                    st.markdown(f'<p class="anime-info"><strong>Popularity:</strong> #{anime_details["popularity"]} on MyAnimeList</p>', unsafe_allow_html=True)
                
                # Genres and themes
                st.markdown('<p class="section-title">Genres & Themes</p>', unsafe_allow_html=True)
                genres = [genre['name'] for genre in anime_details.get('genres', [])]
                themes = [theme['name'] for theme in anime_details.get('themes', [])]
                demographics = [demo['name'] for demo in anime_details.get('demographics', [])]
                all_tags = genres + themes + demographics
                tags_html = "".join([f'<span class="tag">{tag}</span>' for tag in all_tags])
                st.markdown(tags_html, unsafe_allow_html=True)
                
                # Synopsis
                st.markdown('<p class="section-title">Synopsis</p>', unsafe_allow_html=True)
                synopsis = anime_details.get('synopsis', 'No synopsis available.')
                st.markdown(f'<p class="anime-synopsis">{synopsis}</p>', unsafe_allow_html=True)
                
                # Background (if available)
                if anime_details.get('background'):
                    st.markdown('<p class="section-title">Background</p>', unsafe_allow_html=True)
                    st.markdown(f'<p class="anime-synopsis">{anime_details["background"]}</p>', unsafe_allow_html=True)
                
                # Relations (sequels, prequels, etc.)
                if anime_details.get('relations') and anime_details['relations']:
                    st.markdown('<p class="section-title">Related Anime</p>', unsafe_allow_html=True)
                    for relation in anime_details['relations']:
                        relation_list = ", ".join([entry['name'] for entry in relation['entry']])
                        st.markdown(f'<p class="anime-info"><strong>{relation["relation"]}:</strong> {relation_list}</p>', unsafe_allow_html=True)
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.error("Could not load anime details.")
    else:
        st.info("Select an anime from search results to view details.")

with tab3:
    if 'selected_anime_id' in st.session_state:
        with st.spinner("Loading recommendations..."):
            recommendations = get_anime_recommendations(st.session_state.selected_anime_id)
        
        if recommendations:
            st.markdown(f'<h3>Recommendations based on {st.session_state.search_results[0]["title"]}</h3>', unsafe_allow_html=True)
            
            # Display as grid
            cols = st.columns(3)
            for idx, rec in enumerate(recommendations[:6]):  # Show top 6 recommendations
                entry = rec['entry']
                with cols[idx % 3]:
                    st.markdown(f'<div class="anime-card">', unsafe_allow_html=True)
                    
                    if entry['images']['jpg']['image_url']:
                        st.image(entry['images']['jpg']['image_url'], use_container_width=True)
                    
                    st.markdown(f'<h4 class="anime-title">{entry["title"]}</h4>', unsafe_allow_html=True)
                    
                    # Count of recommendations
                    st.markdown(f'<p class="anime-info">{rec["votes"]} users recommended this</p>', unsafe_allow_html=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.warning("No recommendations found for this anime.")
    else:
        st.info("Select an anime from search results to get recommendations.")

# Save watchlist to JSON file (optional)
def save_watchlist():
    with open('anime_watchlist.json', 'w') as f:
        json.dump(st.session_state.watchlist, f)

# Load watchlist from JSON file (optional)
def load_watchlist():
    try:
        with open('anime_watchlist.json', 'r') as f:
            st.session_state.watchlist = json.load(f)
    except FileNotFoundError:
        pass

# Uncomment to enable JSON watchlist persistence
# load_watchlist()
# st.session_state.save_watchlist = save_watchlist