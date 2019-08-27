import sys
from datetime import datetime
# from getpass import getpass  # This should be used when prompting for passwords, but it doesn't work in an IDE.

from psycopg2 import connect, Error
from psycopg2.extras import NamedTupleCursor
from passlib.hash import sha256_crypt


ERROR_TEMPLATE = """
Couldn't connect to server. Potential problems might be:
    * You haven't started the server. This is done by running psql and connecting to the correct database.
    * You've passed incorrect arguments. Make sure the following arguments are correct:
        Server      : {server}
        Database    : {database}
        Port        : {port}
        Username    : {user}
    * Another error occurred. Here's what psycopg2 suggestions:
        {error}
"""


class Database:

    DEFAULT_DATABASE = 'tweeter'
    DEFAULT_USER     = 'postgres'
    DEFAULT_PORT     = 5432
    DEFAULT_HOST     = 'localhost'  # localhost is 127.0.0.1

    def __init__(self, dbname=DEFAULT_DATABASE, user=DEFAULT_USER, password='', host=DEFAULT_HOST, port=DEFAULT_PORT):

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
            print(
                ERROR_TEMPLATE.format(
                    server=host, database=dbname, port=port, user=user, error=str(error).replace('\n', '\n\t\t')
                ), file=sys.stderr
            )
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


database = Database(password=input('Password: '), port=int(input('Port: ')))


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
    query = """
        SELECT tweet_id, poster_id, username, content, time_posted
        FROM   users JOIN tweets ON user_id = poster_id
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
    query = """
        SELECT tweet_id, poster_id, username, content, time_posted
        FROM   users JOIN tweets ON user_id = poster_id
        WHERE  username LIKE %(search)s OR content LIKE %(search)s
        ORDER BY time_posted DESC;
    """
    database.execute(query, search='%{}%'.format(search))
    result = []
    for tweet in database.get_result_from_last_query():
        result.append(tweet)
    return result


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
    query = """        
        WITH user_followers AS (
            SELECT follower_id 
            FROM users JOIN followers ON users.user_id = followers.user_id
            WHERE users.user_id = %(user_id)s
        )
        
        SELECT tweet_id, poster_id, username, content, time_posted
        FROM user_followers JOIN tweets ON follower_id = poster_id JOIN users ON poster_id = user_id
        ORDER BY time_posted DESC;
    """
    database.execute(query, user_id=user_id)
    result = []
    for tweet in database.get_result_from_last_query():
        result.append(tweet)
    return result


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
    query = """    
        SELECT user_id, username, email, age
        FROM users 
        WHERE email = %(email)s;
    """
    database.execute(query, email=email)
    result = database.get_result_from_last_query(1)
    return result


def create_user(username, password, email, age):
    """
    Add a new user to the database.

    Insert the username, email and age in the users table, and insert the password in the passwords table.

    Notice:
        1. The user_id is auto-generated.
        2. The password should be hashed and salted.

    Return:
         True if user was added, False otherwise.

    Hardness:
        5
    """
    hashed_password = sha256_crypt.encrypt(password)

    query = """
        START TRANSACTION READ WRITE ISOLATION LEVEL SERIALIZABLE;
        
        INSERT INTO users (username, email, age) VALUES (%(username)s, %(email)s, %(age)s);
        INSERT INTO passwords (user_id, password) VALUES (
            (SELECT user_id FROM users WHERE email = %(email)s), %(password)s
        );
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
        SELECT password
        FROM   passwords
        WHERE  user_id = (SELECT user_id FROM users WHERE email = %(email)s);
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
    query = """    
        INSERT INTO tweets (poster_id, content, time_posted) 
        VALUES (%(user_id)s, %(content)s, %(time_posted)s);
    """
    success = database.execute(query, user_id=user_id, content=content, time_posted=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    return success


def get_user_tweets(user_id):  # TODO(ted): This is not used, but we'll leave it here for now.
    query = """
        SELECT tweet_id, poster_id, username, content, time_posted
        FROM   users JOIN tweets ON user_id = poster_id
        WHERE  user_id = %(user_id)s;
    """
    database.execute(query, user_id=user_id)
    result = []
    for tweet in database.get_result_from_last_query():
        result.append(tweet)
    return result


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
        5
    """

    # First query the password.
    query = """
        SELECT password
        FROM   passwords
        WHERE  user_id = %(user_id)s;
    """
    database.execute(query, user_id=user_id)
    result = database.get_result_from_last_query(1)

    if not result:
        return False
    elif not sha256_crypt.verify(password_confirmation, result.password):
        return False

    # This have to be a transaction. Otherwise we might only change parts of the user's info. Since we're executing
    # multiple queries within the transaction, we cannot use the database's helper function 'execute', since it commits
    # each query. We'll have to use the cursor manually and only commit at the end of the function.
    start_transaction = "START TRANSACTION READ WRITE ISOLATION LEVEL SERIALIZABLE;"
    database.cursor.execute(start_transaction)

    if username:
        query = """
                UPDATE users 
                SET    username = %(username)s 
                WHERE  user_id = %(user_id)s;
        """
        try:
            database.cursor.execute(query, {'username':username, 'user_id':user_id})
        except Error as error:
            print(error.pgerror, file=sys.stderr)
            database.connection.rollback()
            return False

    if age:
        query = """
                UPDATE users 
                SET    age = %(age)s 
                WHERE  user_id = %(user_id)s;
        """
        try:
            database.cursor.execute(query, {'age':age, 'user_id':user_id})
        except Error as error:
            print(error.pgerror, file=sys.stderr)
            database.connection.rollback()
            return False

    if password:
        query = """
                UPDATE passwords 
                SET    password = %(password)s 
                WHERE  user_id = %(user_id)s;
        """
        hashed_password = sha256_crypt.encrypt(password)
        try:
            database.cursor.execute(query, {'password':hashed_password, 'user_id':user_id})
        except Error as error:
            print(error.pgerror, file=sys.stderr)
            database.connection.rollback()
            return False

    if email:
        query = """
                UPDATE users 
                SET    email  = %(email)s 
                WHERE  user_id = %(user_id)s;
        """
        try:
            database.cursor.execute(query, {'email':email, 'user_id':user_id})
        except Error as error:
            print(error.pgerror, file=sys.stderr)
            database.connection.rollback()
            return False

    # Don't forget to commit the transaction!
    database.connection.commit()
    return True


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
    query = """
        SELECT user_id, username, email, age
        FROM   users
        WHERE  user_id = %(user_id)s;
    """
    database.execute(query, user_id=user_id)
    result = database.get_result_from_last_query(1)
    return result


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
    query = """
        SELECT follower_id
        FROM   followers
        WHERE  user_id = %(user_id)s;
    """
    database.execute(query, user_id=user_id)
    result = []
    for follower in database.get_result_from_last_query():
        result.append(follower.follower_id)
    return result


def add_follower(user_id, follower_id):
    """
    Add

    Return:
         True if follower was added, False otherwise.

    Hardness:
        1
    """
    query = """
        INSERT INTO followers (user_id, follower_id) 
        VALUES (%(user_id)s, %(follower_id)s);
    """
    success = database.execute(query, user_id=user_id, follower_id=follower_id)
    return success


def remove_follower(user_id, follower_id):
    """
    Add

    Return:
         True if follower was removed, False otherwise

    Hardness:
        1
    """
    query = """
        DELETE FROM followers 
        WHERE user_id = %(user_id)s AND follower_id = %(follower_id)s;
    """
    success = database.execute(query, user_id=user_id, follower_id=follower_id)
    return success


def remove_tweet(tweet_id):
    """
    Add

    Return:
         True if tweet was removed, False otherwise.

    Hardness:
        1
    """
    query = """
        DELETE FROM tweets 
        WHERE tweet_id = %(tweet_id)s;
    """
    success = database.execute(query, tweet_id=tweet_id)
    return success
