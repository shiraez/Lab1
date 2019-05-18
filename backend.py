import sqlite3
from flask import Flask
from flask import jsonify
from flask import request
import csv
# from scipy.stats.stats import pearsonr
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
        return rows


def search(movieId, title, genres):
    with connect() as conn:
        cur = conn.cursor()
        if movieId is "" and title is "" and genres is "":
            return []
        if movieId is "":
            movieId = movieId + '%'
        if title is "":
            title = title + '%'
        if genres is "":
            genres = genres + '%'
        cur.execute("SELECT * FROM movies WHERE movieId LIKE ? AND title LIKE ? AND genres LIKE ?;", (movieId, title, genres))
        rows = cur.fetchall()
        return rows


def delete(movieId, title, genres):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM movies WHERE movieId = ?;", (movieId, ))
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
def rec():
    # create tables if not exists
    create_table()
    create_table_rating()

    # get request arguments
    user_u_id = request.args.get('userid')
    k = request.args.get('k')

    # input validations
    if user_u_id is None:
        return "user id is invalid"
    if k is None:
        return "k is invalid"
    try:
        int(k)
    except Exception:
        return "k is not a number"

    # ratings of user u
    u_movies_rating_dictionary = get_user_movies_and_ratings(user_u_id)

    # input validations
    if len(u_movies_rating_dictionary.keys()) is 0:
        return "user does not exist or does not rate any movies"

    # all users pearsonr matching socre
    pearsonr_users = get_pearsonr_users(u_movies_rating_dictionary, user_u_id)

    # the k best matches
    user_ids_matching = get_k_matching_users_ids(k, pearsonr_users)

    # the k best movies ids of the matches
    best_movies_ids = get_best_movies_ids(user_ids_matching)

    # convert the movies ids to names
    best_movies_names = movie_ids_to_names(best_movies_ids)

    return jsonify(best_movies_names)


def movie_ids_to_names(best_movies_ids):
    """
    :param best_movies_ids: list of movie ids
    :return: list of the corresponding movie names
    """
    best_movies_names = []
    with connect() as conn:
        cur = conn.cursor()
        for movie in best_movies_ids:
            cur.execute("SELECT title FROM movies WHERE movieId = ?;", (movie,))
            best_movies_names.append(cur.fetchall()[0][0])
        return best_movies_names


def get_best_movies_ids(user_ids_matching):
    """
    :param user_ids_matching: the best user ids matches
    :return: ids of the best movies by order
    """
    best_movies_ids = []
    for user_n_id in user_ids_matching:
        movies = get_all_movies_of_user(user_n_id)
        for movie in movies:
            if str(movie[0]) not in best_movies_ids:
                best_movies_ids.append(str(movie[0]))
                break
    return best_movies_ids


def get_all_movies_of_user(user):
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT movieId FROM Rating WHERE userId = ? order by rating;", (user,))
        return cur.fetchall()


def get_k_matching_users_ids(k, pearsonr_users):
    """
    :param k: number of best matches
    :param pearsonr_users: dictionary from user id to its matching score with user u
    :return: list of the user ids of the best k matches
    """
    user_ids_matching = []
    for i in range(0, int(k)):
        best_match = 0
        matching_user = 'not found yet'
        for user in pearsonr_users.keys():
            if pearsonr_users[user] >= best_match:
                best_match = pearsonr_users[user]
                matching_user = user
        pearsonr_users[matching_user] = 0
        user_ids_matching.append(matching_user)
    return user_ids_matching


def get_pearsonr_users(u_movies_rating_dictionary, user_u_id):
    """
    :param u_movies_rating_dictionary: dictionary between movie to its rating be user :user_u_id
    :param user_u_id: the user that we dont need his id
    :return: dictionary from user id to its matching score with user :user_u_id
    """
    pearsonr_users = {}
    for user_id in get_users_ids(user_u_id):
        user_id = str(user_id[0])
        n_movies_rating_dictionary = get_user_movies_and_ratings(user_id)
        user_n_ratings, user_u_ratings = ratings_of_intersection_movies(n_movies_rating_dictionary,
                                                                        u_movies_rating_dictionary)
        calc_pearsonr(pearsonr_users, user_id, user_n_ratings, user_u_ratings)
    return pearsonr_users


def calc_pearsonr(pearsonr_users, user_id, user_n_ratings, user_u_ratings):
    """
    calc the pearsonr for specific user and add it to dictionary
    :param pearsonr_users: dictionary from user id to its matching score
    :param user_id: the user to calc its pearsonr
    :param user_n_ratings: ratings of user n
    :param user_u_ratings: ratings of user u
    """
    if len(user_n_ratings) is 0:
        pearsonr_users[user_id] = 0
    else:
        pearsonr_users[user_id] = pearsonr(user_n_ratings, user_u_ratings)[1]
        if math.isnan(pearsonr_users[user_id]):
            pearsonr_users[user_id] = 0


def ratings_of_intersection_movies(n_movies_rating_dictionary, u_movies_rating_dictionary):
    """
    :param n_movies_rating_dictionary: ratings of user n
    :param u_movies_rating_dictionary: ratings of user u
    :return: ratings of intersection movies
    """
    user_n_ratings = []
    user_u_ratings = []
    for movie in n_movies_rating_dictionary.keys():
        if movie in u_movies_rating_dictionary.keys():
            user_n_ratings.append(n_movies_rating_dictionary[movie])
            user_u_ratings.append(u_movies_rating_dictionary[movie])
    return user_n_ratings, user_u_ratings


def get_users_ids(user_u_id):
    """
    :param user_u_id: user id
    :return: all user ids exclude :param user_u_id
    """
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT userId FROM Rating WHERE NOT userId = ?;", (user_u_id,))
        return cur.fetchall()


def get_user_movies_and_ratings(user_u_id):
    """
    :param user_u_id: user id
    :return: dictionary from movie id to its rating by :param user_u_id
    """
    user_u_movies_to_ratings = {}
    with connect() as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM Rating WHERE userId = ?;", (user_u_id,))
        rows = cur.fetchall()
        for row in rows:
            movie_id = str(row[1])
            rating = row[2]
            user_u_movies_to_ratings[movie_id] = rating
        return user_u_movies_to_ratings


if __name__ == '__main__':
    create_table()
    create_table_rating()
    print("done enter values to dbs")
    app.run(debug=True)
