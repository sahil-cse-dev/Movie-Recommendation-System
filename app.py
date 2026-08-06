import streamlit as st
import pandas as pd
from movie_recommender import recommend_movies


# -----------------------------
# Page Configuration
# -----------------------------
st.set_page_config(
    page_title="Movie Recommendation System",
    page_icon="🎬",
    layout="wide"
)


# -----------------------------
# Load Movie Dataset
# -----------------------------
movies = pd.read_csv("data/movies.csv")


# -----------------------------
# Custom CSS
# -----------------------------
st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 45px;
        font-weight: bold;
    }

    .subtitle {
        text-align: center;
        font-size: 20px;
        margin-bottom: 30px;
    }

    .movie-card {
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #ddd;
        margin-bottom: 15px;
    }
    </style>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Header
# -----------------------------
st.markdown(
    '<div class="main-title">🎬 Movie Recommendation System</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">Find movies similar to your favorite movie</div>',
    unsafe_allow_html=True
)


# -----------------------------
# Movie Selection
# -----------------------------
movie_titles = movies["title"].tolist()

selected_movie = st.selectbox(
    "🎥 Select a Movie",
    movie_titles
)


# -----------------------------
# Recommendation Button
# -----------------------------
if st.button("🍿 Recommend Movies"):

    recommendations = recommend_movies(selected_movie)

    if recommendations:

        st.success(
            f"Top 5 movies similar to **{selected_movie}**:"
        )

        for i, movie in enumerate(recommendations, start=1):

            movie_info = movies[
                movies["title"] == movie
            ].iloc[0]

            st.markdown(
                f"""
                <div class="movie-card">
                    <h3>🎬 {i}. {movie}</h3>
                    <p><b>Genre:</b> {movie_info['genre']}</p>
                    <p>{movie_info['description']}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

    else:

        st.error(
            "Sorry, recommendations could not be found."
        )


# -----------------------------
# Footer
# -----------------------------
st.markdown("---")

st.markdown(
    "Built with ❤️ using Python, Pandas, Scikit-learn and Streamlit"
)
