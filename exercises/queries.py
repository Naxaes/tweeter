import sys
from collections import namedtuple
from datetime import datetime

from psycopg2 import connect, Error
from psycopg2.extras import NamedTupleCursor
from passlib.hash import sha256_crypt


Tweet = namedtuple('Tweet', 'poster, content, posted')
User  = namedtuple('User',  'username, email, age')

connection = connect(dbname='tweeter', user='postgres', password='', host='localhost', port=5432)
cursor = connection.cursor(cursor_factory=NamedTupleCursor)


def get_newest_tweets(x):
    """
    Fetch x amount of the newest tweets.

    The values in each tuple should be put in a Tweet object (listed above), which has the attributes poster,
    content and posted, where poster should be the username (instead of the id).

    Return all tweets in a list.

    Example:

        list_of_tweets = []
        for result in result_from_query:
            tweet = Tweet(result.username, result.content, result.posted)
            list_of_tweets.append(tweet)

        return list_of_tweets
    """
    query = """
        SELECT username, content, posted 
        FROM   Users JOIN Tweets ON userID = poster;
        """
    cursor.execute(query)
    result = []
    for tuple in cursor.fetchall():
        tweet = Tweet(tuple.username, tuple.content, tuple.posted)
        result.append(tweet)
    return result


def search_for_tweets(x):
    """
    Search for all tweets that contains x in the content or poster.

    The values in each tuple should be put in a Tweet object (listed above), which has the attributes poster,
    content and posted, where poster should be the username (instead of the id).

    Return all tweets in a list.

    Example:

        list_of_tweets = []
        for result in result_from_query:
            tweet = Tweet(result.username, result.content, result.posted)
            list_of_tweets.append(tweet)

        return list_of_tweets
    """
    return []


def get_user(email):
    """
    Return the user with the corresponding email.

    The values in the tuple should be put in a User object (listed above), which has the attributes username,
    email and age.

    Return just the user object.

    Example:

        result = result_from_query
        user = User(result.username, result.email, result.age)
        return user
    """
    return User('', '', 0)


def create_user(username, password, email, age):
    """
    Add a new user to the database.

    Insert the username, email and age in the Users table, and insert the password in the Passwords table. Remember
    that the primary key in the Passwords table is the UserID (not username) which gets auto-generated when the user
    is inserted in the Users table.

    Return nothing.
    """
    return None


def validate_login(email, password):
    """
    Make sure that the email and password match for an user.

    Return -1 if the email is wrong.
    Return 0  if the password is wrong.
    Return 1  if they both are correct.
    """
    return -1


def post_tweet(userID, content):
    """
    Save the a tweet in the database.

    The Tweets table stores the poster, content and posted. Poster should be the userID for the user with the
    corresponding email, and posted should be the current time.

    To get the current time (and properly formatted) you can use the function:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    Return nothing.
    """
    return None


def get_user_tweets(userID):
    return []


def validate_and_perform_user_changes(userID, confirmation, username=None, email=None, age=None, password=None):
    return False


def get_user_name(userID):
    return ''
