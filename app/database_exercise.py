import sys
from collections import namedtuple
from datetime import datetime

from psycopg2 import connect, Error
from psycopg2.extras import NamedTupleCursor
from passlib.hash import sha256_crypt




def get_newest_tweets(number):
    """
    Fetch x amount of tweets ordered by time_posted (descending order).

    The values in each tuple should be:
        tweet_id, poster_id, username, content, time_posted

    Return:
         all tuples in a list.

    Example:

        all_tuples = []
        for tuple in get_tuples_from_query():
            all_tuples.append(tuple)

        return all_tuples

    Hardness:
        2
    """
    return []


def search_for_tweets(search):
    """
    Fetch all tweets that has the search string in the content or in the username. Order by time posted.

    The values in each tuple should be:
        tweet_id, poster_id, username, content, time_posted

    Return:
         all tuples in a list.

    Example:

        all_tuples = []
        for tuple in get_tuples_from_query():
            all_tuples.append(tuple)

        return all_tuples


    Hardness:
        3
    """
    return []


def get_followers_tweets(user_id):
    """
    Fetch all tweets that are posted by the user's followers.

    The values in each tuple should be:
        tweet_id, poster_id, username, content, time_posted

    Where username is the username of the follower, not the user.

    Return:
         all tuples in a list.

    Example:

        all_tuples = []
        for tuple in get_tuples_from_query():
            all_tuples.append(tuple)

        return all_tuples

    Hardness:
        5
    """
    return []


def get_user(email):
    """
    Fetch the user with the email.

    The values in each tuple should be:
        user_id, username, email, age

    Return:
         one tuple.

    Example:

        tuple = get_tuple_from_query():
        return tuple

    Hardness:
        1
    """
    return ()


def create_user(username, password, email, age):
    """
    Add a new user to the database.

    Insert the username, email and age in the Users table, and insert the password in the Passwords table.

    Notice:
        1. The user_id is auto-generated.
        2. The password should be hashed and salted.

    Return:
         True if user was added, False otherwise.

    Hardness:
        5
    """
    return False


def validate_login(email, password):
    """
    Make sure that the email and password match for an user.

    Notice:
        1. The password in the database is hashed and salted, while the password given is not.

    Return:
       -1 if the email is wrong.
        0 if the password is wrong.
        1 if they both are correct.

    Hardness:
        3
    """
    return -1


def save_tweet(user_id, content):
    """
    Save the a tweet in the database.


    Notice:
        1. user_id should be saved as poster_id.
        2. To get the current time (and properly formatted) you can use the function:
              current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    Return:
         True if tweet was posted, False otherwise.

    Hardness:
        2
    """
    return False


def validate_and_perform_user_changes(user_id, password_confirmation, username=None, email=None, age=None, password=None):
    """
    Update the user's attributes.

    Notice:
        1. If the parameter has value None, then it shouldn't be changed.
        2. The password in the database is hashed and salted, while the password_confirmation given is not.
        3. The parameter password is the new password the user wants to change to. It should be hashed and salted.

    Return:
         True if password is correct, False otherwise.

    Hardness:
        3
    """
    return False


def get_user_by_id(user_id):
    """
    Fetch the user with the user_id.

    The values in each tuple should be:
        user_id, username, email, age

    Return:
         one tuple.

    Example:

        tuple = get_tuple_from_query():
        return tuple

    Hardness:
        1
    """
    return ()


def get_user_followers(user_id):
    """
    Fetch the followers of the user with the user_id.

    The values in each tuple should be:
        follower_id

    Return:
         one tuple.

    Example:
        all_tuples = []
        for tuple in get_tuples_from_query():
            all_tuples.append(tuple)
        return all_tuples

    Hardness:
        1
    """
    return []


def add_follower(user_id, follower_id):
    """
    Add

    Return:
         True if the follower could follow the user, False otherwise.

    Hardness:
        1
    """
    return False


def remove_follower(user_id, follower_id):
    """
    Add

    Return:
         True if follower was removed, False otherwise.

    Hardness:
        1
    """
    return False


def remove_tweet(tweet_id):
    """
    Add

    Return:
         True if tweet was removed, False otherwise.

    Hardness:
        1
    """
    return False
