from movie_recommender import recommend_movies


movie = input("Enter a movie title: ")

recommendations = recommend_movies(movie)


if recommendations:
    print("\nRecommended Movies:")

    for i, recommendation in enumerate(recommendations, start=1):
        print(f"{i}. {recommendation}")

else:
    print("\nMovie not found.")