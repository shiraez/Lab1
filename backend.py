import sqlite3
import csv


# app = Flask(__name__)
import jsonify as jsonify


def create_table():

    try:
        with connect() as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE movies (movieId TEXT PRIMARY KEY,title TEXT,genres TEXT)")
            conn.commit()
        insertall()

    except Exception:
        print("Exception")

def connect():
    conn = sqlite3.connect('lite.db')
    conn.text_factory = str
    return conn


def insert_to_db(movieId, title, genres):
    with connect() as conn:
        cur = conn.cursor()
        if('|' in genres):
            genres = genres.split("|")[0]
        cur.execute("INSERT INTO movies VALUES (?,?,?);", (movieId, title, genres))
        conn.commit()


def insertall():
    index = 0
    with open('movies.csv', 'r', encoding="utf8") as csv_file:
        allmovies = csv.reader(csv_file, delimiter=',')
        for row in allmovies:
            insert_to_db(row[0], row[1], row[2])
            print(index)
            index = index+1



def view():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM movies;")
        rows = cur.fetchall()
        return jsonify(rows)

def search(movieId, title, genres):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM movies WHERE movieId = ?, title = ?, genres = ?;", movieId, title, genres)
        rows = cur.fetchall()
        return rows

def delete(movieId, title, genres):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM movies WHERE movieId = ?, title = ?, genres = ?;", movieId, title, genres)
        conn.commit()

def update(movieId, title, genres):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("UPDATE movies SET title=?, genres=? WHERE movieId=?;", (title, genres, movieId))
        conn.commit()






# create_table()
