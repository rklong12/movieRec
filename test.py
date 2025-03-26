# Import necessary libraries
import pandas as pd
from sqlalchemy import create_engine
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

# 1. Connect to PostgreSQL Database and Fetch Data
engine = create_engine('postgresql://postgres:Eggroll%4012@localhost:5432/movies_db')
query = "SELECT movie_id, title, genre, imdb_rating, release_year FROM movies"
df = pd.read_sql(query, engine)

# 2. Preprocessing Data
# Assuming 'genre' column contains a string of comma-separated genres (e.g., "Action, Comedy")
df['genre'] = df['genre'].apply(lambda x: x.split(','))  # Convert genre to list of genres

# One-Hot Encoding for genre using MultiLabelBinarizer to handle multiple genres
from sklearn.preprocessing import MultiLabelBinarizer
mlb = MultiLabelBinarizer()
genre_encoded = mlb.fit_transform(df['genre'])
genre_df = pd.DataFrame(genre_encoded, columns=mlb.classes_)

# Append the genre encoding to the original dataframe
df = pd.concat([df, genre_df], axis=1)

# Standardizing rating and release year
scaler = StandardScaler()
df['rating_scaled'] = scaler.fit_transform(df[['imdb_rating']])
df['release_year_scaled'] = scaler.fit_transform(df[['release_year']])

# 3. Create Feature Matrix (genre, rating, release year)
features = df.drop(columns=['movie_id', 'title', 'genre', 'imdb_rating', 'release_year'])

# 4. Compute Cosine Similarity
cosine_sim = cosine_similarity(features, features)

# 5. Recommendation Function
def get_recommendations(movie_title, cosine_sim=cosine_sim):
    # Get the index of the movie that matches the title
    idx = df[df['title'] == movie_title].index[0]
    
    # Get the pairwise similarity scores of all movies with the selected movie
    sim_scores = list(enumerate(cosine_sim[idx]))
    
    # Sort the movies based on similarity scores
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    # Get the top 5 most similar movies (excluding the first movie itself)
    sim_scores = sim_scores[1:6]
    
    # Get the movie indices
    movie_indices = [i[0] for i in sim_scores]
    
    # Return the top 5 most similar movies
    return df['title'].iloc[movie_indices]

# 6. Example Usage
recommended_movies = get_recommendations('The Matrix')
print("Recommended Movies:")
print(recommended_movies)
