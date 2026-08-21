import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# LOAD DATASET
# ============================================================

movies = pd.read_csv(
    "data/tmdb_movies.csv"
)


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

movies.columns = (
    movies.columns
    .str.strip()
)


# ============================================================
# REQUIRED COLUMNS
# ============================================================

required_columns = [
    "title",
    "overview",
    "genre",
    "release_date",
    "vote_average",
    "popularity"
]

for column in required_columns:

    if column not in movies.columns:
        movies[column] = ""


# ============================================================
# CLEAN TITLE
# ============================================================

movies["title"] = (
    movies["title"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# CLEAN OVERVIEW
# ============================================================

movies["overview"] = (
    movies["overview"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# CLEAN GENRE
# ============================================================

movies["genre"] = (
    movies["genre"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# CLEAN RELEASE DATE
# ============================================================

movies["release_date"] = pd.to_datetime(
    movies["release_date"],
    errors="coerce"
)


# ============================================================
# REMOVE INVALID RELEASE DATES
# ============================================================

# Keep only movies from 1888 through 2026.

movies = movies[
    movies["release_date"].notna()
    & (
        movies["release_date"].dt.year >= 1888
    )
    & (
        movies["release_date"].dt.year <= 2026
    )
].copy()


# ============================================================
# CLEAN NUMERIC COLUMNS
# ============================================================

movies["vote_average"] = pd.to_numeric(
    movies["vote_average"],
    errors="coerce"
).fillna(0)


movies["popularity"] = pd.to_numeric(
    movies["popularity"],
    errors="coerce"
).fillna(0)


# ============================================================
# REMOVE MOVIES WITHOUT TITLE
# ============================================================

movies = movies[
    movies["title"].str.strip() != ""
].copy()


# ============================================================
# CREATE YEAR
# ============================================================

movies["year"] = (
    movies["release_date"]
    .dt.year
    .astype(int)
)


# ============================================================
# CREATE FEATURES
# ============================================================

movies["features"] = (
    movies["title"]
    + " "
    + movies["overview"]
    + " "
    + movies["genre"]
)


movies["features"] = (
    movies["features"]
    .fillna("")
    .astype(str)
    .str.strip()
)


# ============================================================
# RESET INDEX
# ============================================================

movies = movies.reset_index(
    drop=True
)


# ============================================================
# TF-IDF VECTORISATION
# ============================================================

vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=50000
)


feature_matrix = vectorizer.fit_transform(
    movies["features"]
)


# ============================================================
# RECOMMEND MOVIES
# ============================================================

def recommend_movies(
    movie_title,
    number_of_recommendations=5
):

    # --------------------------------------------------------
    # Find selected movie
    # --------------------------------------------------------

    movie_matches = movies[
        movies["title"]
        .str.lower()
        == movie_title.lower()
    ]


    if movie_matches.empty:
        return []


    # --------------------------------------------------------
    # Get movie index
    # --------------------------------------------------------

    movie_index = movie_matches.index[0]


    # --------------------------------------------------------
    # Get selected movie vector
    # --------------------------------------------------------

    movie_vector = feature_matrix[
        movie_index
    ]


    # --------------------------------------------------------
    # Calculate cosine similarity
    # --------------------------------------------------------

    similarity_scores = cosine_similarity(
        movie_vector,
        feature_matrix
    ).flatten()


    # --------------------------------------------------------
    # Sort by similarity
    # --------------------------------------------------------

    similar_indexes = (
        similarity_scores
        .argsort()[::-1]
    )


    recommendations = []


    # --------------------------------------------------------
    # Create recommendations
    # --------------------------------------------------------

    for index in similar_indexes:

        # Skip selected movie
        if index == movie_index:
            continue


        recommendations.append({

            "title":
                movies.iloc[index]["title"],

            "genre":
                movies.iloc[index]["genre"],

            "release_date":
                movies.iloc[index]["release_date"],

            "rating":
                movies.iloc[index]["vote_average"],

            "overview":
                movies.iloc[index]["overview"],

            "similarity":
                round(
                    similarity_scores[index] * 100,
                    2
                )
        })


        if len(recommendations) >= (
            number_of_recommendations
        ):
            break


    return recommendations


# ============================================================
# SORT MOVIES
# ============================================================

def get_movies_sorted(
    sort_order="newest",
    limit=50
):

    sorted_movies = movies.copy()


    # --------------------------------------------------------
    # Newest
    # --------------------------------------------------------

    if sort_order == "newest":

        sorted_movies = (
            sorted_movies
            .sort_values(
                by="release_date",
                ascending=False,
                na_position="last"
            )
        )


    # --------------------------------------------------------
    # Oldest
    # --------------------------------------------------------

    elif sort_order == "oldest":

        sorted_movies = (
            sorted_movies
            .sort_values(
                by="release_date",
                ascending=True,
                na_position="last"
            )
        )


    # --------------------------------------------------------
    # Highest Rating
    # --------------------------------------------------------

    elif sort_order == "rating":

        sorted_movies = (
            sorted_movies
            .sort_values(
                by="vote_average",
                ascending=False
            )
        )


    # --------------------------------------------------------
    # Most Popular
    # --------------------------------------------------------

    elif sort_order == "popular":

        sorted_movies = (
            sorted_movies
            .sort_values(
                by="popularity",
                ascending=False
            )
        )


    return sorted_movies.head(
        limit
    )


# ============================================================
# SEARCH MOVIES
# ============================================================

def search_movies(
    search_text,
    limit=20
):

    # --------------------------------------------------------
    # Empty search
    # --------------------------------------------------------

    if not search_text:

        return movies.head(
            limit
        )


    # --------------------------------------------------------
    # Search title
    # --------------------------------------------------------

    results = movies[
        movies["title"]
        .str.contains(
            search_text,
            case=False,
            na=False,
            regex=False
        )
    ]


    return results.head(
        limit
    )