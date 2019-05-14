import sqlite3
from flask import Flask
from flask import jsonify
from flask import request
import csv
from scipy.stats.stats import pearsonr
import math
import warnings

warnings.filterwarnings("ignore")

app = Flask(__name__)


def create_table():
    try:
        with connect() as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE movies (movieId TEXT PRIMARY KEY,title TEXT,genres TEXT)")
            conn.commit()
        insertall()
    except Exception as e:
        print(e.message)


def connect():
    conn = sqlite3.connect('lite.db')
    conn.text_factory = str
    return conn


def insert_to_db(movieId, title, genres):
    with connect() as conn:
        cur = conn.cursor()
        if ('|' in genres):
            genres = genres.split("|")[0]
        cur.execute("INSERT INTO movies VALUES (?,?,?);", (movieId, title, genres))
        conn.commit()


def insertall():
    with open('movies.csv', 'r') as csv_file:
        allmovies = csv.reader(csv_file, delimiter=',')
        with connect() as conn:
            cur = conn.cursor()
            for row in allmovies:
                genres = row[2]
                if ('|' in genres):
                    genres = genres.split("|")[0]
                cur.execute("INSERT INTO movies VALUES (?,?,?);", (row[0], row[1], genres))
            cur.execute("DELETE FROM movies WHERE movieId = 'movieId'")
            conn.commit()


def view():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM movies;")
        rows = cur.fetchall()
        return jsonify(rows)


def search(movieId, title, genres):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM movies WHERE movieId = ? AND title = ? AND genres = ?;", movieId, title, genres)
        rows = cur.fetchall()
        return rows


def delete(movieId, title, genres):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM movies WHERE movieId = ? AND title = ? AND genres = ?;", movieId, title, genres)
        conn.commit()


def update(movieId, title, genres):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE movies SET title=?, genres=? WHERE movieId=?;", (title, genres, movieId))
        conn.commit()


# create_table()


#   ______                    ______
#  (_____ \           _      (_____ \
#   _____) )___  ____| |_      ____) )
#  |  ____/ _  |/ ___)  _)    /_____/
#  | |   ( ( | | |   | |__    _______
#  |_|    \_||_|_|    \___)  (_______)
#

def create_table_rating():
    is_rating_table_exist = False
    try:
        with connect() as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE Rating (userId TEXT ,movieId TEXT, rating REAL)")
            conn.commit()
    except Exception:
        print("Exception")
        is_rating_table_exist = True

    if not is_rating_table_exist:
        insert_all_ratings()


def insert_all_ratings():
    with open('ratings.csv', 'r') as csv_file:
        ratings = csv.reader(csv_file, delimiter=',')
        with connect() as conn:
            cur = conn.cursor()
            for row in ratings:
                cur.execute("INSERT INTO Rating VALUES (?,?,?);", (row[0], row[1], row[2]))
            conn.commit()
            cur.execute("DELETE FROM Rating WHERE movieId = 'movieId'")
            conn.commit()


@app.route('/rec', methods=['GET', 'POST'])
def view2():
    user_id = request.args.get('userid')
    k = request.args.get('k')
    user_movies = []
    user_movies_ratings = {}
    conn = sqlite3.connect('lite.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Rating WHERE userId = ?;", (user_id,))
    rows = cur.fetchall()
    for row in rows:
        user_movies.append(str(row[1]))
        user_movies_ratings[str(row[1])] = row[2]

    cur.execute("SELECT DISTINCT userId FROM Rating WHERE NOT userId = ?;", (user_id,))
    user_ids = cur.fetchall()
    pearsonr_users = {}
    for uid in user_ids:
        cur.execute("SELECT * FROM Rating WHERE userId = ?;", (str(uid[0]),))
        rows = cur.fetchall()
        user_n_ratings = []
        user_u_ratings = []
        for row in rows:
            if str(row[1]) in user_movies:
                user_n_ratings.append(row[2])
                user_u_ratings.append(user_movies_ratings[str(row[1])])
        if len(user_n_ratings) is 0 or len(user_n_ratings) is 1:
            pearsonr_users[str(uid[0])] = 0
        else:
            pearsonr_users[str(uid[0])] = pearsonr(user_n_ratings, user_u_ratings)[1]
            if math.isnan(pearsonr_users[str(uid[0])]):
                pearsonr_users[str(uid[0])] = 0

    max_users = []
    for i in range(0, int(k)):
        max = 0
        u = ''
        for user in pearsonr_users.keys():
            if pearsonr_users[user] >= max:
                max = pearsonr_users[user]
                u = user
        pearsonr_users[u] = 0
        max_users.append(u)

    result_movies = []
    for user in max_users:
        cur.execute("SELECT movieId FROM Rating WHERE userId = ? order by rating;", (user,))
        movies = cur.fetchall()
        for movie in movies:
            if str(movie[0]) not in result_movies:
                result_movies.append(str(movie[0]))
                break

    movies_names = []
    for movie in result_movies:
        cur.execute("SELECT title FROM movies WHERE movieId = ?;", (movie,))
        movies_names.append(cur.fetchall()[0][0])

    conn.close()
    return jsonify(movies_names)


if __name__ == '__main__':
    create_table()
    create_table_rating()
    print("done enter values to dbs")
    app.run(debug=True)
