from tmdb_api import get_movie_details


movie = get_movie_details("Interstellar")


if movie:

    print("Title:", movie["title"])
    print("Release Date:", movie["release_date"])
    print("Rating:", movie["rating"])
    print("Poster:", movie["poster"])

else:

    print("Movie not found.")