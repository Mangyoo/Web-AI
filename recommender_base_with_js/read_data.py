import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, Link, Tag

def check_and_read_data(db):
    # check if we have movies in the database
    # read data if the database is empty
    if Movie.query.count() == 0:
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

                        # Reading links from 'links.csv'
                        link_row = next(csv.reader(open('recommender_base_with_js/data/links.csv', newline='', encoding='utf8'), delimiter=','))
                        imdb_id = link_row[1] if link_row[0] == id else None
                        link = Link(movie_id=id, imdb_id=imdb_id)
                        db.session.add(link)

                        # Reading tags from 'tags.csv'
                        tag_row = next(csv.reader(open('recommender_base_with_js/data/tags.csv', newline='', encoding='utf8'), delimiter=','))
                        tag_user_id = tag_row[0]
                        tag_movie_id = tag_row[1]
                        tag = Tag(movie_id=id, tag=tag_row[2] if tag_movie_id == id else None)
                        db.session.add(tag)

                        db.session.commit()  # save data to the database
                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")
