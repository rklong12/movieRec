import requests
import psycopg2
from psycopg2 import sql

import os
from dotenv import load_dotenv


# Retrieve TMDB API Key
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = 'https://api.themoviedb.org/3'

# PostgreSQL connection setup
conn = psycopg2.connect(
    dbname="movies_db",
    user="postgres",
    password="Eggroll@12",
    host="localhost",  # Or your host
    port="5432"
)
cursor = conn.cursor()

# Get top-rated movies from TMDb (filter by region US)
def get_top_rated_movies(page=1):
    url = f'{BASE_URL}/movie/top_rated?api_key={TMDB_API_KEY}&page={page}&region=US'
    response = requests.get(url)
    return response.json()

# Genre Mapping
def get_genre_names(genre_ids):
    genre_dict = {
        28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
        99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
        27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
        10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
    }
    return [genre_dict.get(genre_id, "Unknown") for genre_id in genre_ids]

# Function to validate release year
def validate_year(year_str):
    try:
        return int(year_str[:4]) if year_str else None
    except ValueError:
        return None

# Fetch top 200 movies (10 pages, 20 movies per page)
movies_data = []
for page in range(1, 11):
    data = get_top_rated_movies(page)
    movies_data.extend(data.get('results', []))  # Ensure it doesn't break on missing results

# Insert data into the database
for movie in movies_data:
    title = movie['title']
    imdb_rating = movie.get('vote_average', 0)  # Default to 0 if missing
    release_year = validate_year(movie.get('release_date', ""))  # Validate year
    genre_ids = movie.get('genre_ids', [])  # Ensure genre_ids is a list
    genres = ', '.join(get_genre_names(genre_ids)) if genre_ids else "Unknown"

    # Insert into movies table with duplicate protection
    insert_query = sql.SQL("""
        INSERT INTO movies (title, imdb_rating, release_year, genre)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (title) DO NOTHING;
    """)
    cursor.execute(insert_query, (title, imdb_rating, release_year, genres))

# Commit changes and close connection
conn.commit()
cursor.close()
conn.close()

print("Top 200 American movies inserted into the database!")