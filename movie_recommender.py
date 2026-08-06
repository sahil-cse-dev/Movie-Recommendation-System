import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# Load movie dataset
movies = pd.read_csv("data/movies.csv")


# Combine genre and description
movies["features"] = movies["genre"] + " " + movies["description"]


# Convert text into numerical vectors
vectorizer = TfidfVectorizer(stop_words="english")
feature_matrix = vectorizer.fit_transform(movies["features"])


# Calculate similarity between all movies
similarity_matrix = cosine_similarity(feature_matrix)


def recommend_movies(movie_title, number_of_recommendations=5):

    # Find the movie
    movie_matches = movies[
        movies["title"].str.lower() == movie_title.lower()
    ]

    if movie_matches.empty:
        return []

    movie_index = movie_matches.index[0]

    # Get similarity scores for selected movie
    similarity_scores = list(
        enumerate(similarity_matrix[movie_index])
    )

    # Sort from most similar to least similar
    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    # Get top recommendations
    recommendations = []

    for index, score in similarity_scores[1:number_of_recommendations + 1]:
        recommendations.append(movies.iloc[index]["title"])

    return recommendations