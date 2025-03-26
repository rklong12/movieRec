import requests
import psycopg2
from psycopg2 import sql

import os
from dotenv import load_dotenv

# TMDb API Configuration
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
BASE_URL = "https://api.themoviedb.org/3"


DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# PostgreSQL Database Connection
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# Fetch Movie Data by Title
def get_movie_by_title(title):
    url = f'{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={title}&page=1'
    response = requests.get(url)
    data = response.json()
    
    if data['results']:
        return data['results'][0]  # Return the first result
    else:
        return None  # No movie found

# Genre Mapping
def get_genre_names(genre_ids):
    genre_dict = {
        28: "Action", 12: "Adventure", 16: "Animation", 35: "Comedy", 80: "Crime",
        99: "Documentary", 18: "Drama", 10751: "Family", 14: "Fantasy", 36: "History",
        27: "Horror", 10402: "Music", 9648: "Mystery", 10749: "Romance", 878: "Science Fiction",
        10770: "TV Movie", 53: "Thriller", 10752: "War", 37: "Western"
    }
    return [genre_dict.get(genre_id, "Unknown") for genre_id in genre_ids]

def get_movie_by_title(title):
    url = f'{BASE_URL}/search/movie?api_key={TMDB_API_KEY}&query={title}&page=1'
    response = requests.get(url)
    data = response.json()
    
    if data['results']:
        return data['results'][0]  # Return the first result
    else:
        return None  # No movie found

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

# Function to add a movie by title
def add_movie_by_title():
    # Get movie title from user
    title = input("Enter the title of the movie: ")

    # Fetch movie data from TMDb
    movie = get_movie_by_title(title)

    if movie:
        title = movie.get('title', "Unknown")
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

        # Commit changes
        conn.commit()

        print(f"Movie '{title}' has been added to the database!")
    else:
        print(f"Sorry, no movie found with the title '{title}'.")

# Call the function
add_movie_by_title()

# Close the database connection
cursor.close()
conn.close()