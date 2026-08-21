import os
import pandas as pd
import streamlit as st
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)


# ============================================================
# LOAD DATASET
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "movies_large.csv")


@st.cache_data
def load_movies():

    movies = pd.read_csv(DATA_PATH)

    # Clean column names
    movies.columns = movies.columns.str.strip()

    # Required columns
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

    # --------------------------------------------------------
    # TEXT CLEANING
    # --------------------------------------------------------

    movies["title"] = (
        movies["title"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    movies["overview"] = (
        movies["overview"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    movies["genre"] = (
        movies["genre"]
        .fillna("")
        .astype(str)
        .str.strip()
    )

    # --------------------------------------------------------
    # RELEASE DATE
    # --------------------------------------------------------

    movies["release_date"] = pd.to_datetime(
        movies["release_date"],
        errors="coerce"
    )

    # Only valid movie dates
    movies.loc[
        movies["release_date"].dt.year < 1888,
        "release_date"
    ] = pd.NaT

    movies.loc[
        movies["release_date"].dt.year > 2026,
        "release_date"
    ] = pd.NaT

    # --------------------------------------------------------
    # NUMERIC COLUMNS
    # --------------------------------------------------------

    movies["vote_average"] = pd.to_numeric(
        movies["vote_average"],
        errors="coerce"
    ).fillna(0)

    movies["popularity"] = pd.to_numeric(
        movies["popularity"],
        errors="coerce"
    ).fillna(0)

    # --------------------------------------------------------
    # REMOVE MOVIES WITHOUT TITLE
    # --------------------------------------------------------

    movies = movies[
        movies["title"].str.strip() != ""
    ]

    # --------------------------------------------------------
    # YEAR
    # --------------------------------------------------------

    movies["year"] = movies["release_date"].dt.year

    # --------------------------------------------------------
    # CLEAN GENRE
    # --------------------------------------------------------

    movies["genre"] = (
        movies["genre"]
        .replace("nan", "")
        .replace("None", "")
        .fillna("")
        .astype(str)
    )

    # --------------------------------------------------------
    # FEATURES FOR RECOMMENDATION
    # --------------------------------------------------------

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
    )

    # Reset index
    movies = movies.reset_index(drop=True)

    return movies


movies = load_movies()


# ============================================================
# TF-IDF MODEL
# ============================================================

@st.cache_resource
def create_model(features):

    vectorizer = TfidfVectorizer(
        stop_words="english",
        max_features=50000
    )

    matrix = vectorizer.fit_transform(features)

    return vectorizer, matrix


vectorizer, feature_matrix = create_model(
    movies["features"]
)


# ============================================================
# RECOMMENDATION FUNCTION
# ============================================================

def recommend_movies(movie_title, number_of_recommendations=5):

    matches = movies[
        movies["title"].str.lower() == movie_title.lower()
    ]

    if matches.empty:
        return pd.DataFrame()

    movie_index = matches.index[0]

    movie_vector = feature_matrix[movie_index]

    similarity_scores = cosine_similarity(
        movie_vector,
        feature_matrix
    ).flatten()

    similar_indexes = similarity_scores.argsort()[::-1]

    recommendations = []

    for index in similar_indexes:

        if index == movie_index:
            continue

        recommendations.append({
            "title": movies.iloc[index]["title"],
            "genre": movies.iloc[index]["genre"],
            "release_date": movies.iloc[index]["release_date"],
            "rating": movies.iloc[index]["vote_average"],
            "overview": movies.iloc[index]["overview"],
            "similarity": round(
                similarity_scores[index] * 100,
                2
            )
        })

        if len(recommendations) >= number_of_recommendations:
            break

    return pd.DataFrame(recommendations)


# ============================================================
# GENRE LIST
# ============================================================

def get_genres():

    genres = set()

    for genre_string in movies["genre"]:

        if not genre_string:
            continue

        # Handle common formats
        cleaned = (
            genre_string
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
            .replace('"', "")
        )

        parts = cleaned.split(",")

        for genre in parts:

            genre = genre.strip()

            if genre:
                genres.add(genre)

    return sorted(genres)


genres = get_genres()


# ============================================================
# SIDEBAR
# ============================================================

st.sidebar.title("⚙️ Movie Explorer")


# ------------------------------------------------------------
# SORT
# ------------------------------------------------------------

sort_option = st.sidebar.selectbox(
    "📅 Sort Movies",
    [
        "Newest",
        "Oldest",
        "Highest Rated",
        "Most Popular"
    ]
)


# ------------------------------------------------------------
# GENRE FILTER
# ------------------------------------------------------------

genre_options = ["All Genres"] + genres

selected_genre = st.sidebar.selectbox(
    "🎭 Filter by Genre",
    genre_options
)


# ------------------------------------------------------------
# NUMBER OF MOVIES
# ------------------------------------------------------------

movie_limit = st.sidebar.select_slider(
    "Number of Movies",
    options=[10, 20, 50, 100],
    value=20
)


# ------------------------------------------------------------
# YEAR FILTER
# ------------------------------------------------------------

valid_years = movies["year"].dropna()

if not valid_years.empty:

    min_year = int(valid_years.min())
    max_year = int(valid_years.max())

    if min_year < max_year:

        selected_year = st.sidebar.slider(
            "📅 Release Year",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="sidebar_year_filter"
        )

    else:

        selected_year = (min_year, max_year)

        st.sidebar.info(
            f"📅 All movies are from {min_year}."
        )

else:

    selected_year = None

    st.sidebar.warning(
        "No valid release years found."
    )


# ============================================================
# MAIN HEADER
# ============================================================

st.title("🎬 Movie Recommendation System")

st.write(
    "Discover movies, browse thousands of titles, "
    "and get personalized recommendations."
)


st.info(
    f"🎬 Local database contains {len(movies):,} movies"
)


# ============================================================
# FILTER MOVIES
# ============================================================

filtered_movies = movies.copy()


# ------------------------------------------------------------
# YEAR FILTER
# ------------------------------------------------------------

if selected_year is not None:

    start_year, end_year = selected_year

    filtered_movies = filtered_movies[
        filtered_movies["year"].between(
            start_year,
            end_year
        )
    ]


# ------------------------------------------------------------
# GENRE FILTER
# ------------------------------------------------------------

if selected_genre != "All Genres":

    filtered_movies = filtered_movies[
        filtered_movies["genre"]
        .str.contains(
            selected_genre,
            case=False,
            na=False,
            regex=False
        )
    ]


# ============================================================
# SORT MOVIES
# ============================================================

if sort_option == "Newest":

    filtered_movies = filtered_movies.sort_values(
        by="release_date",
        ascending=False,
        na_position="last"
    )

elif sort_option == "Oldest":

    filtered_movies = filtered_movies.sort_values(
        by="release_date",
        ascending=True,
        na_position="last"
    )

elif sort_option == "Highest Rated":

    filtered_movies = filtered_movies.sort_values(
        by="vote_average",
        ascending=False
    )

elif sort_option == "Most Popular":

    filtered_movies = filtered_movies.sort_values(
        by="popularity",
        ascending=False
    )


# ============================================================
# BROWSE MOVIES
# ============================================================

st.header("🎥 Browse Movies")

display_movies = filtered_movies.head(movie_limit)

st.write(
    f"Showing {len(display_movies):,} movies"
)


if display_movies.empty:

    st.warning(
        "No movies match the selected filters."
    )

else:

    for _, movie in display_movies.iterrows():

        st.subheader(
            f"🎬 {movie['title']}"
        )

        # Release date
        if pd.notna(movie["release_date"]):

            release_date = movie["release_date"].strftime(
                "%Y-%m-%d"
            )

        else:

            release_date = "Unknown"

        st.markdown(
            f"📅 **Release Date:** {release_date}"
        )

        # Rating
        st.markdown(
            f"⭐ **Rating:** "
            f"{float(movie['vote_average']):.1f}/10"
        )

        # Genre
        genre_text = movie["genre"]

        if not genre_text:
            genre_text = "Unknown"

        st.markdown(
            f"🎭 **Genre:** {genre_text}"
        )

        # Overview
        overview = movie["overview"]

        if overview:

            st.write(overview)

        else:

            st.caption(
                "No overview available."
            )

        st.divider()


# ============================================================
# MOVIE RECOMMENDATIONS
# ============================================================

st.header("🍿 Find Similar Movies")


movie_titles = sorted(
    movies["title"].dropna().unique().tolist()
)


selected_movie = st.selectbox(
    "🔎 Search for a movie",
    ["Select a movie"] + movie_titles
)


recommendation_count = st.selectbox(
    "Number of recommendations",
    [5, 10],
    index=0
)


if selected_movie != "Select a movie":

    if st.button(
        "🎯 Recommend Similar Movies",
        type="primary"
    ):

        recommendations = recommend_movies(
            selected_movie,
            recommendation_count
        )

        if recommendations.empty:

            st.error(
                "Could not find recommendations."
            )

        else:

            st.subheader(
                f"Movies similar to {selected_movie}"
            )

            for _, movie in recommendations.iterrows():

                st.markdown(
                    f"### 🎬 {movie['title']}"
                )

                release_date = movie["release_date"]

                if pd.notna(release_date):

                    release_date = release_date.strftime(
                        "%Y-%m-%d"
                    )

                else:

                    release_date = "Unknown"

                st.markdown(
                    f"📅 **Release Date:** {release_date}"
                )

                st.markdown(
                    f"⭐ **Rating:** "
                    f"{float(movie['rating']):.1f}/10"
                )

                genre_text = movie["genre"]

                if not genre_text:
                    genre_text = "Unknown"

                st.markdown(
                    f"🎭 **Genre:** {genre_text}"
                )

                st.markdown(
                    f"🤖 **Similarity:** "
                    f"{movie['similarity']:.2f}%"
                )

                if movie["overview"]:

                    st.write(
                        movie["overview"]
                    )

                st.divider()


# ============================================================
# LATEST MOVIES
# ============================================================

st.header("🌐 Latest Movies")

st.caption(
    "Latest movies from the local database — newest releases first."
)


latest_movies = movies.sort_values(
    by="release_date",
    ascending=False,
    na_position="last"
).head(10)


for _, movie in latest_movies.iterrows():

    if pd.notna(movie["release_date"]):

        date_text = movie["release_date"].strftime(
            "%Y-%m-%d"
        )

    else:

        date_text = "Unknown"

    st.markdown(
        f"🎬 **{movie['title']}** — "
        f"📅 {date_text} — "
        f"⭐ {float(movie['vote_average']):.1f}"
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Built with Python, Pandas, Scikit-learn, "
    "and Streamlit"
)