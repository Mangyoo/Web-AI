import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, Link, Tag, Rating
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
def check_and_read_data(db):
    # check if we have movies in the database
    # read data if the database is empty
    if Movie.query.count() == 0:
        # Read links from 'links.csv' outside the loop
        #links_data = csv_reader('data/links.csv',0)
        # Read tags from 'tags.csv' outside the loop
        #print(links_data)
        #tags_data = csv_reader('data/tags.csv',1)
        #ratings_data = csv_reader('data/ratings.csv',2)
        #read ratings from 'ratings.csv' outside the loop
        # read movies from csv
        with open('data/movies.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        id = row[0]
                        title = row[1]
                        movie = Movie(id=id, title=title)
                        db.session.add(movie)
                        genres = row[2].split('|')  # genres is a list of genres
                        for genre in genres:  # add each genre to the movie_genre table
                            movie_genre = MovieGenre(movie_id=id, genre=genre)
                            db.session.add(movie_genre)
                        db.session.commit()  # save data to database
                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")
                # Retrieve IMDb ID from the pre-read data
    if Link.query.count() == 0:
        # read movies from csv
        with open('data/links.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        
                        movie_id = row[0]
                        imdb_id = row[1]
                        tmdb_id = row[2]
                        links = Link(movie_id = movie_id, imdb_id = imdb_id, tmdb_id=tmdb_id )
                        db.session.add(links)
                        db.session.commit()
                       
                    except IntegrityError:
                        print("Ignoring duplicate link: " + imdb_id)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, "links read")  
                # Retrieve tags from the pre-read data
    if Tag.query.count() == 0:
        # read movies from csv
        with open('data/tags.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    try:
                        
                        user_id = row[0]
                        movie_id = row[1]
                        tag = row[2]
                        timestamp = datetime.utcfromtimestamp(int(row[3]))
                        tags = Tag(user_id = user_id, movie_id = movie_id, tag= tag, timestamp = timestamp)
                        
                        db.session.add(tags)
                        db.session.commit()
                       
                    except IntegrityError:
                        print("Ignoring duplicate tag: " + tag)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, "tags read")
    if Rating.query.count() == 0:
        # read movies from csv
        with open('data/ratings.csv', newline='', encoding='utf8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            count = 0
            for row in reader:
                if count > 0:
                    
                        
                        user_id = row[0]
                        movie_id = row[1]
                        rating = row[2]
                        
                        
                        ratings = Rating(user_id = user_id, movie_id = movie_id, rating=rating )
                        db.session.add(ratings)
                        db.session.commit()
                       
                    
                count += 1
                if count % 100 == 0:
                    print(count, "ratings read") 

                #next one: recreate this model with the previous model for faster duplicate elimination
                
                        
                            


def csv_reader(path:str, movie_id_index):
    reader = csv.reader(open(path, newline='', encoding='utf8'), delimiter=',')
    next(reader, None)
    data = dict()
    for row in reader:
        try:
            key = int(float(row[movie_id_index]))
        except ValueError:
            # Handle the case where the value cannot be converted to int
            print(f"Skipping invalid key: {row[movie_id_index]}")
            continue
        if not key in data:
            data[key] = list()
        data[key].append(row)
    return data 