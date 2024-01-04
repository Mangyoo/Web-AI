import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, Link, Tag
from flask_sqlalchemy import SQLAlchemy

def check_and_read_data(db):
    # check if we have movies in the database
    # read data if the database is empty
    if Movie.query.count() == 0:
        # Read links from 'links.csv' outside the loop
        links_data = list(csv.reader(open('recommender_base_with_js/data/links.csv', newline='', encoding='utf8'), delimiter=','))

        # Read tags from 'tags.csv' outside the loop
        tags_data = list(csv.reader(open('recommender_base_with_js/data/tags.csv', newline='', encoding='utf8'), delimiter=','))

        # read movies from csv
        with open('recommender_base_with_js/data/movies.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        id = row[0]
                        title = row[1]
                        movie = Movie(id=id, title=title)
                        db.session.add(movie)

                        # Adding genres to the MovieGenre table
                        genres = row[2].split('|')
                        for genre in genres:
                            movie_genre = MovieGenre(movie_id=id, genre=genre)
                            db.session.add(movie_genre)

                        # Retrieve IMDb ID from the pre-read data
                        link_row = next((link for link in links_data if link[0] == id), None)
                        imdb_id = link_row[1] if link_row else None
                        link = Link(movie_id=id, imdb_id=imdb_id)
                        db.session.add(link)

                        # Retrieve tags from the pre-read data
                        tag_row = next((tag for tag in tags_data if tag[1] == id), None)
                        tag = Tag(movie_id=id, tag=tag_row[2] if tag_row else None)
                        db.session.add(tag)

                        db.session.commit()  # save data to the database
                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")
