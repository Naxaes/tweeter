import sys
from collections import namedtuple
from datetime import datetime

from psycopg2 import connect, Error
from psycopg2.extras import NamedTupleCursor
from passlib.hash import sha256_crypt


class Database:

    def __init__(self, dbname, user, password='', host='localhost', port=5432):

        self.arguments = {
            'dbname':   dbname,
            'user':     user,
            'password': password,
            'host':     host,
            'port':     port
        }

        try:
            self.connection = connect(**self.arguments)
        except Error as error:
            print(error, "\nDid you remember to start your server?\n", file=sys.stderr)
            exit(-1)

        self.cursor = self.connection.cursor(cursor_factory=NamedTupleCursor)

    def execute(self, query, **arguments):
        """
        This function will try to execute the query and commit. If the query fails, it'll rollback.

        Parameters:
            query:       The SQL query to execute.
            **arguments: The named arguments to inject in the query. (Optional)
        """
        try:
            self.cursor.execute(query, arguments)
        except Error as error:
            print(error.pgerror, file=sys.stderr)
            self.connection.rollback()
            return False
        else:
            # This will be executed if the exception isn't raised.
            self.connection.commit()
            return True

    def get_result_from_last_query(self, number_of_tuples = -1):
        """
        Returns the tuples produced from last query.

        Parameters:
            number_of_tuples: The amount of tuples to return.
                    If the number is negative, a list of all tuples will be returned.
                    If the number is 1, only one tuple will be returned (it'll not be in a list).
                    If the number is greater than 1, return a list of at most that amount of tuples.
        Returns:
            List of tuples.
        """
        try:
            if number_of_tuples < 0:
                return self.cursor.fetchall()
            elif number_of_tuples == 1:
                return self.cursor.fetchone()
            else:
                return self.cursor.fetchmany(number_of_tuples)
        except Error as error:
            print(error.pgerror, "\nThere were no results to fetch.", file=sys.stderr)
            return ()


database = Database(dbname='tweeter', user='postgres')



def get_newest_tweets(number):
    """
    Fetch x amount of tweets ordered by time_posted (descending order).

    The values in each tuple should be:
        tweetID, posterID, username, content, time_posted

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
    query = """
        START TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE;

        SELECT tweetID, posterID, username, content, time_posted
        FROM   Users JOIN Tweets ON userID = posterID
        ORDER BY time_posted DESC
        LIMIT %(number)s;
    """
    database.execute(query, number=number)
    result = []
    for tweet in database.get_result_from_last_query(number):
        result.append(tweet)

    return result


def search_for_tweets(search):
    """
    Fetch all tweets that has the search string in the content or in the username.

    The values in each tuple should be:
        tweetID, posterID, username, content, time_posted

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
    query = """
        START TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE;

        SELECT tweetID, posterID, username, content, time_posted
        FROM Users JOIN Tweets ON userID = posterID
        WHERE username LIKE %(search)s OR content LIKE %(search)s;
    """
    database.execute(query, search='%{}%'.format(search))
    result = []
    for tweet in database.get_result_from_last_query():
        result.append(tweet)
    return result


def get_followers_tweets(userID):
    """
    Fetch all tweets that are posted by the user's followers.

    The values in each tuple should be:
        tweetID, posterID, username, content, time_posted

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
    query = """
        START TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE;
        
        WITH UserFollowers AS (
            SELECT followerID 
            FROM Users JOIN Followers ON Users.userID = Followers.userID
            WHERE Users.userID = %(userID)s
        )
        
        SELECT tweetID, posterID, username, content, time_posted
        FROM UserFollowers JOIN Tweets ON followerID = posterID JOIN Users ON posterID = userID
        ORDER BY time_posted DESC;
    """
    database.execute(query, userID=userID)
    result = []
    for tweet in database.get_result_from_last_query():
        result.append(tweet)
    return result


def get_user(email):
    """
    Fetch the user with the email.

    The values in each tuple should be:
        userID, username, email, age

    Return:
         one tuple.

    Example:

        tuple = get_tuple_from_query():
        return tuple

    Hardness:
        1
    """
    query = """
        START TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE;
    
        SELECT userID, username, email, age
        FROM Users 
        WHERE email = %(email)s;
    """
    database.execute(query, email=email)
    result = database.get_result_from_last_query(1)
    return result


def create_user(username, password, email, age):
    """
    Add a new user to the database.

    Insert the username, email and age in the Users table, and insert the password in the Passwords table.

    Notice:
        1. The userID is auto-generated.
        2. The password should be hashed and salted.

    Return:
         True if user was added, False otherwise.

    Hardness:
        5
    """
    hashed_password = sha256_crypt.encrypt(password)

    query = """
        START TRANSACTION READ WRITE ISOLATION LEVEL SERIALIZABLE;
        
        INSERT INTO Users (username, email, age) VALUES (%(username)s, %(email)s, %(age)s);
        INSERT INTO Passwords (userID, password) VALUES
            ((SELECT userID FROM Users WHERE email = %(email)s), %(password)s);
        COMMIT TRANSACTION;
    """

    success = database.execute(query, username=username, email=email, age=age, password=hashed_password)
    return success


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
    query = """
        START TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE;
    
        SELECT password
        FROM   Passwords
        WHERE  userID = (SELECT userID FROM Users WHERE email = %(email)s);
    """

    database.execute(query, email=email)
    result = database.get_result_from_last_query(number_of_tuples=1)

    if result:
        if sha256_crypt.verify(password, result.password):
            return 1
        else:
            return 0
    else:
        return -1


def post_tweet(userID, content):
    """
    Save the a tweet in the database.


    Notice:
        1. userID should be saved as posterID.
        2. To get the current time (and properly formatted) you can use the function:
              current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    Return:
         True if tweet was posted, False otherwise.

    Hardness:
        2
    """
    query = """
        START TRANSACTION READ WRITE ISOLATION LEVEL SERIALIZABLE;
    
        INSERT INTO Tweets (posterID, content, time_posted) 
        VALUES (%(userID)s, %(content)s, %(time_posted)s);
    """
    success = database.execute(query, userID=userID, content=content, time_posted=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return success


def get_user_tweets(userID):  # TODO(ted): Not used!
    query = """
        START TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE;

        SELECT tweetID, posterID, username, content, time_posted
        FROM   Users JOIN Tweets ON userID = posterID
        WHERE  userID = %(userID)s;
    """
    database.execute(query, userID=userID)
    result = []
    for tweet in database.get_result_from_last_query():
        result.append(tweet)
    return result


def validate_and_perform_user_changes(userID, password_confirmation, username=None, email=None, age=None, password=None):
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
    query = """
        SELECT password
        FROM   Passwords
        WHERE  userID = %(userID)s;
    """
    database.execute(query, userID=userID)
    result = database.get_result_from_last_query(1)

    if not sha256_crypt.verify(password_confirmation, result.password):
        return False

    if username:
        query = """
                UPDATE Users 
                SET    username = %(username)s 
                WHERE  userID = %(userID)s;
            """
        database.execute(query, username=username, userID=userID)

    if age:
        query = """
                UPDATE Users 
                SET    age = %(age)s 
                WHERE  userID = %(userID)s;
            """
        database.execute(query, age=age, userID=userID)

    if password:
        query = """
                UPDATE Passwords 
                SET    password = %(password)s 
                WHERE  userID = %(userID)s;
            """
        hashed_password = sha256_crypt.encrypt(password)
        database.execute(query, password=hashed_password, userID=userID)

    if email:
        query = """
                UPDATE Users 
                SET    email  = %(email)s 
                WHERE  userID = %(userID)s;
            """
        database.execute(query, email=email, userID=userID)

    return True


def get_user_by_ID(userID):
    """
    Fetch the user with the userID.

    The values in each tuple should be:
        userID, username, email, age

    Return:
         one tuple.

    Example:

        tuple = get_tuple_from_query():
        return tuple

    Hardness:
        1
    """
    query = """
        SELECT userID, username, email, age
        FROM   Users
        WHERE  userID = %(userID)s;
    """
    database.execute(query, userID=userID)
    result = database.get_result_from_last_query(1)
    return result


def get_user_followers(userID):
    """
    Fetch the followers of the user with the userID.

    The values in each tuple should be:
        followerID

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
    query = """
        SELECT followerID
        FROM   Followers
        WHERE  userID = %(userID)s;
    """
    database.execute(query, userID=userID)
    result = []
    for follower in database.get_result_from_last_query():
        result.append(follower.followerid)
    return result


def add_follower(userID, followerID):
    """
    Add

    Return:
         True if follower was added, False otherwise.

    Hardness:
        1
    """
    query = """
        START TRANSACTION READ WRITE ISOLATION LEVEL SERIALIZABLE;

        INSERT INTO Followers (userID, followerID) 
        VALUES (%(userID)s, %(followerID)s);
    """
    success = database.execute(query, userID=userID, followerID=followerID)
    return success

def remove_follower(userID, followerID):
    """
    Add

    Return:
         True if follower was removed, False otherwise

    Hardness:
        1
    """
    query = """
        START TRANSACTION READ WRITE ISOLATION LEVEL SERIALIZABLE;

        DELETE FROM Followers 
        WHERE userID = %(userID)s AND followerID = %(followerID)s;
    """
    success = database.execute(query, userID=userID, followerID=followerID)
    return success


def remove_tweet(tweetID):
    """
    Add

    Return:
         Nothing

    Hardness:
        1
    """
    query = """
        START TRANSACTION READ WRITE ISOLATION LEVEL SERIALIZABLE;

        DELETE FROM Tweets 
        WHERE tweetID = %(tweetID)s;
    """
    success = database.execute(query, tweetID=tweetID)
    return success