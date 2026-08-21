from tmdb_api import get_popular_movies


try:

    data = get_popular_movies(1)

    movies = data.get("results", [])

    print("TMDB connection successful!")
    print("Movies received:", len(movies))
    print()

    for movie in movies[:5]:

        print(
            movie.get("title"),
            "-",
            movie.get("release_date")
        )

except Exception as e:

    print("TMDB ERROR:")
    print(e)