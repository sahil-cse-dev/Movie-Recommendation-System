from movie_recommender import get_movies_sorted


movies = get_movies_sorted(
    "newest",
    20
)


print("\nNewest Movies:\n")

for i, movie in enumerate(
    movies.itertuples(),
    start=1
):

    print(
        f"{i}. {movie.title} | "
        f"{movie.release_date} | "
        f"⭐ {movie.vote_average}"
    )