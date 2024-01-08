# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, request
from flask_user import login_required, UserManager, current_user

from models import db, User, Movie, MovieGenre, Link, Tag, Rating
from read_data import check_and_read_data
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# import sleep from python
from time import sleep

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


# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # render home.html template
    return render_template("home.html")

def collaborative_filtering(movie_id):
    # Fetch all ratings from the database using the ORM
    ratings = Rating.query.all()

    # Convert the list of Rating objects to a DataFrame
    ratings_df = pd.DataFrame([(rating.user_id, rating.movie_id, rating.rating) for rating in ratings],
                               columns=['user_id', 'movie_id', 'rating'])
    
    print(ratings_df.head(20))
    print("AAAAAA")

    # Create a user-item matrix for collaborative filtering
    Collab_df = ratings_df.pivot_table(index='movie_id', columns='user_id', values='rating')
    Collab_df = Collab_df.fillna(0)
    print(Collab_df.head(20))
    print("AAAAAA")

    # Take the latent vectors for the selected movie from the collaborative matrix
    a_2 = np.array(Collab_df.loc[movie_id]).reshape(1, -1)

    # Calculate the similarity of this movie with the others in the list
    score_2 = cosine_similarity(Collab_df, a_2).reshape(-1)

    # Form a data frame of similar movies
    dictDf = {'collaborative': score_2}
    similar_collab = pd.DataFrame(dictDf, index=Collab_df.index)

    

    # Sort it based on collaborative filtering similarity
    similar_collab.sort_values(by = 'collaborative', ascending=False, inplace=True)
    print(similar_collab.head(20))
    print("AAAAAA")
    # Return the top 10 similar movies
    top_similar_movies = similar_collab.index[1:11]  # excluding the movie itself
    return top_similar_movies



# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/movies')
@login_required  # User must be authenticated
def movies_page():
    # String-based templates

    # first 10 movies
    movies = Movie.query.limit(100).all()

    movie_id_to_recommend = 1
    top_similar_movies = collaborative_filtering(movie_id_to_recommend)
    recommended_movies = Movie.query.filter(Movie.id.in_(top_similar_movies)).all()

    return render_template("movies.html", movies=movies, recommended_movies=recommended_movies)


    # only Romance movies
    # movies = Movie.query.filter(Movie.genres.any(MovieGenre.genre == 'Romance')).limit(10).all()

    # only Romance AND Horror movies
    # movies = Movie.query\
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Romance')) \
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Horror')) \
    #     .limit(10).all()

    


@app.route('/rate', methods=['POST'])
@login_required  # User must be authenticated
def rate():
    userid = current_user.id
    movieid = request.form.get('movieid')
    rating = float(request.form.get('rating'))
    
    #check for existing rating and overwrite it
    existing_rating = Rating.query.filter_by(user_id=userid, movie_id=movieid).first()
    if existing_rating:
        existing_rating.rating = rating
    else:
        new_rating = Rating(user_id=userid, movie_id=movieid, rating=rating)
        db.session.add(new_rating)

    db.session.commit()
    print("Rate {} for {} by {}".format(rating, movieid, userid))

    return render_template("rated.html", rating=rating)

print(collaborative_filtering(1))

# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
