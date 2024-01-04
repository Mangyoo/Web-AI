import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, Link, Tag
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
def check_and_read_data(db):
    # check if we have movies in the database
    # read data if the database is empty
    if Movie.query.count() == 0:
        # Read links from 'links.csv' outside the loop
        links_data = csv_reader('data/links.csv',0)
        # Read tags from 'tags.csv' outside the loop
        print(links_data)
        tags_data = csv_reader('data/tags.csv',1)
        # read movies from csv
        with open('data/movies.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            next(reader, None)
            for row in reader:
                id = int(row[0])
                title = row[1]
                try:
                    movie = Movie(id=id, title=title)
                    db.session.add(movie)
                     # Adding genres to the MovieGenre table
                    genres = row[2].split('|')
                    for genre in genres:
                        movie_genre = MovieGenre(movie_id=id, genre=genre)
                        db.session.add(movie_genre)
                    db.session.commit()
                except IntegrityError as e: 
                    print("Ignoring duplicate movie: " + title) 
                    db.session.rollback()

                # Retrieve IMDb ID from the pre-read data
                if id in links_data:
                    for link_row in links_data[id]:
                        link = Link(movie_id=id, imdb_id=link_row[1], tmdb_id=link_row[2])
                        db.session.add(link)
                    db.session.commit()

                # Retrieve tags from the pre-read data
                if id in tags_data:
                    for tag_row in tags_data[id]:
                        try:
                            tag = Tag(user_id=tag_row[0], movie_id=id, tag=tag_row[2], timestamp=datetime.utcfromtimestamp(int(tag_row[3])))
                            db.session.add(tag)
                            db.session.commit()
                        except IntegrityError as e: 
                            print("Ignoring duplicate tag: " + tag_row[2]) 
                            db.session.rollback()


def csv_reader(path:str, movie_id_index):
    reader = csv.reader(open(path, newline='', encoding='utf8'), delimiter=',')
    next(reader, None)
    data = dict()
    for row in reader:
        key = int(row[movie_id_index])
        if not key in data:
            data[key] = list()
        data[key].append(row)
    return data 