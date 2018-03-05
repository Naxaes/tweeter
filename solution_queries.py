import sys
from collections import namedtuple
from datetime import datetime

from psycopg2 import connect, Error
from psycopg2.extras import NamedTupleCursor
from passlib.hash import sha256_crypt


Tweet = namedtuple('Tweet', 'tweetID, username, content, time_posted')
User  = namedtuple('User',  'userID, username, email, age')


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
        else:
            # This will be executed if the exception isn't raised.
            self.connection.commit()

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
    Fetch x amount of the newest tweets.

    The values in each tuple should be put in a Tweet object (listed above), which has the attributes posterID,
    content and time_posted, where posterID should be the username (instead of the id).

    Return all tweets in a list.

    Example:

        list_of_tweets = []
        for result in result_from_query:
            tweet = Tweet(result.username, result.content, result.time_posted)
            list_of_tweets.append(tweet)

        return list_of_tweets
    """

    query = """
        START TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE;
            
        SELECT tweetID, username, content, time_posted
        FROM   Users JOIN Tweets ON userID = posterID
        ORDER BY time_posted DESC
        LIMIT %(number)s;
    """
    database.execute(query, number=number)
    result = []
    for tweet in database.get_result_from_last_query(number):
        result.append(
            Tweet(tweet.tweetID, tweet.username, tweet.content, tweet.time_posted)
        )

    return result


def search_for_tweets(search):
    """
        Search for all tweets that contains x in the content or posterID.

        The values in each tuple should be put in a Tweet object (listed above), which has the attributes posterID,
        content and time_posted, where posterID should be the username (instead of the id).

        Return all tweets in a list.

        Example:

            list_of_tweets = []
            for result in result_from_query:
                tweet = Tweet(result.username, result.content, result.time_posted)
                list_of_tweets.append(tweet)

            return list_of_tweets
        """

    query = """
        START TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE;

        SELECT tweetID, username, content, time_posted
        FROM Users JOIN Tweets ON userID = posterID
        WHERE username LIKE %(search)s OR content LIKE %(search)s;
    """
    database.execute(query, search='%{}%'.format(search))
    result = []
    for tweet in database.get_result_from_last_query():
        result.append(
            Tweet(tweet.tweetID, tweet.username, tweet.content, tweet.time_posted)
        )
    return result


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

    query = """
        START TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE;
    
        SELECT userID FROM Users WHERE email = %(email)s;
    """
    database.execute(query, email=email)
    result = database.get_result_from_last_query(1)
    return result.userid  # TODO(ted): This should return the user object!


def create_user(username, password, email, age):
    """
    Add a new user to the database.

    Insert the username, email and age in the Users table, and insert the password in the Passwords table. Remember
    that the primary key in the Passwords table is the UserID (not username) which gets auto-generated when the user
    is inserted in the Users table.

    Return nothing.
    """

    hashed_password = sha256_crypt.encrypt(password)  # removed str(password). TODO(ted): MAKE SUTE IT STILL WORKS

    query = """
        START TRANSACTION READ WRITE ISOLATION LEVEL SERIALIZABLE;
        
        INSERT INTO Users (username, email, age) VALUES (%(username)s, %(email)s, %(age)s);
        INSERT INTO Passwords (userID, password) VALUES
            ((SELECT userID FROM Users WHERE email = %(email)s), %(password)s);
        COMMIT TRANSACTION;
    """

    database.execute(
        query, username=username, email=email, age=age, password=hashed_password
    )

def validate_login(email, password):
    """
    Make sure that the email and password match for an user.

    Return -1 if the email is wrong.
    Return 0  if the password is wrong.
    Return 1  if they both are correct.
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

    The Tweets table stores the posterID, content and time_posted. Poster should be the userID for the user with the
    corresponding email, and time_posted should be the current time.

    To get the current time (and properly formatted) you can use the function:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


    Return nothing.
    """
    query = """
        START TRANSACTION READ WRITE ISOLATION LEVEL SERIALIZABLE;
    
        INSERT INTO Tweets (posterID, content, time_posted) 
        VALUES (%(userID)s, %(content)s, %(time_posted)s);
    """
    database.execute(query, userID=userID, content=content, time_posted=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


def get_user_tweets(userID):
    query = """
        START TRANSACTION READ ONLY ISOLATION LEVEL SERIALIZABLE;

        SELECT tweetID, username, content, time_posted
        FROM   Users JOIN Tweets ON userID = posterID
        WHERE  userID = %(userID)s;
    """
    database.execute(query, userID=userID)
    result = []
    for tweet in database.get_result_from_last_query():
        result.append(
            Tweet(tweet.tweetID, tweet.username, tweet.content, tweet.time_posted)
        )
    return result


def validate_and_perform_user_changes(userID, confirmation, username=None, email=None, age=None, password=None):
    query = """
        SELECT password
        FROM   Passwords
        WHERE  userID = %(userID)s;
    """
    database.execute(query, userID=userID)
    result = database.get_result_from_last_query(1)

    if not sha256_crypt.verify(confirmation, result.password):
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
                SET    age = (age)%s 
                WHERE  userID = %(userID)s;
            """
        database.execute(query, age=age, userID=userID)

    if password:
        query = """
                UPDATE Passwords 
                SET    password = (password)%s 
                WHERE  userID = %(userID)s;
            """
        database.execute(query, password=password, userID=userID)

    if email:
        query = """
                UPDATE Users 
                SET    email  = (email)%s 
                WHERE  userID = %(userID)s;
            """
        database.execute(query, email=email, userID=userID)

    return True


def get_user_name(userID):
    query = """
        SELECT username
        FROM   Users
        WHERE  userID = %(userID)s;
    """
    database.execute(query, userID=userID)
    result = database.get_result_from_last_query(1)
    return result.username


def get_user_followers(userID):
    query = """
        SELECT followerID
        FROM   Followers
        WHERE  userID = %(userID)s;
    """
    database.execute(query, userID=userID)
    result = []
    for follower in database.get_result_from_last_query():
        result.append(follower.followerID)
    return result