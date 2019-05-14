import sqlite3
from flask import Flask
from flask import jsonify
from flask import request
import csv
import math

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
        return rows


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
def view():
    user_id = request.args.get('userid')
    k = request.args.get('k')
    user_movies = []
    user_movies_ratings = {}
    conn = sqlite3.connect('lite.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM Rating WHERE userId = ?;", (user_id,))
    rows = cur.fetchall()
    sum_rating = 0
    for row in rows:
        user_movies.append(str(row[1]))
        user_movies_ratings[str(row[1])] = row[2]
        sum_rating += row[2]
    ru_avg = float(sum_rating) / len(user_movies)

    cur.execute("SELECT DISTINCT userId FROM Rating WHERE NOT userId = ?;", (user_id,))
    user_ids = cur.fetchall()
    for uid in user_ids:
        CR_u_n = []
        cur.execute("SELECT * FROM Rating WHERE userId = ?;", (str(uid[0]),))
        rows = cur.fetchall()
        sum_rating = 0
        for row in rows:
            sum_rating += row[2]
            if row[1] in user_movies:
                CR_u_n.append((str(row[1]), row[2]))
        rn_avg = float(sum_rating) / len(rows)

        # user_sim(CR_u_n, )

    conn.close()
    return jsonify(CR_u_n)


if __name__ == '__main__':
    create_table()
    create_table_rating()
    print("done enter values to dbs")
    app.run(debug=True)
