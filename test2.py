# Import necessary libraries
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import MultiLabelBinarizer, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# 1. Connect to PostgreSQL Database and Fetch Data
engine = create_engine('postgresql://postgres:Eggroll%4012@localhost:5432/movies_db')
query_movies = "SELECT movie_id, title, genre, imdb_rating, release_year FROM movies"
query_user_movies = "SELECT movie_title FROM usermovies WHERE user_id = (SELECT user_id FROM users WHERE username = 'ryan')"

# Fetch the data
df_movies = pd.read_sql(query_movies, engine)
user_movies = pd.read_sql(query_user_movies, engine)

# 2. Preprocessing Data
# Assuming 'genre' column contains a string of comma-separated genres (e.g., "Action, Comedy")
df_movies['genre'] = df_movies['genre'].apply(lambda x: x.split(','))  # Convert genre to list of genres

# One-Hot Encoding for genre using MultiLabelBinarizer to handle multiple genres
mlb = MultiLabelBinarizer()
genre_encoded = mlb.fit_transform(df_movies['genre'])
genre_df = pd.DataFrame(genre_encoded, columns=mlb.classes_)

# Append the genre encoding to the original dataframe
df_movies = pd.concat([df_movies, genre_df], axis=1)

# Standardizing rating and release year
scaler = StandardScaler()
df_movies['rating_scaled'] = scaler.fit_transform(df_movies[['imdb_rating']])
df_movies['release_year_scaled'] = scaler.fit_transform(df_movies[['release_year']])

# 3. Create Feature Matrix (genre, rating, release year)
features = df_movies.drop(columns=['movie_id', 'title', 'genre', 'imdb_rating', 'release_year'])

# 4. Compute Cosine Similarity
cosine_sim = cosine_similarity(features, features)

# 5. Recommendation Function
def get_user_recommendations(user_movies, cosine_sim=cosine_sim, top_n=5):
    # Get the indices of the movies the user has watched
    user_movie_titles = user_movies['movie_title'].tolist()
    
    # Get the indices of the movies in the 'movies' DataFrame
    user_movie_indices = [df_movies[df_movies['title'] == title].index[0] for title in user_movie_titles if title in df_movies['title'].values]
    
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
