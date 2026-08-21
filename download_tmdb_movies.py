import requests
import pandas as pd
import os
import time


# =========================================================
# CONFIGURATION
# =========================================================

API_KEY = "ea3d8f5b79fe36f94fe3e6e7990602e3"

BASE_URL = "https://api.themoviedb.org/3/discover/movie"

OUTPUT_FILE = "tmdb_movies.csv"

# How many TMDB pages to download
# 1 page = 20 movies
MAX_PAGES = 500

# Save after every N pages
SAVE_EVERY = 10


# =========================================================
# TMDB SESSION
# =========================================================

session = requests.Session()

session.headers.update({
    "User-Agent": "MovieRecommendationSystem/1.0"
})


# =========================================================
# LOAD EXISTING DATA
# =========================================================

if os.path.exists(OUTPUT_FILE):

    print(f"Existing database found: {OUTPUT_FILE}")

    try:

        existing_df = pd.read_csv(
            OUTPUT_FILE
        )

        existing_ids = set(
            existing_df["id"].dropna().astype(int)
        )

        movies_data = existing_df.to_dict(
            "records"
        )

        print(
            f"Existing movies: {len(movies_data)}"
        )

    except Exception:

        print(
            "Could not read existing database. "
            "Starting fresh."
        )

        movies_data = []
        existing_ids = set()

else:

    print(
        "No existing TMDB database found."
    )

    movies_data = []
    existing_ids = set()


# =========================================================
# DOWNLOAD MOVIES
# =========================================================

new_movies = 0


for page in range(1, MAX_PAGES + 1):

    print(
        f"\nDownloading page "
        f"{page}/{MAX_PAGES}..."
    )

    params = {

        "api_key": API_KEY,

        "language": "en-US",

        "sort_by": "primary_release_date.desc",

        "page": page,

        "include_adult": "false",

        "include_video": "false"

    }


    try:

        response = session.get(
            BASE_URL,
            params=params,
            timeout=30
        )


        # -------------------------------------------------
        # STATUS CHECK
        # -------------------------------------------------

        if response.status_code != 200:

            print(
                f"TMDB Error: "
                f"{response.status_code}"
            )

            print(
                response.text[:500]
            )

            break


        data = response.json()


        results = data.get(
            "results",
            []
        )


        if not results:

            print(
                "No more movies found."
            )

            break


        # -------------------------------------------------
        # PROCESS MOVIES
        # -------------------------------------------------

        for movie in results:

            movie_id = movie.get(
                "id"
            )


            # Skip duplicate
            if movie_id in existing_ids:

                continue


            # ---------------------------------------------
            # GENRE IDS
            # ---------------------------------------------

            genre_ids = movie.get(
                "genre_ids",
                []
            )


            genre_text = ",".join(
                str(g)
                for g in genre_ids
            )


            # ---------------------------------------------
            # MOVIE RECORD
            # ---------------------------------------------

            movie_record = {

                "id": movie_id,

                "title": movie.get(
                    "title",
                    ""
                ),

                "original_title": movie.get(
                    "original_title",
                    ""
                ),

                "overview": movie.get(
                    "overview",
                    ""
                ),

                "release_date": movie.get(
                    "release_date",
                    ""
                ),

                "vote_average": movie.get(
                    "vote_average",
                    0
                ),

                "vote_count": movie.get(
                    "vote_count",
                    0
                ),

                "popularity": movie.get(
                    "popularity",
                    0
                ),

                "poster_path": movie.get(
                    "poster_path",
                    ""
                ),

                "backdrop_path": movie.get(
                    "backdrop_path",
                    ""
                ),

                "original_language": movie.get(
                    "original_language",
                    ""
                ),

                "genre_ids": genre_text

            }


            movies_data.append(
                movie_record
            )

            existing_ids.add(
                movie_id
            )

            new_movies += 1


        print(
            f"Movies downloaded so far: "
            f"{new_movies}"
        )


        # -------------------------------------------------
        # SAVE PERIODICALLY
        # -------------------------------------------------

        if page % SAVE_EVERY == 0:

            df = pd.DataFrame(
                movies_data
            )

            df.to_csv(
                OUTPUT_FILE,
                index=False,
                encoding="utf-8-sig"
            )

            print(
                f"💾 Saved "
                f"{len(df):,} movies"
            )


        # -------------------------------------------------
        # RATE LIMIT PROTECTION
        # -------------------------------------------------

        time.sleep(0.25)


    except requests.exceptions.RequestException as e:

        print(
            f"\nConnection error: {e}"
        )

        print(
            "Saving downloaded movies before exit..."
        )

        break


    except KeyboardInterrupt:

        print(
            "\nDownload stopped by user."
        )

        break


# =========================================================
# FINAL SAVE
# =========================================================

if movies_data:

    df = pd.DataFrame(
        movies_data
    )


    # Remove duplicate IDs
    if "id" in df.columns:

        df = df.drop_duplicates(
            subset=["id"]
        )


    # Sort newest first
    if "release_date" in df.columns:

        df["release_date"] = pd.to_datetime(
            df["release_date"],
            errors="coerce"
        )

        df = df.sort_values(
            "release_date",
            ascending=False,
            na_position="last"
        )

        df["release_date"] = (
            df["release_date"]
            .dt.strftime("%Y-%m-%d")
            .fillna("")
        )


    # Save
    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )


    print(
        "\n======================================"
    )

    print(
        "DOWNLOAD COMPLETE"
    )

    print(
        "======================================"
    )

    print(
        f"Total movies: {len(df):,}"
    )

    print(
        f"New movies added: {new_movies:,}"
    )

    print(
        f"Database: {OUTPUT_FILE}"
    )

else:

    print(
        "\nNo movie data was downloaded."
    )