from movie_recommender import recommend_movies


movie = input("Enter a movie title: ")


recommendations = recommend_movies(
    movie,
    5
)


if recommendations:

    print("\nRecommended Movies:")

    for i, movie in enumerate(
        recommendations,
        start=1
    ):

        print(
            f"\n{i}. {movie['title']}"
        )

        print(
            f"   Genre: {movie['genre']}"
        )

        print(
            f"   Rating: {movie['rating']}"
        )

        print(
            f"   Release Date: {movie['release_date']}"
        )

        print(
            f"   Similarity: {movie['similarity']}%"
        )

else:

    print(
        "\nMovie not found."
    )