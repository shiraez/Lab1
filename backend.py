import sqlite3
from flask import Flask
from flask import jsonify
from flask import request
import csv


# app = Flask(__name__)


def create_table():

    # try:
        with connect() as conn:
            cur = conn.cursor()
            cur.execute("CREATE TABLE movies (movieId TEXT PRIMARY KEY,title TEXT,genres TEXT)")
            conn.commit()
        insertall()

    # except Exception:
        # print

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
    with open('movies.csv', 'r', encoding="utf8") as csv_file:
        allmovies = csv.reader(csv_file, delimiter=',')
        for row in allmovies:
            insert_to_db(row[0], row[1], row[2])



def view():
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM store;")
        rows = cur.fetchall()
        return rows




create_table()
