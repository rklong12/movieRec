# Import necessary libraries
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")

# 1. Connect to PostgreSQL Database and Fetch Data
DATABASE_URL = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
engine = create_engine(DATABASE_URL)

# Fetch all movies
query_movies = "SELECT movie_id, title, genre, imdb_rating, release_year FROM movies"
df_movies = pd.read_sql(query_movies, engine)

# Fetch movies watched by the user
query_user_movies = "SELECT movie_title FROM usermovies WHERE user_id = (SELECT user_id FROM users WHERE username = 'ryan')"
user_movies = pd.read_sql(query_user_movies, engine)

# 2. Preprocessing Data
# Ensure genre column is not null before splitting
df_movies['genre'] = df_movies['genre'].fillna("").apply(lambda x: x.split(','))

# One-Hot Encoding for genre using MultiLabelBinarizer to handle multiple genres
mlb = MultiLabelBinarizer()
genre_encoded = mlb.fit_transform(df_movies['genre'])
genre_df = pd.DataFrame(genre_encoded, columns=mlb.classes_)

# Append the genre encoding to the original dataframe
df_movies = pd.concat([df_movies, genre_df], axis=1)

# Standardizing rating and release year
scaler = StandardScaler()
df_movies['rating_scaled'] = scaler.fit_transform(df_movies[['imdb_rating']].fillna(0))
df_movies['release_year_scaled'] = scaler.fit_transform(df_movies[['release_year']].fillna(0))

# 3. Create Feature Matrix (genre, rating, release year)
features = df_movies.drop(columns=['movie_id', 'title', 'genre', 'imdb_rating', 'release_year'])

# Ensure there are enough movies before computing similarity
if features.shape[0] > 1:
    cosine_sim = cosine_similarity(features, features)
else:
    cosine_sim = None  # Not enough movies to compute similarity

# 4. Recommendation Function
def get_user_recommendations(user_movies, cosine_sim=cosine_sim, top_n=5):
    if cosine_sim is None:
        return ["Not enough data to generate recommendations"]

    # Get the indices of the movies the user has watched
    user_movie_titles = user_movies['movie_title'].tolist()
    
    # Get the indices of the movies in the 'movies' DataFrame
    user_movie_indices = [df_movies[df_movies['title'] == title].index[0] for title in user_movie_titles if title in df_movies['title'].values]

    if not user_movie_indices:
        return ["No valid movies found in the database for recommendations"]

    # Calculate the average cosine similarity score for the user's watched movies
    sim_scores = []
    for idx in user_movie_indices:
        sim_scores.extend(list(enumerate(cosine_sim[idx])))

    # Sort the movies based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # Get the top N similar movies (excluding movies the user has already watched)
    recommended_movies = []
    for movie in sim_scores:
        movie_idx = movie[0]
        movie_title = df_movies['title'].iloc[movie_idx]
        if movie_title not in user_movie_titles:
            recommended_movies.append(movie_title)
        if len(recommended_movies) == top_n:
            break
    
    return recommended_movies

# 6. Example Usage
recommended_movies = get_user_recommendations(user_movies)
print("Recommended Movies for Ryan:")
print(recommended_movies)
