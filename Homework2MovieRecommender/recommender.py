# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from ctypes.wintypes import tagSIZE
from flask import Flask, render_template, request
from flask_user import login_required, UserManager, current_user
from fuzzywuzzy import process
from models import db, User, Movie, MovieGenre, Link, Tag, Rating
from read_data import check_and_read_data
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from time import sleep
from sqlalchemy import func

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movie_recommender.sqlite'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Movie Recommender"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form

    # make sure we redirect to home view, not /
    # (otherwise paths for registering, login and logout will not work on the server)
    USER_AFTER_LOGIN_ENDPOINT = 'home_page'
    USER_AFTER_LOGOUT_ENDPOINT = 'home_page'
    USER_AFTER_REGISTER_ENDPOINT = 'home_page'
    USER_AFTER_CONFIRM_ENDPOINT = 'home_page'

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db
db.init_app(app)  # initialize database
db.create_all()  # create database if necessary
user_manager = UserManager(app, db, User)  # initialize Flask-User management


@app.cli.command('initdb')
def initdb_command():
    global db
    """Creates the database tables."""
    check_and_read_data(db)
    print('Initialized the database.')


def collaborative_filtering(movie_id):
    # Fetch all ratings from the database using the ORM
    ratings = Rating.query.all()

    # Convert the list of Rating objects to a DataFrame
    ratings_df = pd.DataFrame([(rating.user_id, rating.movie_id, rating.rating) for rating in ratings],
                               columns=['user_id', 'movie_id', 'rating'])
    
    

    # Create a user-item matrix for collaborative filtering
    Collab_df = ratings_df.pivot_table(index='movie_id', columns='user_id', values='rating')
    Collab_df = Collab_df.fillna(0)
    

    # Take the latent vectors for the selected movie from the collaborative matrix
    a_2 = np.array(Collab_df.loc[movie_id]).reshape(1, -1)

    # Calculate the similarity of this movie with the others in the list
    score_2 = cosine_similarity(Collab_df, a_2).reshape(-1)

    # Form a data frame of similar movies
    dictDf = {'collaborative': score_2}
    similar_collab = pd.DataFrame(dictDf, index=Collab_df.index)

    

    # Sort it based on collaborative filtering similarity
    similar_collab.sort_values(by = 'collaborative', ascending=False, inplace=True)
    
    
    # Return the top 10 similar movies
    top_similar_movies = similar_collab.index[1:11]  # excluding the movie itself
    return top_similar_movies

def user_comparison(user_id):
    # Fetch all ratings from the database using the ORM
    ratings = Rating.query.all()

    # Convert the list of Rating objects to a DataFrame
    ratings_df = pd.DataFrame([(rating.user_id, rating.movie_id, rating.rating) for rating in ratings],
                               columns=['user_id', 'movie_id', 'rating'])
    
    

    # Create a user-item matrix for collaborative filtering
    Collab_df = ratings_df.pivot_table(index='user_id', columns='movie_id', values='rating')
    Collab_df = Collab_df.fillna(0)

    
    

    # Take the latent vectors for the selected movie from the collaborative matrix
    a_2 = np.array(Collab_df.loc[user_id]).reshape(1, -1)

    # Calculate the similarity of this movie with the others in the list
    score_2 = cosine_similarity(Collab_df, a_2).reshape(-1)

    # Form a data frame of similar movies
    dictDf = {'collaborative': score_2}
    similar_collab = pd.DataFrame(dictDf, index=Collab_df.index)

    

    # Sort it based on collaborative filtering similarity
    similar_collab.sort_values(by = 'collaborative', ascending=False, inplace=True)
    
    
    # Return the top 10 similar movies
    top_similar_movies = similar_collab.index[1:11]  # excluding the movie itself
    return top_similar_movies

def fuzzy_search_movies(search_query, all_movies, threshold=80):
    # Create a list of movie titles
    movie_titles = [movie.title for movie in all_movies]

    # Use fuzzywuzzy's process.extract to find all matches above the threshold
    results = process.extract(search_query, movie_titles)

    # Get the matched movie titles and their similarity scores
    matched_movies = [(title, score) for title, score in results if score >= threshold]

    if matched_movies:
        # If matches are found, retrieve the corresponding movies
        matched_movies_data = [
            next((movie for movie in all_movies if movie.title == title), None)
            for title, _ in matched_movies
        ]
        return matched_movies_data
    else:
        # If no matches are found, return an empty list
        return []

@app.route('/')
def home_page():
    # render home.html template
    return render_template("home.html")


# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/movies')
@login_required
def movies_page():
    page = request.args.get('page', 1, type=int)  # Get the page parameter from the request, default to 1 if not provided
    per_page = 10  # Number of movies per page

    movies = Movie.query.paginate(page=page, per_page=per_page, error_out=False)

    all_genres = db.session.query(MovieGenre.genre).distinct().all()
    all_genres = [genre[0] for genre in all_genres]
    all_genres = [element.rstrip(',') for element in all_genres]

    selected_genres = request.args.getlist('genres[]')

    search_request = request.args.get('search')
    title = "All Movies"

    if search_request:
        searched_movies = fuzzy_search_movies(search_request, movies.items)
        if len(searched_movies) > 0:
            return render_template("filtermovies.html", movies=searched_movies, all_genres=all_genres, title="Search Results")
        else:
            return render_template("nosearchresults.html")

    if selected_genres:
        genre_movies = Movie.query.filter(Movie.genres.any(MovieGenre.genre == selected_genres[0])).all()
        for g in selected_genres[1:]:
            joiner_movies = Movie.query.filter(Movie.genres.any(MovieGenre.genre == g)).all()
            genre_movies = list(set(genre_movies) & set(joiner_movies))
        if len(genre_movies) > 0:
            return render_template("filtermovies.html", movies=genre_movies, all_genres=all_genres, title="Filtered by Genres")
        else:
            return render_template("filtermovies.html", movies=genre_movies, all_genres=all_genres, title="No Movies match your filtered Genres")

    return render_template("movies.html", movies=movies.items, all_genres=all_genres, title="All Movies", pagination=movies)


@app.route('/recommender')
@login_required
def recommender():
    
     
    current_movie = request.args.get('movie_id')
    current_movie = int(current_movie)
    current_name = Movie.query.get(current_movie)

    sim_movs = collaborative_filtering(current_movie)
    

    movies = Movie.query.filter(Movie.id.in_(sim_movs)).all()

    return render_template("similar_movies.html", movies = movies, current_name = current_name)  

@app.route('/userrecommender')
@login_required
def userrecommender():
    if Rating.query.filter_by(user_id=current_user.id).count() >=10:  
        user_id = current_user.id
        user_id = int(user_id)
        sim_movs = user_comparison(user_id)

        movies = Movie.query.filter(Movie.id.in_(sim_movs)).all()

        return render_template("userrecommendations.html", movies = movies)  
    else:
        return render_template("no10movies.html")

@app.route('/randommovie')
@login_required
def randommovie():
    all_movies = Movie.query.all()
    # Select a random movie from the list
    random_movie = np.random.choice(all_movies)
    return render_template("random_movie.html", m = random_movie)  


@app.route('/ratedmovies')
@login_required
def ratedmovies():
    
    ratings = Rating.query.filter_by(user_id=current_user.id).all()
    movie_ids = [rating.movie_id for rating in ratings]
    ratinglist = [rating.rating for rating in ratings]
    movies = Movie.query.filter(Movie.id.in_(movie_ids)).all()
    
    combined_list = []

    for movie, rating in zip(movies, ratinglist):
        movie_info = {
            'movie_id': movie.id,
            'title': movie.title,
            'genre': movie.genres,  # Update with the actual way to get genres
            'rating': rating,
            'links': [{'imdb_id': link.imdb_id, 'tmdb_id': link.tmdb_id} for link in movie.links],  # Adjust based on your actual structure
            'tags': movie.tags
        }
        combined_list.append(movie_info)
    return render_template("ratedmovies.html", movies = combined_list, ratinglist = ratinglist)  
       


@app.route('/rate', methods=['POST'])
@login_required  # User must be authenticated
def rate():
    userid = current_user.id
    movieid = request.form.get('movieid')
    rating = float(request.form.get('rating'))
    print(userid, movieid, rating)
    new_rating = Rating(user_id=userid, movie_id=movieid, rating=rating)
    db.session.add(new_rating)
    db.session.commit()
    print("Rate {} for {} by {}".format(rating, movieid, userid))

    return render_template("rated.html", rating=rating)


# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
