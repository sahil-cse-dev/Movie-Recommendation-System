import requests
import streamlit as st


BASE_URL = "https://api.themoviedb.org/3"

TMDB_API_KEY = st.secrets["TMDB_API_KEY"]


def get_popular_movies(page=1):

    url = f"{BASE_URL}/movie/popular"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "page": page
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def get_movies_newest(page=1):

    url = f"{BASE_URL}/discover/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "language": "en-US",
        "sort_by": "primary_release_date.desc",
        "page": page,
        "include_adult": "false",
        "include_video": "false"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def get_movie_details(title):

    url = f"{BASE_URL}/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": title,
        "language": "en-US"
    }

    response = requests.get(
        url,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    data = response.json()

    if data["results"]:
        return data["results"][0]

    return None