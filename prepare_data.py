import pandas as pd
import ast


# Load datasets
movies = pd.read_csv("data/tmdb_5000_movies.csv")
credits = pd.read_csv("data/tmdb_5000_credits.csv")


# Rename credits title column
credits = credits.rename(columns={"movie_id": "id"})


# Merge both datasets
movies = movies.merge(
    credits[["id", "cast", "crew"]],
    on="id"
)


# Extract names from JSON-like columns
def get_names(value):
    try:
        data = ast.literal_eval(value)

        return " ".join(
            item["name"].replace(" ", "")
            for item in data[:5]
        )

    except:
        return ""


# Extract genres
def get_genres(value):
    try:
        data = ast.literal_eval(value)

        return ", ".join(
            item["name"]
            for item in data
        )

    except:
        return ""


# Extract director
def get_director(value):
    try:
        data = ast.literal_eval(value)

        for item in data:
            if item["job"] == "Director":
                return item["name"].replace(" ", "")

        return ""

    except:
        return ""


movies["genres_clean"] = movies["genres"].apply(get_genres)

movies["keywords_clean"] = movies["keywords"].apply(get_names)

movies["cast_clean"] = movies["cast"].apply(get_names)

movies["director_clean"] = movies["crew"].apply(get_director)


# Clean overview
movies["overview"] = movies["overview"].fillna("")


# Create combined features
movies["features"] = (
    movies["genres_clean"] + " "
    + movies["keywords_clean"] + " "
    + movies["cast_clean"] + " "
    + movies["director_clean"] + " "
    + movies["overview"]
)


# Convert release date
movies["release_date"] = pd.to_datetime(
    movies["release_date"],
    errors="coerce"
)


# Remove movies without release dates
movies = movies.dropna(
    subset=["release_date"]
)


# Sort newest to oldest
movies = movies.sort_values(
    by="release_date",
    ascending=False
)


# Select useful columns
final_movies = movies[
    [
        "id",
        "title",
        "release_date",
        "genres_clean",
        "vote_average",
        "vote_count",
        "popularity",
        "overview",
        "features"
    ]
].copy()


# Rename columns
final_movies = final_movies.rename(
    columns={
        "genres_clean": "genre"
    }
)


# Save the cleaned dataset
final_movies.to_csv(
    "data/movies_large.csv",
    index=False
)


print("Data preparation completed!")
print("Total movies:", len(final_movies))

print("\nNewest movies:")
print(
    final_movies[
        ["title", "release_date", "vote_average"]
    ].head(10).to_string(index=False)
)